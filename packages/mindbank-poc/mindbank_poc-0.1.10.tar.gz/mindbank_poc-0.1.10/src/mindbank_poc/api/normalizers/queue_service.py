"""
Сервис очереди для нормализации в API.
"""
import asyncio
from typing import Dict, Any, Optional

from fastapi import Depends

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.queue.async_queue import AsyncProcessingQueue
from mindbank_poc.core.queue.normalizer_processor import NormalizerProcessor
from mindbank_poc.core.knowledge_store import get_knowledge_store
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

class NormalizerQueueService:
    """
    Сервис очереди для нормализации агрегатов в API.
    """
    
    def __init__(self):
        """Инициализация сервиса очереди."""
        self.queue = AsyncProcessingQueue(maxsize=settings.api.queue_maxsize)
        
        # Создаем хранилище знаний с фабрикой get_knowledge_store
        # Это автоматически будет использовать ChromaDB вместо JSONL
        knowledge_store = get_knowledge_store()
        
        self.processor = NormalizerProcessor(
            knowledge_store=knowledge_store
        )
        
        # Добавляем обработчик в очередь
        self.queue.add_processor(self.processor.process)
        
        # Флаг запуска очереди
        self._started = False
        
    async def start(self):
        """Запускает очередь, если она еще не запущена."""
        if not self._started:
            await self.queue.start()
            self._started = True
            logger.info("Normalizer queue service started")
        
    async def stop(self):
        """Останавливает очередь."""
        if self._started:
            await self.queue.stop()
            self._started = False
            logger.info("Normalizer queue service stopped")
            
    async def put(self, aggregate: Dict[str, Any]):
        """
        Добавляет агрегат в очередь на обработку.
        
        Args:
            aggregate: Агрегат для обработки
        """
        # Запускаем очередь, если она еще не запущена
        if not self._started:
            await self.start()
            
        # Добавляем агрегат в очередь
        await self.queue.put(aggregate)
        group_id = aggregate.get("group_id", "unknown")
        logger.info(f"Added aggregate {group_id} to normalizer queue (size: {self.queue.qsize()})")


# Синглтон сервиса очереди для нормализации
_normalizer_queue_service: Optional[NormalizerQueueService] = None


def get_normalizer_queue_service() -> NormalizerQueueService:
    """
    Возвращает инстанс сервиса очереди для нормализации.
    
    Returns:
        Сервис очереди для нормализации
    """
    global _normalizer_queue_service
    
    if _normalizer_queue_service is None:
        _normalizer_queue_service = NormalizerQueueService()
        
    return _normalizer_queue_service 