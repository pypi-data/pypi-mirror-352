"""
Модуль настроек приложения на основе pydantic-settings.
"""
from pathlib import Path
from typing import Dict, Any, Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from mindbank_poc.common.logging import get_logger # Импортируем логгер

# Общий конфиг для всех классов настроек
common_config = SettingsConfigDict(
    env_file=".env", 
    env_file_encoding="utf-8",
    extra="ignore"  # Игнорировать лишние переменные окружения
)

# Логгер для этого модуля
settings_logger = get_logger(__name__)


class OpenAISettings(BaseSettings):
    """Настройки для OpenAI провайдеров."""
    api_key: Optional[str] = None
    organization_id: Optional[str] = None
    model_settings: Dict[str, Any] = {}
    
    # Модель для транскрипции
    whisper_model: str = "whisper-1"
    
    # Модель для векторного представления (embedding)
    embedding_model: str = "text-embedding-3-large"
    
    # Модель для генерации описаний
    caption_model: str = "gpt-4o-mini"
    caption_max_tokens: int = 100
    caption_temperature: float = 0.7
    
    # Модель для классификации
    classifier_model: str = "gpt-4o-mini"
    classifier_max_tokens: int = 50
    classifier_temperature: float = 0.2
    
    model_config = SettingsConfigDict(
        env_prefix="OPENAI_", 
        **common_config
    )


class NormalizerSettings(BaseSettings):
    """Настройки для нормализатора."""
    
    # Общие настройки
    offline_mode: bool = Field(default=False) # Явно указываем тип и значение по умолчанию
    
    # Настройки для провайдеров
    transcript_provider: Literal["openai", "fallback"] = "fallback"
    caption_provider: Literal["openai", "fallback"] = "fallback" 
    embed_provider: Literal["openai", "fallback"] = "openai"
    classifier_provider: Literal["openai", "fallback"] = "fallback"
    
    # Флаги включения провайдеров
    enable_transcript: bool = True
    enable_caption: bool = True
    enable_embed: bool = True
    enable_classifier: bool = True
    
    # Настройки для путей к файлам
    config_dir: str = "config/normalizer"
    knowledge_store_dir: str = "data/knowledge_store"
    knowledge_store_file: str = "normalized_units.jsonl"
    config_file: str = "normalizer_config.json"
    config_path: Path = Path(config_dir) / config_file

    model_config = SettingsConfigDict(
        env_prefix="NORMALIZER_", 
        validation_mode="coerce_deep_any",
        arbitrary_types_allowed=True,
        **common_config
    )

    def __init__(self, **values: Any):
        super().__init__(**values)
        settings_logger.info(f"NormalizerSettings initialized: offline_mode={self.offline_mode} (type: {type(self.offline_mode)})")
        settings_logger.debug(f"Original offline_mode input value: {values.get('offline_mode')}")
        settings_logger.debug(f"All NormalizerSettings: {self.model_dump_json(indent=2)}")
        # Явное приведение к bool если значение в строке было "true"/"false"
        if isinstance(self.offline_mode, str):
            self.offline_mode = self.offline_mode.lower() in ("true", "1", "yes", "y", "on")
            settings_logger.info(f"Converted string offline_mode to bool: {self.offline_mode}")


class APISettings(BaseSettings):
    """Настройки для API."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    
    buffer_timeout_seconds: float = 30.0
    buffer_max_entries_per_group: int = 100
    buffer_check_interval_seconds: float = 5.0
    
    queue_maxsize: int = 100
    
    model_config = SettingsConfigDict(
        env_prefix="API_", 
        **common_config
    )
    

class StorageSettings(BaseSettings):
    """Настройки для хранения данных."""
    data_dir: str = "data"
    ingest_dir: str = "data/ingest_jsonl"
    knowledge_dir: str = "data/knowledge_store"
    raw_entries_file: str = "raw_entries.jsonl"
    aggregates_file: str = "aggregates.jsonl"
    normalized_units_file: str = "normalized_units.jsonl"
    # Тип хранилища знаний: "jsonl" или "chroma"
    store_type: str = "jsonl"
    # Файл для хранения данных чатов
    chats_file: str = "chats.json"
    
    model_config = SettingsConfigDict(
        env_prefix="STORAGE_", 
        **common_config
    )


class ConnectorSettings(BaseSettings):
    """Настройки для работы с коннекторами."""
    # Путь к файлу хранения данных коннекторов
    storage_path: str = "data/connectors.json"
    
    # Путь к директории для хранения состояний онбоардинга FSM
    onboarding_states_path: str = "data/onboarding_states"
    
    # Интервал поллинга для handshake (в секундах)
    polling_interval_seconds: int = 15
    
    # Максимальное время тишины перед отключением коннектора (в минутах)
    max_silence_minutes: int = 10
    
    # Интервал проверки таймаутов (в секундах)
    check_interval_seconds: int = 60
    
    # Таймаут HTTP ответа (в секундах)
    http_timeout_seconds: int = 5
    
    # Путь к файлу хранения ключей интеграции
    integration_keys_path: str = "data/integration_keys.json"
    
    # Срок действия ключей интеграции по умолчанию (в днях)
    default_key_expiry_days: int = 30
    
    model_config = SettingsConfigDict(
        env_prefix="CONNECTOR_", 
        **common_config
    )


class AuthSettings(BaseSettings):
    """Настройки аутентификации для административного доступа."""
    # Имя пользователя администратора
    admin_username: str = "admin"
    
    # Хеш пароля администратора (SHA-256)
    # По умолчанию используется хеш от "admin123" - только для разработки!
    admin_password_hash: str = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

    # Новый API-ключ администратора (берётся из .env)
    admin_api_key: str = ""
    
    # Путь к файлу хранения fingerprint токенов
    fingerprint_tokens_path: str = "data/fingerprint_tokens.json"
    
    model_config = SettingsConfigDict(
        env_prefix="AUTH_", 
        **common_config
    )


class Settings(BaseSettings):
    """Общие настройки приложения."""
    app_name: str = "Mindbank"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Вложенные настройки
    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    normalizer: NormalizerSettings = Field(default_factory=NormalizerSettings)
    api: APISettings = Field(default_factory=APISettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    connector: ConnectorSettings = Field(default_factory=ConnectorSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    
    model_config = SettingsConfigDict(
        env_prefix="APP_", 
        **common_config
    )

    def __init__(self, **values: Any):
        super().__init__(**values)
        settings_logger.info("Global Settings initialized.")
        # Дополнительное логирование значения offline_mode при инициализации глобальных настроек
        settings_logger.info(f"Global Settings - Initial normalizer.offline_mode: {self.normalizer.offline_mode} (type: {type(self.normalizer.offline_mode)})")


# Создаем глобальный экземпляр настроек
settings_logger.info("Creating global settings instance...")
settings = Settings()
settings_logger.info(f"Global settings instance created. Final normalizer.offline_mode: {settings.normalizer.offline_mode} (type: {type(settings.normalizer.offline_mode)})")


def get_settings() -> Settings:
    """
    Функция для получения глобального экземпляра настроек.
    
    Returns:
        Settings: Глобальный экземпляр настроек приложения
    """
    return settings 