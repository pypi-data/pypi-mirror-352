"""
Менеджер нормализации для API.
"""
import asyncio
from typing import Dict, Any, Optional

from mindbank_poc.common.logging import get_logger
from .queue_service import NormalizerQueueService, get_normalizer_queue_service

logger = get_logger(__name__)

class NormalizationManager:
    """
    Менеджер нормализации для API.
    Управляет очередью и обработкой агрегатов.
    """
    
    def __init__(self, queue_service: NormalizerQueueService):
        """
        Инициализация менеджера нормализации.
        
        Args:
            queue_service: Сервис очереди для нормализации
        """
        self.queue_service = queue_service
        
    async def start(self):
        """Запускает сервис очереди."""
        await self.queue_service.start()
        
    async def stop(self):
        """Останавливает сервис очереди."""
        await self.queue_service.stop()
        
    async def add_aggregate(self, aggregate: Dict[str, Any]):
        """
        Добавляет агрегат в очередь нормализации.
        
        Args:
            aggregate: Агрегат для обработки
        """
        try:
            await self.queue_service.put(aggregate)
            return True
        except Exception as e:
            logger.error(f"Error adding aggregate to normalization queue: {e}")
            return False


# Синглтон менеджера нормализации
_normalization_manager: Optional[NormalizationManager] = None


async def get_normalization_manager() -> NormalizationManager:
    """
    Возвращает инстанс менеджера нормализации.
    
    Returns:
        Менеджер нормализации
    """
    global _normalization_manager
    
    if _normalization_manager is None:
        queue_service = get_normalizer_queue_service()
        _normalization_manager = NormalizationManager(queue_service)
        await _normalization_manager.start()
        logger.info("Normalization manager initialized and started")
        
    return _normalization_manager 