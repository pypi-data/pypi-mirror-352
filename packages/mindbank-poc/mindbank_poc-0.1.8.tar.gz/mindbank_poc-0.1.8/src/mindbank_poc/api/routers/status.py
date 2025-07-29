"""
Роутер для API статуса системы.
"""

import time
import platform
import os
import datetime
import psutil
from typing import Dict, Any, Optional, List, Union

from fastapi import APIRouter, Depends, HTTPException, status, Security, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from mindbank_poc.core.models.access_token import AccessTokenType, AccessToken, AccessScope, ScopeType
from mindbank_poc.core.services.access_token_service import get_access_token_service
from mindbank_poc.api.routers.access_tokens import get_current_token
from mindbank_poc.core.config.settings import settings
from mindbank_poc.core.connectors.service import get_connector_service
from mindbank_poc.core.services.auth_service import verify_admin_auth

# Создаем роутер
router = APIRouter(
    prefix="/status",
    tags=["System Status"],
    responses={404: {"description": "Not found"}},
)

# Модели данных для ответов API
class SystemInfo(BaseModel):
    """Базовая информация о системе."""
    os: str
    python_version: str
    hostname: str
    data_dir: str


class ProcessInfo(BaseModel):
    """Информация о процессе."""
    pid: int
    memory_usage_mb: float
    cpu_percent: float
    threads: int
    uptime_seconds: int


class ConnectorsInfo(BaseModel):
    """Информация о коннекторах."""
    total: int
    enabled: int
    disabled: int


class TokensInfo(BaseModel):
    """Информация о токенах доступа."""
    total: int
    active: int
    master: int
    standard: int
    delegated: int


class SettingsInfo(BaseModel):
    """Информация о настройках системы."""
    debug: bool
    normalizer_offline_mode: bool
    data_dir: str


class ExtendedInfo(BaseModel):
    """Расширенная информация о системе (только для мастер-токенов)."""
    process: ProcessInfo
    connectors: ConnectorsInfo
    tokens: TokensInfo
    settings: SettingsInfo


class BasicSystemStatusResponse(BaseModel):
    """Базовый ответ API статуса системы."""
    status: str
    version: str
    timestamp: str
    system_info: SystemInfo
    core_ready: bool
    connector_service_status: str
    integration_key_service_status: str
    settings_valid: bool


class ExtendedSystemStatusResponse(BasicSystemStatusResponse):
    """Расширенный ответ API статуса системы (для мастер-токенов)."""
    extended_info: ExtendedInfo


@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """
    Простая проверка работоспособности API.
    Не требует авторизации.
    """
    return {"status": "ok"}


security = HTTPBearer(auto_error=False)

def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    x_admin_api_key: str = Header(None, alias="X-Admin-API-Key")
) -> AccessToken:
    admin_api_key = settings.auth.admin_api_key
    now = datetime.datetime.now()
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


@router.get("/", response_model=Union[BasicSystemStatusResponse, ExtendedSystemStatusResponse])
async def get_system_status(token: AccessToken = Depends(get_current_token)):
    """
    Получение информации о статусе системы.
    Требует административный API-ключ.
    """
    # Базовая информация о системе
    system_info = SystemInfo(
        os=f"{platform.system()} {platform.release()}",
        python_version=platform.python_version(),
        hostname=platform.node(),
        data_dir=os.path.abspath(settings.storage.data_dir)
    )

    # Проверка статуса сервисов
    # Проверка connector_service
    try:
        connector_service = get_connector_service()
        connector_service_status = "running" if connector_service and getattr(connector_service, "is_running", lambda: False)() else "not_running"
    except Exception:
        connector_service_status = "error"

    # Проверка integration_key_service
    try:
        from mindbank_poc.core.services.integration_key_service import get_integration_key_service
        integration_key_service = get_integration_key_service()
        integration_key_service_status = "available" if integration_key_service else "not_available"
    except Exception:
        integration_key_service_status = "error"

    # Проверка валидности настроек
    try:
        settings_valid = bool(settings.api.host and settings.api.port)
    except Exception:
        settings_valid = False

    # Core считается ready, если все сервисы running/available и настройки валидны
    core_ready = (
        connector_service_status == "running"
        and integration_key_service_status == "available"
        and settings_valid
    )

    response_data = {
        "status": "ok",
        "version": settings.app_version,
        "timestamp": datetime.datetime.now().isoformat(),
        "system_info": system_info,
        "core_ready": core_ready,
        "connector_service_status": connector_service_status,
        "integration_key_service_status": integration_key_service_status,
        "settings_valid": settings_valid,
    }
    # Можно добавить расширенную информацию, если нужно
    return response_data
