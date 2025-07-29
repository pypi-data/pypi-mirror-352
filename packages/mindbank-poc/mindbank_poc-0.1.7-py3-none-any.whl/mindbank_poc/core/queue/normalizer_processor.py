"""
Обработчик очереди для нормализации агрегатов.
"""
import asyncio
from typing import Any, Dict, Optional

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.normalizer.normalizer import Normalizer
from mindbank_poc.core.knowledge_store.base import KnowledgeStore
from mindbank_poc.core.knowledge_store import get_knowledge_store
from mindbank_poc.api.normalizers.config import load_config

logger = get_logger(__name__)

class NormalizerProcessor:
    """
    Обработчик очереди, который нормализует агрегаты и сохраняет их в хранилище знаний.
    """
    
    def __init__(
        self, 
        config_path: Optional[str] = None, 
        knowledge_store: Optional[KnowledgeStore] = None
    ):
        """
        Инициализация обработчика.
        
        Args:
            config_path: Путь к конфигурационному файлу нормализатора
            knowledge_store: Хранилище знаний для сохранения нормализованных единиц
        """
        self.config_path = config_path
        normalizer_config = load_config(config_path)
        self.normalizer = Normalizer(normalizer_config)
        
        # Инициализируем хранилище знаний, если оно не передано
        self.knowledge_store = knowledge_store or get_knowledge_store()
        
        logger.info(
            f"NormalizerProcessor initialized with providers: "
            f"transcript={normalizer_config.transcript.name} (enabled={normalizer_config.transcript.enabled}), "
            f"caption={normalizer_config.caption.name} (enabled={normalizer_config.caption.enabled}), "
            f"embed={normalizer_config.embed.name} (enabled={normalizer_config.embed.enabled}), "
            f"classifier={normalizer_config.classifier.name} (enabled={normalizer_config.classifier.enabled})"
        )
        
    def load_normalizer(self, config_path: Optional[str] = None):
        normalizer_config = load_config(config_path or self.config_path)
        self.normalizer = Normalizer(normalizer_config)
    
    async def process(self, aggregate: Dict[str, Any]):
        """
        Обрабатывает агрегат и сохраняет нормализованную единицу в хранилище.
        
        Args:
            aggregate: Агрегат для обработки
            
        Returns:
            ID сохраненного нормализованного юнита или None в случае ошибки
        """
        self.load_normalizer()

        group_id = aggregate.get("group_id", "unknown")
        entry_count = len(aggregate.get("entries", []))
        
        logger.info(f"Processing aggregate {group_id} with {entry_count} entries")
        
        try:
            # Нормализуем агрегат
            normalized_unit = await self.normalizer.process(aggregate)
            
            try:
                # Сохраняем нормализованную единицу
                unit_id = await self.knowledge_store.store(normalized_unit)
                
                logger.info(f"Processed and stored aggregate {group_id} as normalized unit {unit_id}")
                
                return unit_id
            except ValueError as e:
                # Ошибка при сохранении из-за дубликата ID
                if "already exists" in str(e):
                    logger.warning(f"Duplicate aggregate_id detected during storage: {e}")
                    
                    # Если идентификатор уже существует, получаем существующую единицу и логируем
                    existing_unit = await self.knowledge_store.get(normalized_unit.aggregate_id)
                    if existing_unit:
                        logger.info(f"Existing unit with same aggregate_id has text length: {len(existing_unit.text_repr)}")
                        logger.info(f"New unit has text length: {len(normalized_unit.text_repr)}")
                        
                    # Но обработку считаем успешной, т.к. дупликаты не должны приводить к сбою всего процесса
                    return normalized_unit.aggregate_id
                else:
                    # Другие ошибки ValueError пробрасываем дальше
                    raise
        except Exception as e:
            logger.error(f"Error processing aggregate {group_id}: {e}")
            # В продакшн-системе здесь следует добавить механизм повторных попыток
            # или передачу в очередь ошибок для дальнейшей обработки
            raise 