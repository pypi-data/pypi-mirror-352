from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Set
from pydantic import BaseModel, Field, HttpUrl, field_validator

# Импортируем ContentType и ArchetypeType из core
from mindbank_poc.core.common.types import ContentType, ArchetypeType
# Импортируем модели ConnectorMessage, ConfigValidation
from mindbank_poc.core.models.connector import ConnectorMessage, ConfigValidation
from mindbank_poc.core.models.connector import ConnectorStage
# Импортируем модели для токенов доступа
from mindbank_poc.core.models.access_token import ScopeType, AccessTokenType

# Определяем схему ConnectorStep здесь, чтобы избежать циклического импорта
# и добавить новое поле options
class ConnectorStep(BaseModel):
    """Схема для шага настройки коннектора."""
    id: str
    status: str
    title: Optional[str] = None
    message: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description='Опциональный список опций для выбора пользователем (например, `[{"value": "id1", "label": "Name 1"}]`)'
    )

class RawEntryInput(BaseModel):
    """Схема для входной сырой записи."""
    collector_id: str = Field(
        description="Уникальный идентификатор коллектора"
    )
    group_id: str = Field(
        description="Идентификатор группы, к которой принадлежит запись"
    )
    entry_id: str = Field(
        description="Уникальный идентификатор записи"
    )
    type: ContentType = Field(
        description="Тип содержимого записи"
    )
    archetype: Optional[str] = Field(
        default=None,
        description="Семантический тип (архитип) контента"
    )
    payload: Dict[str, Any] = Field(
        description="Данные записи"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Метаданные записи"
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        description="Время создания записи (если не указано, будет использовано текущее время)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "collector_id": "telegram-001",
                "group_id": "chat-12345",
                "entry_id": "msg-67890",
                "type": "text",
                "payload": {"content": "Hello, world!"},
                "metadata": {
                    "source": "telegram",
                    "author": "user123",
                    "is_last": True, # Flag indicating this is the last entry in a batch/group
                    "group_timeout_seconds": 120 # Optional: group-specific timeout in seconds
                },
                "timestamp": "2023-04-01T12:00:00"
            }
        }

class AggregateInput(BaseModel):
    """Схема для входных агрегированных данных."""
    group_id: str = Field(
        description="Уникальный идентификатор группы"
    )
    entries: List[RawEntryInput] = Field(
        description="Список записей в группе"
    )
    archetype: Optional[str] = Field(
        default=None,
        description="Семантический тип (архитип) агрегата"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Метаданные агрегата"
    )
    # aggregated_at будет добавлен бекендом

# Новая схема для setup_details
class SetupDetails(BaseModel):
    """Детали для сложной первоначальной настройки коннектора."""
    setup_url: Optional[str] = Field(default=None, description="URL для UI настройки коннектора. Mindbank может передать сюда connector_id.")
    setup_instructions: Optional[str] = Field(default=None, description="Текстовые инструкции для администратора по настройке.")

class ConnectorRegistrationRequest(BaseModel):
    """Схема для регистрации нового коннектора."""
    type: str = Field(
        description="Идентификатор типа коннектора (например, 'telegram')"
    )
    metadata: Dict[str, Any] = Field(
        description="Метаданные коннектора (должен содержать хотя бы version и description)"
    )
    config_schema: Dict[str, Any] = Field(
        description="Описание требуемых полей конфигурации"
    )
    integration_key: str = Field(
        description="Ключ интеграции для регистрации коннектора"
    )
    capabilities: Optional[List[str]] = Field(
        default_factory=list,
        description="Возможности коннектора (например, 'multi-account', 'file-support')"
    )
    supported_archetypes: Optional[List[str]] = Field(
        default_factory=list,
        description="Список поддерживаемых архитипов данных"
    )
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Начальная конфигурация коннектора (должна быть валидна по config_schema)"
    )
    setup_details: Optional[SetupDetails] = Field(default=None, description="Детали для сложной первоначальной настройки, если требуется.")
    skip_periodic_handshake: bool = Field(
        default=False,
        description="Если True, коннектор не будет выполнять периодический handshake и должен быть готов к работе сразу"
    )
    dynamic_options: Optional[Dict[str, Any]] = None

class ConnectorRegistrationResponse(BaseModel):
    """Схема ответа при регистрации коннектора."""
    connector_id: str
    access_token: str
    config: Dict[str, Any] = Field(default_factory=dict)
    stage: str
    setup_url_resolved: Optional[str] = None

class ConnectorHandshakeResponse(BaseModel):
    """Схема ответа для handshake запроса от коннектора."""
    stage: str
    enabled: bool
    current_config: Dict[str, Any]
    config_validation: Dict[str, Any]
    setup_url_resolved: Optional[str] = None
    messages: List[Dict[str, Any]]
    capabilities: List[str]
    auth_token: Optional[str] = None

class ConnectorConfigUpdate(BaseModel):
    """Схема для полного обновления конфигурации коннектора."""
    config: Dict[str, Any] = Field(
        description="Новая конфигурация коннектора"
    )

