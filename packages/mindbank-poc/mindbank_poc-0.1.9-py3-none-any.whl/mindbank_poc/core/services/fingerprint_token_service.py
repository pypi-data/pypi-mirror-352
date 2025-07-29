import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from mindbank_poc.core.models.fingerprint_token import FingerprintToken, FingerprintTokenType
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

# Можно добавить в settings путь, но по умолчанию кладём в data/fingerprint_tokens.json
DEFAULT_STORAGE_PATH = Path("data/fingerprint_tokens.json")

class FingerprintTokenService:
    """
    Сервис для управления fingerprint-токенами.
    Выполняет CRUD-операции, проверки прав доступа и фильтрацию по типам и ограничениям.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """Инициализация сервиса fingerprint-токенов с указанием пути хранения."""
        self.storage_path = Path(storage_path or settings.auth.fingerprint_tokens_path)
        self.tokens: Dict[str, FingerprintToken] = {}
        
        # Загружаем токены из файла
        self._load_tokens()
        
        # Создаем мастер-токен, если токенов нет
        self._ensure_master_token()
    
    def create_token(self, name: str, token_type: FingerprintTokenType, description: Optional[str] = None,
                    allowed_archetypes: Optional[List[str]] = None, allowed_connector_ids: Optional[List[str]] = None, 
                    allowed_connector_types: Optional[List[str]] = None,
                    expires_at: Optional[datetime] = None, created_by: Optional[str] = None) -> FingerprintToken:
        """Создание нового fingerprint-токена."""
        token = FingerprintToken(
            name=name,
            description=description,
            token_type=token_type,
            allowed_archetypes=allowed_archetypes or [],
            allowed_connector_ids=allowed_connector_ids or [],
            allowed_connector_types=allowed_connector_types or [],
            expires_at=expires_at,
            created_by=created_by
        )
        
        self.tokens[token.token_id] = token
        self._save_tokens()
        
        logger.info(f"Создан fingerprint-токен: {token.token_id} ({name})")
        return token
    
    def get_token(self, token_id: str) -> Optional[FingerprintToken]:
        """Получение токена по ID."""
        return self.tokens.get(token_id)
    
    def get_token_by_value(self, token_value: str) -> Optional[FingerprintToken]:
        """Получение токена по значению (key_value)."""
        for token in self.tokens.values():
            if token.token_value == token_value:
                return token
        return None
    
    def list_tokens(self, token_type: Optional[FingerprintTokenType] = None,
                  archetype: Optional[str] = None, connector: Optional[str] = None) -> List[FingerprintToken]:
        """
        Получение списка токенов с фильтрацией.
        
        Args:
            token_type: Фильтр по типу токена
            archetype: Фильтр по архетипу (ищет среди allowed_archetypes)
            connector: Фильтр по ID коннектора (ищет среди allowed_connector_ids)
            
        Returns:
            Список токенов, соответствующих фильтрам
        """
        results = []
        for token in self.tokens.values():
            # Если указан фильтр по типу и токен не соответствует
            if token_type and token.token_type != token_type:
                continue
                
            # Если указан фильтр по архетипу и токен не имеет доступа к нему
            if archetype and token.allowed_archetypes and archetype not in token.allowed_archetypes:
                # Пропускаем этот фильтр для мастер-токена
                if token.token_type != FingerprintTokenType.MASTER:
                    continue
                    
            # Если указан фильтр по коннектору и токен не имеет доступа к нему
            if connector and token.allowed_connector_ids and connector not in token.allowed_connector_ids:
                # Пропускаем этот фильтр для мастер-токена
                if token.token_type != FingerprintTokenType.MASTER:
                    continue
            
            results.append(token)
        
        return results
    
    def revoke_token(self, token_id: str) -> bool:
        """Отзыв токена."""
        if token_id not in self.tokens:
            return False
        
        self.tokens[token_id].is_active = False
        self.tokens[token_id].updated_at = datetime.now()
        self._save_tokens()
        
        logger.info(f"Отозван fingerprint-токен: {token_id}")
        return True
    
    def update_token(self, token_id: str, **kwargs) -> Optional[FingerprintToken]:
        """
        Обновление данных токена.
        
        Args:
            token_id: ID токена для обновления
            **kwargs: Поля для обновления (name, description, allowed_*)
            
        Returns:
            Обновленный токен или None, если токен не найден
        """
        if token_id not in self.tokens:
            return None
        
        token = self.tokens[token_id]
        
        # Обновляем поля
        if 'name' in kwargs:
            token.name = kwargs['name']
        if 'description' in kwargs:
            token.description = kwargs['description']
        if 'token_type' in kwargs:
            token.token_type = kwargs['token_type']
        if 'is_active' in kwargs:
            token.is_active = kwargs['is_active']
        if 'expires_at' in kwargs:
            token.expires_at = kwargs['expires_at']
        if 'allowed_archetypes' in kwargs:
            token.allowed_archetypes = kwargs['allowed_archetypes']
        if 'allowed_connector_ids' in kwargs:
            token.allowed_connector_ids = kwargs['allowed_connector_ids']
        if 'allowed_connector_types' in kwargs:
            token.allowed_connector_types = kwargs['allowed_connector_types']
        
        # Обновляем дату изменения
        token.updated_at = datetime.now()
        
        self._save_tokens()
        return token
    
    def _save_tokens(self):
        """Сохранение токенов в файл."""
        try:
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Преобразуем токены в словарь для сериализации
            data = {}
            for token_id, token in self.tokens.items():
                data[token_id] = token.model_dump()
            
            # Сохраняем в файл
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Не удалось сохранить fingerprint-токены: {e}")
    
    def _load_tokens(self):
        """Загрузка токенов из файла."""
        try:
            if not self.storage_path.exists():
                logger.info(f"Файл хранения fingerprint-токенов {self.storage_path} не существует, начинаем с пустого состояния")
                return
            
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Преобразуем данные в объекты FingerprintToken
            for token_id, token_data in data.items():
                try:
                    # Преобразуем строковые даты в datetime
                    if 'created_at' in token_data:
                        token_data['created_at'] = datetime.fromisoformat(token_data['created_at'])
                    if 'updated_at' in token_data:
                        token_data['updated_at'] = datetime.fromisoformat(token_data['updated_at'])
                    if 'expires_at' in token_data and token_data['expires_at']:
                        token_data['expires_at'] = datetime.fromisoformat(token_data['expires_at'])
                    
                    self.tokens[token_id] = FingerprintToken(**token_data)
                except Exception as e:
                    logger.error(f"Не удалось загрузить fingerprint-токен {token_id}: {e}")
            
            logger.info(f"Загружено {len(self.tokens)} fingerprint-токенов из хранилища")
        except Exception as e:
            logger.error(f"Не удалось загрузить fingerprint-токены: {e}")
    
    def _ensure_master_token(self):
        """Создание мастер-токена, если нет ни одного токена."""
        if not self.tokens:
            logger.info("Мастер-токен не найден. Создаем новый.")
            
            # Создаем мастер-токен с 30-дневным сроком жизни
            expires_at = datetime.now() + timedelta(days=30)
            
            token = self.create_token(
                name="Master Fingerprint Token",
                description="Автоматически созданный мастер-токен для полного доступа к API",
                token_type=FingerprintTokenType.MASTER,
                expires_at=expires_at,
                created_by="system"
            )
            
            logger.info(f"Создан мастер-токен: {token.token_id}")
            logger.info(f"Значение мастер-токена: {token.token_value}")
            
            # Сохраняем токены
            self._save_tokens()

# Синглтон экземпляр
_fingerprint_token_service = None

def get_fingerprint_token_service() -> FingerprintTokenService:
    """Получение синглтон-экземпляра сервиса fingerprint-токенов."""
    global _fingerprint_token_service
    if _fingerprint_token_service is None:
        _fingerprint_token_service = FingerprintTokenService()
    return _fingerprint_token_service 