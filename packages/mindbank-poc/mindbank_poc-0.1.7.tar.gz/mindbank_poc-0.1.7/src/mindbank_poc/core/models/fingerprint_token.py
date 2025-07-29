from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import uuid
import secrets


class FingerprintTokenType(str, Enum):
    """Типы fingerprint-токенов для доступа к API."""
    MASTER = "master"        # Полный доступ ко всему API
    STANDARD = "standard"    # Стандартный токен с фильтрами доступа
    TEMPORARY = "temporary"  # Короткоживущий токен
    INTERNAL = "internal"    # Служебный токен для внутренних нужд


class FingerprintToken(BaseModel):
    """
    Модель fingerprint-токена для управления доступом к функциям системы.
    Токены имеют типы, различные ограничения по времени жизни, 
    и могут фильтроваться по архетипам и идентификаторам коннекторов.
    """
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    token_value: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    name: str = Field(description="Название токена")
    description: Optional[str] = Field(default=None, description="Описание токена")
    token_type: FingerprintTokenType = Field(description="Тип токена (master, standard, temporary, internal)")
    is_active: bool = Field(default=True, description="Активен ли токен")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания токена")
    updated_at: datetime = Field(default_factory=datetime.now, description="Дата последнего обновления токена")
    expires_at: Optional[datetime] = Field(default=None, description="Дата истечения срока действия токена")
    created_by: Optional[str] = Field(default=None, description="ID пользователя или системы, создавшей токен")
    
    # Фильтры доступа
    allowed_archetypes: List[str] = Field(
        default_factory=list, 
        description="Список разрешенных архетипов (пустой = без ограничений)"
    )
    allowed_connector_ids: List[str] = Field(
        default_factory=list, 
        description="Список разрешенных ID коннекторов (пустой = без ограничений)"
    )
    allowed_connector_types: List[str] = Field(
        default_factory=list, 
        description="Список разрешенных типов коннекторов (пустой = без ограничений)"
    )
    
    def is_expired(self) -> bool:
        """
        Проверяет, истек ли срок действия токена.
        
        Returns:
            True, если токен истек или неактивен, иначе False.
        """
        if not self.is_active:
            return True
        
        if self.expires_at and self.expires_at < datetime.now():
            return True
        
        return False
    
    def has_access(self, archetype: Optional[str] = None, connector_id: Optional[str] = None, 
                  connector_type: Optional[str] = None) -> bool:
        """
        Проверяет, имеет ли токен доступ согласно фильтрам.
        
        Args:
            archetype: Архетип данных для проверки доступа
            connector_id: ID коннектора для проверки доступа
            connector_type: Тип коннектора для проверки доступа
            
        Returns:
            True, если токен имеет доступ, иначе False.
        """
        # Проверяем, не истек ли срок действия токена
        if self.is_expired():
            return False
        
        # Мастер-токен имеет доступ ко всему
        if self.token_type == FingerprintTokenType.MASTER:
            return True
        
        # Проверяем архетип, если указан
        if archetype and self.allowed_archetypes:
            if archetype not in self.allowed_archetypes:
                return False
        
        # Проверяем ID коннектора, если указан
        if connector_id and self.allowed_connector_ids:
            if connector_id not in self.allowed_connector_ids:
                return False
        
        # Проверяем тип коннектора, если указан
        if connector_type and self.allowed_connector_types:
            if connector_type not in self.allowed_connector_types:
                return False
        
        return True