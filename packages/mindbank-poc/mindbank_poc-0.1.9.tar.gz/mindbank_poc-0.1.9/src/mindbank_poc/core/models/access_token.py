"""
Модели для токенов доступа (скоуп-фингерпринтов).
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from pydantic import BaseModel, Field


class ScopeType(str, Enum):
    """Типы скоупов для токенов доступа."""
    ARCHETYPE = "archetype"  # Доступ к определенным архитипам данных
    TYPE = "type"            # Доступ к определенным типам контента
    TAG = "tag"              # Доступ к данным с определенными тегами
    SOURCE = "source"        # Доступ к данным из определенных источников
    ALL = "all"              # Полный доступ ко всем данным


class AccessTokenType(str, Enum):
    """Типы токенов доступа."""
    STANDARD = "standard"    # Стандартный токен с ограниченными правами
    MASTER = "master"        # Мастер-токен с полным доступом
    DELEGATED = "delegated"  # Делегированный мастер-токен с полным доступом к определенным сегментам данных


class AccessScope(BaseModel):
    """Модель для скоупа доступа."""
    scope_type: ScopeType
    values: Optional[List[str]] = None  # Для типа ALL значения не требуются

    def matches(self, scope_type: str, value: str) -> bool:
        """
        Проверяет, соответствует ли данный скоуп указанному типу и значению.
        
        Args:
            scope_type: Тип скоупа для проверки.
            value: Значение для проверки.
            
        Returns:
            True, если скоуп соответствует типу и значению, иначе False.
        """
        if self.scope_type == ScopeType.ALL:
            return True
        
        if self.scope_type.value != scope_type:
            return False
        
        if not self.values:
            return False
        
        return value in self.values


class AccessToken(BaseModel):
    """Модель для токена доступа."""
    token_id: str = Field(description="Уникальный идентификатор токена")
    token_value: str = Field(description="Значение токена для использования при авторизации")
    name: str = Field(description="Название токена")
    description: Optional[str] = Field(default=None, description="Описание токена")
    token_type: AccessTokenType = Field(description="Тип токена")
    scopes: List[AccessScope] = Field(default_factory=list, description="Список скоупов доступа")
    is_active: bool = Field(default=True, description="Активен ли токен")
    created_at: datetime = Field(default_factory=datetime.now, description="Дата создания токена")
    updated_at: datetime = Field(default_factory=datetime.now, description="Дата последнего обновления токена")
    expires_at: Optional[datetime] = Field(default=None, description="Дата истечения срока действия токена")
    created_by: Optional[str] = Field(default=None, description="ID пользователя или системы, создавшей токен")

    def has_access(self, scope_type: str, value: str) -> bool:
        """
        Проверяет, имеет ли токен доступ к указанному скоупу.
        
        Args:
            scope_type: Тип скоупа для проверки.
            value: Значение для проверки.
            
        Returns:
            True, если токен имеет доступ, иначе False.
        """
        # Мастер-токен имеет доступ ко всему
        if self.token_type == AccessTokenType.MASTER:
            return True
        
        # Проверяем, не истек ли срок действия токена
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < datetime.now():
            return False
        
        # Проверяем скоупы
        for scope in self.scopes:
            if scope.matches(scope_type, value):
                return True
        
        return False

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
    
    def has_access_to_data(self, data: Dict[str, Any]) -> bool:
        """
        Проверяет, имеет ли токен доступ к указанным данным.
        
        Args:
            data: Словарь с данными, содержащий поля archetype, type, tags, source.
            
        Returns:
            True, если токен имеет доступ, иначе False.
        """
        # Мастер-токен имеет доступ ко всему
        if self.token_type == AccessTokenType.MASTER:
            return True
        
        # Проверяем, не истек ли срок действия токена
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < datetime.now():
            return False
        
        # Если у токена нет скоупов, то доступ запрещен
        if not self.scopes:
            return False
        
        # Проверяем наличие скоупа ALL
        for scope in self.scopes:
            if scope.scope_type == ScopeType.ALL:
                return True
        
        # Проверяем архитип
        if "archetype" in data and data["archetype"]:
            for scope in self.scopes:
                if scope.scope_type == ScopeType.ARCHETYPE and scope.values and data["archetype"] in scope.values:
                    return True
        
        # Проверяем тип
        if "type" in data and data["type"]:
            for scope in self.scopes:
                if scope.scope_type == ScopeType.TYPE and scope.values and data["type"] in scope.values:
                    return True
        
        # Проверяем теги
        if "tags" in data and data["tags"]:
            for tag in data["tags"]:
                for scope in self.scopes:
                    if scope.scope_type == ScopeType.TAG and scope.values and tag in scope.values:
                        return True
        
        # Проверяем источник
        if "source" in data and data["source"]:
            for scope in self.scopes:
                if scope.scope_type == ScopeType.SOURCE and scope.values and data["source"] in scope.values:
                    return True
        
        return False


class AccessTokenFilter(BaseModel):
    """Модель для фильтрации токенов доступа."""
    token_type: Optional[AccessTokenType] = None
    is_active: Optional[bool] = None
    scope_type: Optional[ScopeType] = None
    scope_value: Optional[str] = None
