"""
Роутер для API управления провайдерами обработки данных.
"""

from typing import Dict, Any, List, Optional, Literal, Union
from fastapi import APIRouter, Depends, HTTPException, status, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import os
import json

from mindbank_poc.core.common.types import ProviderType
from mindbank_poc.core.models.access_token import AccessTokenType, AccessToken, AccessScope, ScopeType
from mindbank_poc.core.services.auth_service import verify_admin_auth
from mindbank_poc.core.config.settings import settings
from mindbank_poc.core.services.provider_service import get_provider_service, DEFAULT_PROVIDERS_PATH
from mindbank_poc.core.models.provider import ProviderFilter, ProviderModel, MetadataCondition
from datetime import datetime

# Создаем роутер
router = APIRouter(
    prefix="/api/processing/providers",
    tags=["Processing Providers"],
    responses={404: {"description": "Not found"}},
)

# Модели данных для API
class ProviderConfig(BaseModel):
    """Конфигурация провайдера обработки."""
    config: Dict[str, Any] = Field(..., description="Параметры конфигурации провайдера")

class ProviderInfo(BaseModel):
    """Информация о провайдере обработки."""
    id: str
    name: str
    description: str
    provider_type: str
    supported_archetypes: List[str] = []
    config_schema: Dict[str, Any] = {}
    current_config: Dict[str, Any] = {}
    status: str = "active"
    capabilities: List[str] = []
    filters: List[ProviderFilter] = Field(default_factory=list, description="Фильтры для выбора провайдера")
    
    @classmethod
    def from_provider_model(cls, model: ProviderModel) -> "ProviderInfo":
        """Convert a ProviderModel to a ProviderInfo."""
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
            provider_type=model.provider_type.value,
            supported_archetypes=model.supported_archetypes,
            config_schema=model.config_schema,
            current_config=model.current_config,
            status=model.status,
            capabilities=model.capabilities,
            filters=model.filters
        )

class ProvidersResponse(BaseModel):
    """Ответ со списком доступных провайдеров."""
    providers: List[ProviderInfo]

class DefaultProviderMapping(BaseModel):
    """Маппинг типа провайдера к конкретному провайдеру."""
    provider_type: str
    provider_id: str

class DefaultProvidersRequest(BaseModel):
    """Запрос на установку провайдеров по умолчанию."""
    defaults: List[DefaultProviderMapping]

class DefaultProvidersResponse(BaseModel):
    """Ответ с текущими провайдерами по умолчанию."""
    defaults: List[DefaultProviderMapping]

security = HTTPBearer(auto_error=False)

def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    x_admin_api_key: str = Header(None, alias="X-Admin-API-Key")
) -> AccessToken:
    admin_api_key = settings.auth.admin_api_key
    now = datetime.now()
    if x_admin_api_key and x_admin_api_key == admin_api_key:
        return AccessToken(
            token_id="admin-api-key",
            token_value=admin_api_key,
            name="Admin API Key",
            token_type=AccessTokenType.MASTER,
            scopes=[AccessScope(scope_type=ScopeType.ALL)],
            is_active=True,
            created_at=now,
            updated_at=now,
            expires_at=None,
            created_by="system"
        )
    if credentials and credentials.credentials == admin_api_key:
        return AccessToken(
            token_id="admin-api-key",
            token_value=admin_api_key,
            name="Admin API Key",
            token_type=AccessTokenType.MASTER,
            scopes=[AccessScope(scope_type=ScopeType.ALL)],
            is_active=True,
            created_at=now,
            updated_at=now,
            expires_at=None,
            created_by="system"
        )
    # Здесь можно добавить обычную логику проверки пользовательских токенов, если потребуется
    # Пока возвращаем 401 если не admin ключ
    raise HTTPException(
        status_code=401,
        detail="Недействительный токен или ключ",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.get("", response_model=ProvidersResponse)
async def get_all_providers(_: bool = Depends(verify_admin_auth)):
    """
    Получение списка всех доступных провайдеров обработки данных.
    """
    provider_service = get_provider_service()
    providers = provider_service.get_all_providers()
    
    # Convert to ProviderInfo objects
    provider_infos = [ProviderInfo.from_provider_model(p) for p in providers]
    
    return {"providers": provider_infos}


@router.post("/{provider_id}/config", response_model=ProviderInfo)
async def update_provider_config(
    provider_id: str,
    config_data: ProviderConfig,
    _: bool = Depends(verify_admin_auth)
):
    """
    Обновление конфигурации провайдера обработки данных.
    Требует административный API-ключ.
    """
    provider_service = get_provider_service()
    updated_provider = provider_service.update_provider_config(provider_id, config_data.config)
    
    if not updated_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Провайдер с ID {provider_id} не найден"
        )
        
    return ProviderInfo.from_provider_model(updated_provider)

