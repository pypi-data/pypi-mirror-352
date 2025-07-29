from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import uuid
import secrets

class IntegrationKey(BaseModel):
    """Модель ключа интеграции для регистрации коннекторов."""
    key_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key_value: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    name: str
    description: Optional[str] = None
    allow_skip_periodic_handshake: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    type_restrictions: List[str] = Field(default_factory=list)
    
    def is_expired(self) -> bool:
        """
        Проверяет, истек ли срок действия ключа.
        
        Returns:
            True если срок действия истек, False в противном случае
        """
        if not self.expires_at:
            return False
        
        return datetime.now() > self.expires_at
    
    def can_register_connector(self, connector_type: Optional[str] = None) -> bool:
        """
        Проверяет, может ли ключ использоваться для регистрации коннектора.
        
        Args:
            connector_type: Тип коннектора, если указан - проверяется соответствие ограничениям
            
        Returns:
            True если ключ может быть использован, False иначе
        """
        # Проверка на активность и срок действия
        if not self.is_active or self.is_expired():
            return False
        
        # Проверка на ограничение типов, если ограничения заданы
        if connector_type and self.type_restrictions:
            return connector_type in self.type_restrictions
        
        # Если нет ограничений или тип не указан
        return True 