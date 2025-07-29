"""
Базовые интерфейсы и абстракции для хранилища знаний.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol

from ..normalizer.models import NormalizedUnit


class KnowledgeStore(Protocol):
    """Протокол для хранилища знаний."""
    
    async def store(self, unit: NormalizedUnit) -> str:
        """
        Сохраняет нормализованную единицу в хранилище.
        
        Args:
            unit: Нормализованная единица для сохранения
            
        Returns:
            Идентификатор сохраненной единицы
        """
        ...
        
    async def get(self, unit_id: str) -> Optional[NormalizedUnit]:
        """
        Получает нормализованную единицу из хранилища.
        
        Args:
            unit_id: Идентификатор единицы
            
        Returns:
            Нормализованная единица или None, если единица не найдена
        """
        ...


class BaseKnowledgeStore(ABC):
    """Базовый класс для хранилища знаний."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Инициализация хранилища.
        
        Args:
            config: Конфигурация хранилища
        """
        self.config = config
    
    @abstractmethod
    async def store(self, unit: NormalizedUnit) -> str:
        """
        Сохраняет нормализованную единицу в хранилище.
        
        Args:
            unit: Нормализованная единица для сохранения
            
        Returns:
            Идентификатор сохраненной единицы
        """
        pass
    
    @abstractmethod
    async def get(self, unit_id: str) -> Optional[NormalizedUnit]:
        """
        Получает нормализованную единицу из хранилища.
        
        Args:
            unit_id: Идентификатор единицы
            
        Returns:
            Нормализованная единица или None, если единица не найдена
        """
        pass 