@router.get("/defaults", response_model=DefaultProvidersResponse)
async def get_default_providers(_: bool = Depends(verify_admin_auth)):
    """
    Получение текущих провайдеров по умолчанию для каждого типа обработки.
    """
    provider_service = get_provider_service()
    defaults = []
    
    for provider_type in ProviderType:
        default_id = provider_service.get_default_provider(provider_type)
        if default_id:
            defaults.append({
                "provider_type": provider_type.value,
                "provider_id": default_id
            })
    
    return {"defaults": defaults}

@router.post("/defaults", response_model=DefaultProvidersResponse)
async def set_default_providers(
    request: DefaultProvidersRequest,
    _: bool = Depends(verify_admin_auth)
):
    """
    Установка провайдеров по умолчанию для каждого типа обработки.
    Требует административный API-ключ.
    """
    provider_service = get_provider_service()
    
    for mapping in request.defaults:
        try:
            provider_type = ProviderType(mapping.provider_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный тип провайдера: {mapping.provider_type}"
            )
            
        provider = provider_service.get_provider(mapping.provider_id)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Провайдер с ID {mapping.provider_id} не найден"
            )
            
        if provider.provider_type.value != mapping.provider_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Провайдер {mapping.provider_id} не поддерживает тип обработки {mapping.provider_type}"
            )
            
        success = provider_service.set_default_provider(provider_type, mapping.provider_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Не удалось установить провайдер {mapping.provider_id} по умолчанию для типа {mapping.provider_type}"
            )
    
    # Return updated defaults
    return await get_default_providers(_)

@router.get("/{provider_id}/filters", response_model=List[ProviderFilter])
async def get_provider_filters(
    provider_id: str,
    _: bool = Depends(verify_admin_auth)
):
    """
    Получение списка фильтров для провайдера обработки данных.
    Требует административный API-ключ.
    """
    provider_service = get_provider_service()
    filters = provider_service.get_provider_filters(provider_id)
    
    if filters is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Провайдер с ID {provider_id} не найден"
        )
        
    return filters

@router.post("/{provider_id}/filters", response_model=ProviderInfo)
async def add_provider_filter(
    provider_id: str,
    filter_data: ProviderFilter,
    _: bool = Depends(verify_admin_auth)
):
    """
    Добавление фильтра для провайдера обработки данных.
    Требует административный API-ключ.
    """
    provider_service = get_provider_service()
    updated_provider = provider_service.add_provider_filter(provider_id, filter_data)
    
    if not updated_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Провайдер с ID {provider_id} не найден"
        )
        
    return ProviderInfo.from_provider_model(updated_provider)

@router.delete("/{provider_id}/filters/{filter_index}", response_model=ProviderInfo)
async def delete_provider_filter(
    provider_id: str,
    filter_index: int,
    _: bool = Depends(verify_admin_auth)
):
    """
    Удаление фильтра для провайдера обработки данных.
    Требует административный API-ключ.
    """
    provider_service = get_provider_service()
    updated_provider = provider_service.delete_provider_filter(provider_id, filter_index)
    
    if not updated_provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Провайдер с ID {provider_id} не найден или фильтр с индексом {filter_index} не существует"
        )
        
    return ProviderInfo.from_provider_model(updated_provider)

@router.get("/{provider_id}/status", response_model=Dict[str, Any])
async def get_provider_status(
    provider_id: str,
    token: AccessToken = Depends(get_current_token)
):
    """
    Получение статуса провайдера обработки данных.
    """
    provider_service = get_provider_service()
    provider = provider_service.get_provider(provider_id)
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Провайдер с ID {provider_id} не найден"
        )
    
    # В реальной системе здесь должна быть логика проверки статуса провайдера
    # Например, проверка доступности API, лимитов и т.д.
    
    return {
        "status": provider.status,
        "limits": {
            "daily_requests": 10000,
            "remaining_requests": 9500,
            "reset_at": "2025-05-14T00:00:00Z"
        },
        "performance": {
            "avg_response_time_ms": 250,
            "success_rate": 0.99
        }
    }
