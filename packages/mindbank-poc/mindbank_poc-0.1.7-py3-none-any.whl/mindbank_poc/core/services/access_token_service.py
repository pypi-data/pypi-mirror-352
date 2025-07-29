"""
Сервис для управления токенами доступа (скоуп-фингерпринтами).
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
import secrets
from pathlib import Path

from mindbank_poc.core.models.access_token import (
    AccessToken, AccessTokenFilter, AccessScope, ScopeType, AccessTokenType
)
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

# Синглтон для сервиса токенов доступа
_access_token_service_instance = None


class AccessTokenService:
    """Сервис для управления токенами доступа."""

    def __init__(self, storage_path: str = None):
        """
        Инициализация сервиса токенов доступа.
        
        Args:
            storage_path: Путь к файлу для хранения токенов доступа.
        """
        self.storage_path = storage_path or os.path.join(settings.storage.data_dir, "access_tokens.json")
        self.tokens: Dict[str, AccessToken] = {}
        self._load_tokens()
        
        # Создаем мастер-токен, если его нет
        self._ensure_master_token()

    def _ensure_master_token(self):
        """
        Убеждаемся, что в системе есть хотя бы один мастер-токен.
        Если нет, создаем его.
        """
        # Проверяем наличие мастер-токена
        master_tokens = [token for token in self.tokens.values() if token.token_type == AccessTokenType.MASTER and token.is_active]
        
        if not master_tokens:
            logger.info("Мастер-токен не найден. Создаем новый.")
            
            # Создаем мастер-токен
            token = self.create_token(
                name="Master Token",
                description="Автоматически созданный мастер-токен для администрирования системы",
                token_type=AccessTokenType.MASTER,
                scopes=[AccessScope(scope_type=ScopeType.ALL)],
                expires_at=None,
                created_by="system"
            )
            
            logger.info(f"Создан мастер-токен: {token.token_id}")
            logger.info(f"Значение мастер-токена: {token.token_value}")
            
            # Сохраняем токены
            self._save_tokens()

    def _load_tokens(self):
        """Загрузка токенов из хранилища."""
        try:
            if not os.path.exists(self.storage_path):
                logger.info(f"Файл токенов доступа не найден: {self.storage_path}. Создаем новый.")
                # Создаем пустой файл с пустым словарем токенов
                os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
                with open(self.storage_path, "w") as f:
                    json.dump({}, f)
                self.tokens = {}
                return
            
            with open(self.storage_path, "r") as f:
                tokens_data = json.load(f)
            
            self.tokens = {}
            for token_id, token_data in tokens_data.items():
                # Преобразуем scopes из словарей в объекты AccessScope
                scopes = []
                for scope_data in token_data.get("scopes", []):
                    scope = AccessScope(
                        scope_type=scope_data["scope_type"],
                        values=scope_data.get("values")
                    )
                    scopes.append(scope)
                
                # Преобразуем даты из строк в объекты datetime
                created_at = datetime.fromisoformat(token_data["created_at"])
                updated_at = datetime.fromisoformat(token_data["updated_at"])
                expires_at = datetime.fromisoformat(token_data["expires_at"]) if token_data.get("expires_at") else None
                
                # Создаем объект AccessToken
                token = AccessToken(
                    token_id=token_id,
                    token_value=token_data["token_value"],
                    name=token_data["name"],
                    description=token_data.get("description"),
                    token_type=token_data["token_type"],
                    scopes=scopes,
                    is_active=token_data["is_active"],
                    created_at=created_at,
                    updated_at=updated_at,
                    expires_at=expires_at,
                    created_by=token_data.get("created_by")
                )
                
                self.tokens[token_id] = token
            
            logger.info(f"Загружено {len(self.tokens)} токенов доступа из хранилища")
        except Exception as e:
            logger.error(f"Ошибка при загрузке токенов доступа: {e}")
            self.tokens = {}

    def _save_tokens(self):
        """Сохранение токенов в хранилище."""
        try:
            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Преобразуем токены в словари для сохранения
            tokens_data = {}
            for token_id, token in self.tokens.items():
                # Преобразуем scopes в словари
                scopes_data = []
                for scope in token.scopes:
                    scope_data = {
                        "scope_type": scope.scope_type,
                        "values": scope.values
                    }
                    scopes_data.append(scope_data)
                
                # Преобразуем даты в строки
                created_at = token.created_at.isoformat()
                updated_at = token.updated_at.isoformat()
                expires_at = token.expires_at.isoformat() if token.expires_at else None
                
                # Создаем словарь с данными токена
                token_data = {
                    "token_value": token.token_value,
                    "name": token.name,
                    "description": token.description,
                    "token_type": token.token_type,
                    "scopes": scopes_data,
                    "is_active": token.is_active,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "expires_at": expires_at,
                    "created_by": token.created_by
                }
                
                tokens_data[token_id] = token_data
            
            # Сохраняем токены в файл
            with open(self.storage_path, "w") as f:
                json.dump(tokens_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Сохранено {len(self.tokens)} токенов доступа в хранилище")
        except Exception as e:
            logger.error(f"Ошибка при сохранении токенов доступа: {e}")

    def create_token(
        self,
        name: str,
        description: Optional[str] = None,
        token_type: AccessTokenType = AccessTokenType.STANDARD,
        scopes: List[AccessScope] = None,
        expires_at: Optional[datetime] = None,
        created_by: Optional[str] = None
    ) -> AccessToken:
        """
        Создание нового токена доступа.
        
        Args:
            name: Название токена.
            description: Описание токена.
            token_type: Тип токена.
            scopes: Список скоупов доступа.
            expires_at: Дата истечения срока действия токена.
            created_by: ID пользователя или системы, создавшей токен.
            
        Returns:
            Созданный токен доступа.
        """
        # Генерируем уникальный ID для токена
        token_id = str(uuid.uuid4())
        
        # Генерируем значение токена
        token_value = secrets.token_urlsafe(32)
        
        # Создаем токен
        token = AccessToken(
            token_id=token_id,
            token_value=token_value,
            name=name,
            description=description,
            token_type=token_type,
            scopes=scopes or [],
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=expires_at,
            created_by=created_by
        )
        
        # Добавляем токен в словарь
        self.tokens[token_id] = token
        
        # Сохраняем токены
        self._save_tokens()
        
        return token

    def get_token_by_id(self, token_id: str) -> Optional[AccessToken]:
        """
        Получение токена по ID.
        
        Args:
            token_id: ID токена.
            
        Returns:
            Токен доступа или None, если токен не найден.
        """
        return self.tokens.get(token_id)

    def get_token_by_value(self, token_value: str) -> Optional[AccessToken]:
        """
        Получение токена по значению.
        
        Args:
            token_value: Значение токена.
            
        Returns:
            Токен доступа или None, если токен не найден.
        """
        for token in self.tokens.values():
            if token.token_value == token_value:
                return token
        
        return None

    def get_all_tokens(self) -> List[AccessToken]:
        """
        Получение всех токенов доступа.
        
        Returns:
            Список всех токенов доступа.
        """
        return list(self.tokens.values())
    
    def get_tokens(self, filter_params: Optional[AccessTokenFilter] = None) -> List[AccessToken]:
        """
        Получение списка токенов с возможностью фильтрации.
        
        Args:
            filter_params: Параметры фильтрации.
            
        Returns:
            Список токенов доступа, соответствующих фильтру.
        """
        if not filter_params:
            return list(self.tokens.values())
        
        filtered_tokens = []
        
        for token in self.tokens.values():
            # Фильтрация по типу токена
            if filter_params.token_type and token.token_type != filter_params.token_type:
                continue
            
            # Фильтрация по активности
            if filter_params.is_active is not None and token.is_active != filter_params.is_active:
                continue
            
            # Фильтрация по типу скоупа и значению
            if filter_params.scope_type and filter_params.scope_value:
                # Проверяем, есть ли у токена скоуп с указанным типом и значением
                has_scope = False
                for scope in token.scopes:
                    if scope.scope_type == filter_params.scope_type and scope.values and filter_params.scope_value in scope.values:
                        has_scope = True
                        break
                
                if not has_scope:
                    continue
            
            filtered_tokens.append(token)
        
        return filtered_tokens

    def revoke_token(self, token_id: str) -> bool:
        """
        Отзыв токена доступа.
        
        Args:
            token_id: ID токена.
            
        Returns:
            True, если токен успешно отозван, иначе False.
        """
        token = self.tokens.get(token_id)
        
        if not token:
            return False
        
        # Отзываем токен
        token.is_active = False
        token.updated_at = datetime.now()
        
        # Сохраняем токены
        self._save_tokens()
        
        return True

    def delete_token(self, token_id: str) -> bool:
        """
        Удаление токена доступа.
        
        Args:
            token_id: ID токена.
            
        Returns:
            True, если токен успешно удален, иначе False.
        """
        if token_id not in self.tokens:
            return False
        
        # Удаляем токен
        del self.tokens[token_id]
        
        # Сохраняем токены
        self._save_tokens()
        
        return True

    def get_available_scopes(self) -> Dict[str, List[str]]:
        """
        Получение доступных скоупов для создания токенов.
        
        Returns:
            Словарь с доступными скоупами, где ключи - типы скоупов, а значения - списки доступных значений.
        """
        # Здесь можно реализовать логику получения доступных скоупов из системы
        # Например, получить список архитипов, типов контента, тегов и т.д.
        
        # Пока возвращаем заглушку с примерами скоупов
        return {
            ScopeType.ARCHETYPE.value: ["document", "note", "meeting_notes", "transcription", "code_snippet"],
            ScopeType.TYPE.value: ["text", "image", "audio", "video", "file", "code", "link"],
            ScopeType.TAG.value: ["important", "work", "personal", "confidential"],
            ScopeType.SOURCE.value: ["telegram", "gmail", "google_meet", "slack", "manual"],
            ScopeType.ALL.value: []
        }


def get_access_token_service() -> AccessTokenService:
    """
    Получение экземпляра сервиса токенов доступа.
    
    Returns:
        Экземпляр сервиса токенов доступа.
    """
    global _access_token_service_instance
    
    if _access_token_service_instance is None:
        _access_token_service_instance = AccessTokenService()
    
    return _access_token_service_instance