class ConnectorToggle(BaseModel):
    """Schema для изменения статуса активности коннектора"""
    enabled: bool

class ConnectorArchetypesUpdate(BaseModel):
    """Схема для обновления поддерживаемых архитипов коннектора."""
    supported_archetypes: List[str] = Field(
        description="Список поддерживаемых архитипов данных"
    )

class ConnectorResponse(BaseModel):
    """Базовый ответ для API-вызовов к коннекторам"""
    status: str
    message: Optional[str] = None

# Схемы для ключей интеграции
class IntegrationKeyRequest(BaseModel):
    """Схема для создания ключа интеграции."""
    name: str = Field(
        description="Название ключа интеграции"
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание ключа интеграции"
    )
    allow_skip_periodic_handshake: bool = Field(
        default=False,
        description="Разрешает ли ключ регистрацию коннекторов в 'облегченном' режиме (без периодического handshake)"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Дата истечения срока действия ключа"
    )

class IntegrationKeyResponse(BaseModel):
    """Схема для ответа с информацией о ключе интеграции."""
    key_id: str = Field(
        description="Уникальный идентификатор ключа"
    )
    key_value: str = Field(
        description="Значение ключа для использования при регистрации коннектора"
    )
    name: str = Field(
        description="Название ключа"
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание ключа"
    )
    allow_skip_periodic_handshake: bool = Field(
        description="Разрешает ли ключ регистрацию коннекторов в 'облегченном' режиме"
    )
    is_active: bool = Field(
        description="Активен ли ключ"
    )
    created_at: datetime = Field(
        description="Дата создания ключа"
    )
    updated_at: datetime = Field(
        description="Дата последнего обновления ключа"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Дата истечения срока действия ключа"
    )

# --- Схемы для поиска (Retrieval) --- 

class NormalizedUnitSchema(BaseModel):
    """Схема для отображения NormalizedUnit в API."""
    aggregate_id: str
    text_repr: str
    vector_repr: Optional[List[float]] = None
    archetype: Optional[str] = None
    classification: Dict[str, Any]
    metadata: Dict[str, Any]
    normalized_at: datetime

    class Config:
        from_attributes = True # Используем orm_mode для Pydantic v2

# Модель запроса расширенной фильтрации
class FilterRequest(BaseModel):
    """Схема для запроса расширенной фильтрации."""
    archetype: Optional[str] = Field(
        default=None,
        description="Архетип (тип) контента (например, document, note, meeting_notes, transcription)"
    )
    source: Optional[str] = Field(
        default=None,
        description="Источник данных (тип коннектора, например, telegram, gmail)"
    )
    source_name: Optional[str] = Field(
        default=None,
        description="Название конкретного источника (например, имя чата в Telegram)"
    )
    author: Optional[str] = Field(
        default=None,
        description="Автор или создатель контента"
    )
    date_from: Optional[datetime] = Field(
        default=None,
        description="Фильтр по дате создания (от)"
    )
    date_to: Optional[datetime] = Field(
        default=None,
        description="Фильтр по дате создания (до)"
    )
    classification_types: Optional[List[str]] = Field(
        default=None,
        description="Список типов классификации контента (например, business, personal)"
    )
    custom_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Любые дополнительные метаданные для фильтрации в формате ключ-значение"
    )
    tags: Optional[List[str]] = Field(
        default=None,
        description="Список тегов для фильтрации"
    )
    limit: int = Field(
        default=50,
        description="Максимальное количество результатов"
    )
    sort_by: Optional[str] = Field(
        default="normalized_at",
        description="Поле для сортировки результатов (например, normalized_at, author)"
    )
    sort_order: Optional[str] = Field(
        default="desc",
        description="Порядок сортировки ('asc' или 'desc')"
    )

class SearchRequest(BaseModel):
    """Схема для запроса поиска."""
    query_text: Optional[str] = Field(
        default=None,
        description="Текст запроса для поиска"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Фильтры по метаданным"
    )
    archetype: Optional[str] = Field(
        default=None,
        description="Фильтр по архетипу"
    )
    mode: str = Field(
        default="hybrid",
        description="Режим поиска: 'semantic', 'fulltext', 'hybrid'"
    )
    limit: int = Field(
        default=10,
        description="Максимальное количество результатов"
    )

class SearchResultItem(BaseModel):
    """Схема для одного элемента в результатах поиска."""
    score: float = Field(description="Релевантность результата (зависит от режима поиска)")
    normalized_unit: NormalizedUnitSchema = Field(description="Найденная нормализованная единица")
    raw_aggregate: AggregateInput = Field(description="Соответствующий агрегат с сырыми данными (RawEntry)")

class SearchResponse(BaseModel):
    """Схема для ответа на поисковый запрос."""
    results: List[SearchResultItem] = Field(description="Список найденных результатов")

class DynamicOptionsUpdate(BaseModel):
    """Схема для обновления динамических опций коннектора"""
    dynamic_options: Dict[str, Any]
    new_config_schema: Optional[Dict[str, Any]] = None

