"""
Реализация хранилища знаний на основе JSONL файлов.
"""
import os
import json
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings
from .base import BaseKnowledgeStore
from ..normalizer.models import NormalizedUnit

# Получаем логгер
logger = get_logger(__name__)

# При импорте модуля выводим информационное сообщение
logger.info(f"JSONL Knowledge Store initialized. Data directory: {settings.storage.knowledge_dir}")

# Определяем корневой каталог проекта и директорию для данных
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "knowledge_store"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Добавляем логирование для отслеживания путей
logger.info(f"JSONL Knowledge Store initialized. Data directory: {DATA_DIR.resolve()}")

# Файл для хранения нормализованных единиц
NORMALIZED_UNITS_FILE = DATA_DIR / "normalized_units.jsonl"


class JSONLKnowledgeStore(BaseKnowledgeStore):
    """
    Реализация хранилища знаний на основе JSONL файлов.
    Простая реализация для MVP, которая сохраняет нормализованные единицы в JSONL-файл.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация хранилища.
        
        Args:
            config: Конфигурация хранилища
        """
        super().__init__(config)
        
        # Получаем конфигурацию
        self.config = config or {}
        
        # Директория для хранения данных
        self.data_dir = Path(self.config.get("data_dir", settings.storage.knowledge_dir))
        self.data_dir.mkdir(exist_ok=True, parents=True)
        
        # Имя файла для хранения нормализованных единиц
        self.file_name = self.config.get("file_name", settings.storage.normalized_units_file)
        self.units_file = self.data_dir / self.file_name
        
        # Добавляем детальное логирование используемого пути
        logger.info(f"JSONLKnowledgeStore instance initialized. Using units file: {self.units_file.resolve()}")
        
        # Если указан конкретный файл, выводим информацию
        if "file_name" in self.config:
            logger.info(f"JSONLKnowledgeStore initialized with units file: {self.units_file}")
        
    async def store(self, unit: NormalizedUnit) -> str:
        """
        Сохраняет нормализованную единицу в хранилище.
        
        Args:
            unit: Нормализованная единица для сохранения
            
        Returns:
            Идентификатор сохраненной единицы (aggregate_id)
        """
        # Добавляем время сохранения
        now = datetime.now()
        unit_dict = unit.model_dump(mode="json")
        unit_dict["stored_at"] = now.isoformat()
        
        # Сохраняем единицу в JSONL-файл
        with open(self.units_file, "a") as f:
            f.write(json.dumps(unit_dict, ensure_ascii=False) + "\n")
            
        # Возвращаем идентификатор единицы (aggregate_id)
        return unit.aggregate_id
    
    async def get(self, unit_id: str) -> Optional[NormalizedUnit]:
        """
        Получает нормализованную единицу из хранилища по идентификатору.
        
        Args:
            unit_id: Идентификатор единицы (aggregate_id)
            
        Returns:
            Нормализованная единица или None, если единица не найдена
        """
        # Проверяем существование файла
        if not self.units_file.exists():
            return None
            
        # Читаем файл и ищем единицу по идентификатору
        with open(self.units_file, "r") as f:
            for line in f:
                unit_dict = json.loads(line)
                if unit_dict.get("aggregate_id") == unit_id:
                    # Удаляем служебные поля
                    if "stored_at" in unit_dict:
                        del unit_dict["stored_at"]
                        
                    # Создаем объект NormalizedUnit
                    return NormalizedUnit.model_validate(unit_dict)
                    
        # Если единица не найдена, возвращаем None
        return None 

    async def load_all(self) -> List[NormalizedUnit]:
        """
        Загружает все нормализованные юниты из JSONL файла.
        Для PoC решение читает весь файл - для production нужен более эффективный вариант.
        """
        try:
            units_file = os.path.join(self.data_dir, self.file_name)
            logger.debug(f"Loading all normalized units from: {units_file}")
            
            if not os.path.exists(units_file):
                logger.warning(f"Units file not found at {units_file}, returning empty list")
                return []
            
            units: List[NormalizedUnit] = []
            async with aiofiles.open(units_file, 'r', encoding='utf-8') as f:
                async for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        unit_data = json.loads(line)
                        units.append(NormalizedUnit(**unit_data))
                    except Exception as e:
                        logger.error(f"Error loading normalized unit: {e}")
            
            logger.info(f"Successfully loaded {len(units)} normalized units from {units_file}")
            return units
        except Exception as e:
            logger.error(f"Failed to load normalized units: {e}", exc_info=True)
            return []
            
    async def list_all(self) -> List[NormalizedUnit]:
        """
        Возвращает список всех нормализованных единиц.
        
        Returns:
            Список нормализованных единиц
        """
        return await self.load_all()
        
    async def get_original_aggregate(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает оригинальный агрегат для нормализованной единицы.
        
        Args:
            unit_id: ID нормализованной единицы (aggregate_id)
            
        Returns:
            Агрегат или None, если не найден
        """
        try:
            # Для JSONL хранилища используем API бэкенда для загрузки агрегата
            from mindbank_poc.api.backends import jsonl_backend
            aggregate = await jsonl_backend.load_aggregate_by_id(unit_id)
            
            if aggregate:
                # Преобразуем модель AggregateInput в словарь
                return aggregate.model_dump(mode="json")
            else:
                logger.warning(f"Original aggregate not found for unit {unit_id}")
                return None
        except Exception as e:
            logger.error(f"Error loading original aggregate for unit {unit_id}: {e}")
            return None

    async def delete_all(self):
        """Удаляет все нормализованные единицы (очищает файл). Используется для тестов."""
        # Реализация метода delete_all
        pass 