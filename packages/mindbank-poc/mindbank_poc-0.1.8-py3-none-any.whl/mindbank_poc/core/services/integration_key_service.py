import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from mindbank_poc.core.models.integration_key import IntegrationKey
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

class IntegrationKeyService:
    """
    Сервис для управления ключами интеграции.
    Позволяет создавать, проверять и отзывать ключи для регистрации коннекторов.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Инициализирует сервис ключей интеграции.
        
        Args:
            storage_path: Путь к файлу для хранения ключей
        """
        self.storage_path = Path(storage_path or settings.connector.integration_keys_path)
        self.keys: Dict[str, IntegrationKey] = {}
        
        # Создаем директорию, если не существует
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Загружаем данные при инициализации
        self._load_keys()
        
        # Добавляем мастер-ключ, если нет ни одного ключа
        if len(self.keys) == 0:
            self.create_key(
                name="Master Key", 
                description="Автоматически созданный мастер-ключ для первоначальной настройки", 
                allow_skip_periodic_handshake=True,
                expires_at=datetime.now() + timedelta(days=30)
            )
            logger.info("Создан мастер-ключ интеграции, так как не было найдено существующих ключей")
    
    def create_key(self, name: str, description: Optional[str] = None, 
                   allow_skip_periodic_handshake: bool = False,
                   expires_at: Optional[datetime] = None,
                   created_by: Optional[str] = None) -> IntegrationKey:
        """
        Создает новый ключ интеграции.
        
        Args:
            name: Название ключа
            description: Описание ключа
            allow_skip_periodic_handshake: Разрешает ли ключ регистрацию облегченных коннекторов
            expires_at: Дата истечения срока действия
            created_by: Информация о создателе ключа
            
        Returns:
            Созданный ключ интеграции
        """
        key = IntegrationKey(
            name=name,
            description=description,
            allow_skip_periodic_handshake=allow_skip_periodic_handshake,
            expires_at=expires_at,
            created_by=created_by
        )
        
        self.keys[key.key_id] = key
        self._save_keys()
        
        logger.info(f"Создан новый ключ интеграции: {key.key_id} ({name})")
        return key
    
    async def create_key_for_type(self, name: str, description: Optional[str] = None,
                           allow_skip_periodic_handshake: bool = False,
                           type_restrictions: List[str] = None,
                           expires_at: Optional[datetime] = None,
                           created_by: Optional[str] = None) -> IntegrationKey:
        """
        Создает новый ключ интеграции с ограничением по типу коннектора.
        
        Args:
            name: Название ключа
            description: Описание ключа
            allow_skip_periodic_handshake: Разрешает ли ключ регистрацию облегченных коннекторов
            type_restrictions: Типы коннекторов, для которых разрешена регистрация
            expires_at: Дата истечения срока действия
            created_by: Информация о создателе ключа
            
        Returns:
            Созданный ключ интеграции
        """
        # Если срок не указан, ставим по умолчанию 30 дней
        if not expires_at:
            expires_at = datetime.now() + timedelta(days=30)
            
        key = IntegrationKey(
            name=name,
            description=description,
            allow_skip_periodic_handshake=allow_skip_periodic_handshake,
            type_restrictions=type_restrictions or [],
            expires_at=expires_at,
            created_by=created_by
        )
        
        self.keys[key.key_id] = key
        self._save_keys()
        
        logger.info(f"Создан новый ключ интеграции для типов {type_restrictions}: {key.key_id} ({name})")
        return key
    
    def revoke_key(self, key_id: str) -> bool:
        """
        Отзывает ключ интеграции.
        
        Args:
            key_id: ID ключа
            
        Returns:
            True если ключ был отозван, False если ключ не найден
        """
        if key_id not in self.keys:
            return False
        
        self.keys[key_id].is_active = False
        self.keys[key_id].updated_at = datetime.now()
        self._save_keys()
        
        logger.info(f"Отозван ключ интеграции: {key_id}")
        return True
    
    def get_key(self, key_id: str) -> Optional[IntegrationKey]:
        """
        Возвращает ключ по ID.
        
        Args:
            key_id: ID ключа
            
        Returns:
            Ключ интеграции или None, если не найден
        """
        return self.keys.get(key_id)
    
    def get_key_by_value(self, key_value: str) -> Optional[IntegrationKey]:
        """Возвращает ключ по его значению (key_value)."""
        for key in self.keys.values():
            if key.key_value == key_value:
                return key
        return None
    
    def get_keys(self) -> List[IntegrationKey]:
        """
        Возвращает все ключи интеграции.
        
        Returns:
            Список ключей интеграции
        """
        return list(self.keys.values())
    
    def verify_key(self, key_value: str) -> bool:
        """
        Проверяет, действителен ли ключ.
        
        Args:
            key_value: Значение ключа
            
        Returns:
            True если ключ действителен и может использоваться, False в противном случае
        """
        key = self.get_key_by_value(key_value)
        if key:
            return key.can_register_connector()
        
        return False
    
    def _save_keys(self):
        """Сохраняет ключи в файл."""
        try:
            # Преобразуем ключи в JSON
            data = {
                key_id: key.model_dump() 
                for key_id, key in self.keys.items()
            }
            
            # Сохраняем в файл
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Не удалось сохранить ключи интеграции: {e}")
    
    def _load_keys(self):
        """Загружает ключи из файла."""
        try:
            if not self.storage_path.exists():
                logger.info(f"Файл хранения ключей интеграции {self.storage_path} не существует, начинаем с пустого состояния")
                return
            
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Преобразуем данные в объекты IntegrationKey
            for key_id, key_data in data.items():
                try:
                    # Преобразуем строковые даты в datetime
                    if 'created_at' in key_data:
                        key_data['created_at'] = datetime.fromisoformat(key_data['created_at'])
                    if 'updated_at' in key_data:
                        key_data['updated_at'] = datetime.fromisoformat(key_data['updated_at'])
                    if 'expires_at' in key_data and key_data['expires_at']:
                        key_data['expires_at'] = datetime.fromisoformat(key_data['expires_at'])
                    
                    self.keys[key_id] = IntegrationKey(**key_data)
                except Exception as e:
                    logger.error(f"Не удалось загрузить ключ интеграции {key_id}: {e}")
            
            logger.info(f"Загружено {len(self.keys)} ключей интеграции из хранилища")
        except Exception as e:
            logger.error(f"Не удалось загрузить ключи интеграции: {e}")

# Синглтон экземпляр
_integration_key_service = None

def get_integration_key_service() -> IntegrationKeyService:
    """
    Возвращает глобальный экземпляр IntegrationKeyService, создавая его при необходимости.
    
    Returns:
        Глобальный экземпляр IntegrationKeyService
    """
    global _integration_key_service
    
    if _integration_key_service is None:
        _integration_key_service = IntegrationKeyService()
    
    return _integration_key_service 