# --- Схемы для токенов доступа (Access Tokens) ---

class AccessScopeCreate(BaseModel):
    """Схема для создания скоупа доступа."""
    scope_type: ScopeType = Field(
        description="Тип скоупа (ARCHETYPE, TYPE, TAG, SOURCE, ALL)"
    )
    values: Optional[List[str]] = Field(
        default=None,
        description="Список значений для скоупа (не требуется для типа ALL)"
    )

class AccessTokenCreate(BaseModel):
    """Схема для создания токена доступа."""
    name: str = Field(
        description="Название токена доступа"
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание токена доступа"
    )
    token_type: AccessTokenType = Field(
        default=AccessTokenType.STANDARD,
        description="Тип токена (STANDARD, MASTER, DELEGATED)"
    )
    scopes: List[AccessScopeCreate] = Field(
        default_factory=list,
        description="Список скоупов доступа"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Дата истечения срока действия токена"
    )

class AccessTokenResponse(BaseModel):
    """Схема для ответа с информацией о токене доступа."""
    token_id: str = Field(
        description="Уникальный идентификатор токена"
    )
    token_value: str = Field(
        description="Значение токена для использования при авторизации"
    )
    name: str = Field(
        description="Название токена"
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание токена"
    )
    token_type: AccessTokenType = Field(
        description="Тип токена (STANDARD, MASTER, DELEGATED)"
    )
    scopes: List[Dict[str, Any]] = Field(
        description="Список скоупов доступа"
    )
    is_active: bool = Field(
        description="Активен ли токен"
    )
    created_at: datetime = Field(
        description="Дата создания токена"
    )
    updated_at: datetime = Field(
        description="Дата последнего обновления токена"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Дата истечения срока действия токена"
    )
    created_by: Optional[str] = Field(
        default=None,
        description="ID пользователя или системы, создавшей токен"
    )

class AccessTokenList(BaseModel):
    """Схема для списка токенов доступа."""
    tokens: List[AccessTokenResponse] = Field(
        description="Список токенов доступа"
    )

class AvailableScopesResponse(BaseModel):
    """Схема для ответа с доступными скоупами."""
    scopes: Dict[str, List[str]] = Field(
        description="Словарь с доступными скоупами, где ключи - типы скоупов, а значения - списки доступных значений"
    )

# --- Схемы для fingerprint токенов ---

class FingerprintTokenRequest(BaseModel):
    """Схема для создания и обновления fingerprint-токена."""
    name: str = Field(
        description="Название токена"
    )
    description: Optional[str] = Field(
        default=None,
        description="Описание токена"
    )
    token_type: str = Field(
        default="standard",
        description="Тип токена (master, standard, temporary, internal)"
    )
    allowed_archetypes: Optional[List[str]] = Field(
        default=None,
        description="Список разрешенных архетипов (пустой = без ограничений)"
    )
    allowed_connector_ids: Optional[List[str]] = Field(
        default=None,
        description="Список разрешенных ID коннекторов (пустой = без ограничений)"
    )
    allowed_connector_types: Optional[List[str]] = Field(
        default=None,
        description="Список разрешенных типов коннекторов (пустой = без ограничений)"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Дата истечения срока действия токена"
    )

class FingerprintTokenFilterQuery(BaseModel):
    """Схема для запроса списка fingerprint-токенов с фильтрами."""
    token_type: Optional[str] = Field(
        default=None,
        description="Фильтр по типу токена"
    )
    archetype: Optional[str] = Field(
        default=None,
        description="Фильтр по архетипу (токены с доступом к указанному архетипу)"
    )
    connector_id: Optional[str] = Field(
        default=None,
        description="Фильтр по ID коннектора (токены с доступом к указанному коннектору)"
    )
    is_active: Optional[bool] = Field(
        default=None,
        description="Фильтр по активности токена"
    )

class FingerprintTokenResponse(BaseModel):
    """Схема ответа с данными fingerprint-токена."""
    token_id: str = Field(description="Уникальный идентификатор токена")
    token_value: str = Field(description="Значение токена для использования в заголовке X-API-Key")
    name: str = Field(description="Название токена")
    description: Optional[str] = Field(default=None, description="Описание токена")
    token_type: str = Field(description="Тип токена (master, standard, temporary, internal)")
    is_active: bool = Field(description="Активен ли токен")
    created_at: datetime = Field(description="Дата создания токена")
    updated_at: datetime = Field(description="Дата последнего обновления токена")
    expires_at: Optional[datetime] = Field(default=None, description="Дата истечения срока действия токена")
    created_by: Optional[str] = Field(default=None, description="ID пользователя или системы, создавшей токен")
    allowed_archetypes: List[str] = Field(description="Список разрешенных архетипов")
    allowed_connector_ids: List[str] = Field(description="Список разрешенных ID коннекторов")
    allowed_connector_types: List[str] = Field(description="Список разрешенных типов коннекторов")
