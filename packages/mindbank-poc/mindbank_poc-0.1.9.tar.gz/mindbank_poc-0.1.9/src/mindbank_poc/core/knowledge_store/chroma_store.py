"""
Реализация хранилища знаний на основе ChromaDB.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List, Tuple, Union
import uuid

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings
from .base import BaseKnowledgeStore
from ..normalizer.models import NormalizedUnit

# Получаем логгер
logger = get_logger(__name__)

# Определяем корневой каталог проекта и директорию для данных
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "knowledge_store" / "chroma_db"
DATA_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"ChromaDB Knowledge Store initialized. Data directory: {DATA_DIR.resolve()}")

class ChromaKnowledgeStore(BaseKnowledgeStore):
    """
    Реализация хранилища знаний на основе ChromaDB.
    
    Использует ChromaDB для эффективного векторного поиска и хранения нормализованных юнитов.
    Преимущества по сравнению с JSONL:
    - Оптимизированный векторный поиск
    - Сохранение/загрузка данных без необходимости хранить все в памяти
    - Поддержка метаданных для фильтрации
    - Улучшенная масштабируемость
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация хранилища.
        
        Args:
            config: Конфигурация хранилища, может содержать:
                   - data_dir: путь к директории для хранения данных
                   - collection_name: имя коллекции в ChromaDB
        """
        super().__init__(config or {})
        
        # Директория для хранения данных
        self.data_dir = Path(self.config.get("data_dir", settings.storage.knowledge_dir))
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        # Имя коллекции
        self.collection_name = self.config.get("collection_name", "normalized_units")
        
        # Путь к ChromaDB
        self.chroma_path = self.data_dir / "chroma_db"
        self.chroma_path.mkdir(exist_ok=True, parents=True)
        
        # Логгирование
        logger.info(f"ChromaKnowledgeStore: Using directory {self.chroma_path.resolve()}")
        logger.info(f"ChromaKnowledgeStore: Using collection {self.collection_name}")
        
        # Инициализация клиента ChromaDB (persistent)
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path.resolve()),
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Получение или создание коллекции
        try:
            # Создаем функцию эмбеддингов None, чтобы отключить встроенную функцию эмбеддингов
            # Это важно, так как мы хотим использовать только наши собственные эмбеддинги от OpenAI
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Нормализованные единицы знаний"},
                embedding_function=None  # Отключаем встроенную функцию эмбеддингов
            )
            logger.info(f"ChromaKnowledgeStore: Collection '{self.collection_name}' ready")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collection: {e}", exc_info=True)
            raise
    
    async def store(self, unit: NormalizedUnit) -> str:
        """
        Сохраняет нормализованную единицу в хранилище.
        
        Args:
            unit: Нормализованная единица для сохранения
            
        Returns:
            Идентификатор сохраненной единицы (совпадает с aggregate_id)
        """
        try:
            # Идентификатор для ChromaDB (используем aggregate_id)
            doc_id = unit.aggregate_id
            
            # Текстовое представление для поиска
            document = unit.text_repr
            
            # Векторное представление (если есть)
            embedding = unit.vector_repr
            
            # Метаданные для хранения и фильтрации
            metadata = {
                "aggregate_id": unit.aggregate_id,
                "normalized_at": unit.normalized_at.isoformat(),
                # Копируем классификацию в метаданные для фильтрации
                **{f"class_{k}": str(v) for k, v in unit.classification.items()},
                # Копируем метаданные юнита для фильтрации (только строковые и числовые)
                **{k: str(v) if not isinstance(v, (int, float, bool, str)) else v 
                   for k, v in unit.metadata.items() 
                   if v is not None}
            }
            
            # Сохраняем полный объект как JSON в документе
            full_unit_json = unit.model_dump_json()
            
            # Проверяем, существует ли документ с таким ID
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing and existing['ids']:
                    # Если существует, обновляем
                    logger.info(f"Updating existing unit with ID {doc_id}")
                    self.collection.update(
                        ids=[doc_id],
                        embeddings=[embedding] if embedding else None,
                        metadatas=[metadata],
                        documents=[full_unit_json]
                    )
                else:
                    # Если не существует, добавляем
                    logger.info(f"Adding new unit with ID {doc_id}")
                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding] if embedding else None,
                        metadatas=[metadata],
                        documents=[full_unit_json]
                    )
            except Exception as e:
                # Если произошла ошибка (например, коллекция пуста), добавляем
                logger.warning(f"Error checking existence, adding as new: {e}")
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding] if embedding else None,
                    metadatas=[metadata],
                    documents=[full_unit_json]
                )
            
            logger.info(f"Stored unit with ID {doc_id} in ChromaDB")
            return doc_id
        
        except Exception as e:
            logger.error(f"Error storing unit in ChromaDB: {e}", exc_info=True)
            raise
    
    async def get(self, unit_id: str) -> Optional[NormalizedUnit]:
        """
        Получает нормализованную единицу из хранилища по идентификатору.
        
        Args:
            unit_id: Идентификатор единицы (aggregate_id)
            
        Returns:
            Нормализованная единица или None, если единица не найдена
        """
        try:
            # Запрашиваем документ по ID
            result = self.collection.get(ids=[unit_id], include=["documents"])
            
            # Проверяем, найден ли документ
            if not result or not result['documents'] or not result['documents'][0]:
                logger.warning(f"Unit with ID {unit_id} not found in ChromaDB")
                return None
            
            # Десериализуем JSON в объект NormalizedUnit
            try:
                unit_json = result['documents'][0]
                unit = NormalizedUnit.model_validate_json(unit_json)
                return unit
            except Exception as e:
                logger.error(f"Error deserializing unit from ChromaDB: {e}", exc_info=True)
                return None
        
        except Exception as e:
            logger.error(f"Error retrieving unit from ChromaDB: {e}", exc_info=True)
            return None
    
    async def load_all(self) -> List[NormalizedUnit]:
        """
        Загружает все нормализованные юниты из хранилища.
        
        Returns:
            Список всех нормализованных юнитов
        """
        try:
            # Запрашиваем все документы из коллекции
            result = self.collection.get(include=["documents"])
            
            # Проверяем, есть ли результаты
            if not result or not result['documents']:
                logger.warning("No units found in ChromaDB")
                return []
            
            # Десериализуем каждый JSON в объект NormalizedUnit
            units = []
            for unit_json in result['documents']:
                try:
                    if unit_json:  # Проверяем, что JSON не пустой
                        unit = NormalizedUnit.model_validate_json(unit_json)
                        units.append(unit)
                except Exception as e:
                    logger.error(f"Error deserializing unit from ChromaDB: {e}", exc_info=True)
            
            logger.info(f"Loaded {len(units)} units from ChromaDB")
            return units
        
        except Exception as e:
            logger.error(f"Error loading all units from ChromaDB: {e}", exc_info=True)
            return []
    
    async def delete(self, unit_id: str) -> bool:
        """
        Удаляет нормализованную единицу из хранилища по идентификатору.
        
        Args:
            unit_id: Идентификатор единицы (aggregate_id)
            
        Returns:
            True, если удаление успешно, иначе False
        """
        try:
            # Удаляем документ по ID
            self.collection.delete(ids=[unit_id])
            logger.info(f"Deleted unit with ID {unit_id} from ChromaDB")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting unit from ChromaDB: {e}", exc_info=True)
            return False
    
    async def delete_all(self) -> bool:
        """
        Удаляет все нормализованные единицы из хранилища.
        
        Returns:
            True, если удаление успешно, иначе False
        """
        try:
            # Удаляем всю коллекцию и создаем заново
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Нормализованные единицы знаний"}
            )
            logger.info(f"Deleted all units from ChromaDB collection '{self.collection_name}'")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting all units from ChromaDB: {e}", exc_info=True)
            return False
    
    async def search(
        self, 
        # Убираем query_text, так как поиск будет только по вектору
        # query_text: Optional[str] = None,
        query_vector: Optional[List[float]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Tuple[NormalizedUnit, float]]:
        """
        Выполняет поиск в хранилище по вектору и/или метаданным.
        
        Args:
            query_vector: Вектор запроса для семантического поиска
            metadata_filters: Фильтры по метаданным
            limit: Максимальное количество результатов
            
        Returns:
            Список кортежей (unit, score) с найденными единицами и их релевантностью
        """
        try:
            # Проверяем, есть ли критерий поиска (вектор или фильтры)
            if not query_vector and not metadata_filters:
                logger.warning("Search requires either query_vector or metadata_filters")
                return []
            
            # Подготавливаем фильтры метаданных в формате ChromaDB
            chroma_filter = None
            if metadata_filters:
                # Конвертируем фильтры в формат ChromaDB
                chroma_filter = {"$and": []}
                for key, value in metadata_filters.items():
                    filter_key = f"class_{key}" if key in ["type", "topic", "category"] else key
                    chroma_filter["$and"].append({"$eq": {filter_key: value}})
            
            # Выполняем поиск
            if query_vector:
                # Семантический поиск по вектору
                result = self.collection.query(
                    query_embeddings=[query_vector],
                    where=chroma_filter,
                    n_results=limit,
                    include=["documents", "distances"] # Запрашиваем дистанции
                )
            elif metadata_filters: # Если вектора нет, но есть фильтры
                # Только фильтрация по метаданным
                result = self.collection.get(
                    where=chroma_filter,
                    limit=limit,
                    include=["documents"] # Дистанции не нужны/недоступны
                )
            else: # На случай, если контроль выше пропустит
                return []
            
            # Проверяем, есть ли результаты
            # Для query результат в result["documents"][0], для get в result["documents"]
            documents = result.get('documents')
            if not documents or (isinstance(documents, list) and not documents[0]):
                logger.warning("No results found in ChromaDB query")
                return []
            
            # Обработка результатов
            results_list = []
            docs_to_process = documents[0] if query_vector else documents
            distances_list = result.get('distances')[0] if query_vector and result.get('distances') else None
            
            for i, unit_json in enumerate(docs_to_process):
                try:
                    if unit_json:
                        unit = NormalizedUnit.model_validate_json(unit_json)
                        score = 0.99 # Скор по умолчанию для get()
                        
                        if distances_list:
                            distance = float(distances_list[i])
                            # Преобразуем косинусную дистанцию [0, 2] в скор [0.99, ~0]
                            # similarity = 1.0 - (distance / 2.0) # Сходство [0, 1]
                            # score = 0.99 * (similarity ** 0.8) # Нелинейное масштабирование
                            score = max(0.01, 0.99 * (1.0 - (distance / 2.0))) # Линейное масштабирование
                            score = round(score, 2)
                            
                        results_list.append((unit, score))
                except Exception as e:
                    logger.error(f"Error deserializing search result from ChromaDB: {e}", exc_info=True)
            
            logger.info(f"Found {len(results_list)} results in ChromaDB")
            # Сортируем по скору, если был векторный поиск
            if query_vector:
                results_list.sort(key=lambda item: item[1], reverse=True)
                
            return results_list
        
        except Exception as e:
            logger.error(f"Error searching in ChromaDB: {e}", exc_info=True)
            return [] 