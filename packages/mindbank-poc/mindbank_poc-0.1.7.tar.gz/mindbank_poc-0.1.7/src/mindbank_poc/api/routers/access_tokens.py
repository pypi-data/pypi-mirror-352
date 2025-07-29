"""
Роутер для управления токенами доступа (скоуп-фингерпринтами).
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from mindbank_poc.api.schemas import (
    AccessTokenCreate, AccessTokenResponse, AccessTokenList, AvailableScopesResponse
)
from mindbank_poc.core.models.access_token import (
    AccessToken, AccessScope, ScopeType, AccessTokenType
)
from mindbank_poc.core.services.access_token_service import get_access_token_service
from mindbank_poc.core.services.auth_service import verify_admin_auth
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

# Создаем роутер
router = APIRouter(
    prefix="/access",
    tags=["Access Tokens"],
    responses={404: {"description": "Not found"}},
)

security = HTTPBearer(auto_error=False)

async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    x_admin_api_key: str = Header(None, alias="X-Admin-API-Key")
) -> AccessToken:
    """
    Получение текущего токена доступа из заголовка Authorization или X-Admin-API-Key.
    Если передан admin API-ключ — возвращает виртуальный мастер-токен.
    """
    admin_api_key = settings.auth.admin_api_key
    now = datetime.now()
    # Проверка через X-Admin-API-Key
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
    # Проверка через Bearer
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
    # Обычная логика для обычных токенов
    if not credentials:
        logger.warning("Попытка доступа без токена")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется токен доступа",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_value = credentials.credentials
    token_service = get_access_token_service()
    token = token_service.get_token_by_value(token_value)
    if not token:
        logger.warning(f"Попытка доступа с несуществующим токеном: {token_value[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен доступа",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not token.is_active:
        logger.warning(f"Попытка доступа с неактивным токеном: {token.token_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен доступа отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token.expires_at and token.expires_at < now:
        logger.warning(f"Попытка доступа с истекшим токеном: {token.token_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


async def get_admin_token(token: AccessToken = Depends(get_current_token)) -> AccessToken:
    """
    Проверка, что текущий токен имеет права администратора (мастер-токен).
    
    Args:
        token: Токен доступа.
        
    Returns:
        Токен доступа с правами администратора.
        
    Raises:
        HTTPException: Если токен не имеет прав администратора.
    """
    if token.token_type != AccessTokenType.MASTER:
        logger.warning(f"Попытка административного доступа с недостаточными правами: {token.token_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения операции",
        )
    
    return token


def require_token_type(allowed_types: List[AccessTokenType]):
    """
    Зависимость для проверки типа токена.
    
    Args:
        allowed_types: Список разрешенных типов токенов.
        
    Returns:
        Функция-зависимость для FastAPI.
    """
    async def check_token_type(token: AccessToken = Depends(get_current_token)) -> AccessToken:
        if token.token_type not in allowed_types:
            logger.warning(f"Попытка доступа с недостаточными правами: {token.token_id}, тип: {token.token_type}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции",
            )
        return token
    
    return check_token_type


@router.post("/tokens", response_model=AccessTokenResponse)
async def create_token(
    token_data: AccessTokenCreate,
    _: bool = Depends(verify_admin_auth)
) -> AccessTokenResponse:
    """
    Создание нового токена доступа.
    
    Args:
        token_data: Данные для создания токена.
        _: Административный ключ из заголовка.
        
    Returns:
        Созданный токен доступа.
    """
    token_service = get_access_token_service()
    
    # Преобразуем скоупы из схемы в модель
    scopes = []
    for scope_data in token_data.scopes:
        scope = AccessScope(
            scope_type=scope_data.scope_type,
            values=scope_data.values
        )
        scopes.append(scope)
    
    # Создаем токен
    token = token_service.create_token(
        name=token_data.name,
        description=token_data.description,
        token_type=token_data.token_type,
        scopes=scopes,
        expires_at=token_data.expires_at,
        created_by=token.token_id  # Используем ID токена как created_by
    )
    
    logger.info(f"Создан новый токен доступа: {token.token_id}, тип: {token.token_type}")
    
    # Преобразуем скоупы в словари для ответа
    scopes_data = []
    for scope in token.scopes:
        scope_data = {
            "scope_type": scope.scope_type,
            "values": scope.values
        }
        scopes_data.append(scope_data)
    
    # Формируем ответ
    return AccessTokenResponse(
        token_id=token.token_id,
        token_value=token.token_value,
        name=token.name,
        description=token.description,
        token_type=token.token_type,
        scopes=scopes_data,
        is_active=token.is_active,
        created_at=token.created_at,
        updated_at=token.updated_at,
        expires_at=token.expires_at,
        created_by=token.created_by
    )


@router.get("/tokens", response_model=AccessTokenList)
async def get_tokens(
    _: bool = Depends(verify_admin_auth)
) -> AccessTokenList:
    """
    Получение списка всех токенов доступа.
    
    Args:
        _: Административный ключ из заголовка.
        
    Returns:
        Список токенов доступа.
    """
    token_service = get_access_token_service()
    tokens = token_service.get_tokens()
    
    # Преобразуем токены в ответ
    tokens_response = []
    for token in tokens:
        # Преобразуем скоупы в словари для ответа
        scopes_data = []
        for scope in token.scopes:
            scope_data = {
                "scope_type": scope.scope_type,
                "values": scope.values
            }
            scopes_data.append(scope_data)
        
        # Формируем ответ для токена
        token_response = AccessTokenResponse(
            token_id=token.token_id,
            token_value=token.token_value,
            name=token.name,
            description=token.description,
            token_type=token.token_type,
            scopes=scopes_data,
            is_active=token.is_active,
            created_at=token.created_at,
            updated_at=token.updated_at,
            expires_at=token.expires_at,
            created_by=token.created_by
        )
        
        tokens_response.append(token_response)
    
    return AccessTokenList(tokens=tokens_response)


@router.get("/tokens/{token_id}", response_model=AccessTokenResponse)
async def get_token(
    token_id: str,
    _: bool = Depends(verify_admin_auth)
) -> AccessTokenResponse:
    """
    Получение информации о токене доступа по ID.
    
    Args:
        token_id: ID токена.
        _: Административный ключ из заголовка.
        
    Returns:
        Информация о токене доступа.
        
    Raises:
        HTTPException: Если токен не найден.
    """
    token_service = get_access_token_service()
    token = token_service.get_token_by_id(token_id)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Токен с ID {token_id} не найден",
        )
    
    # Преобразуем скоупы в словари для ответа
    scopes_data = []
    for scope in token.scopes:
        scope_data = {
            "scope_type": scope.scope_type,
            "values": scope.values
        }
        scopes_data.append(scope_data)
    
    # Формируем ответ
    return AccessTokenResponse(
        token_id=token.token_id,
        token_value=token.token_value,
        name=token.name,
        description=token.description,
        token_type=token.token_type,
        scopes=scopes_data,
        is_active=token.is_active,
        created_at=token.created_at,
        updated_at=token.updated_at,
        expires_at=token.expires_at,
        created_by=token.created_by
    )


@router.delete("/tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    token_id: str,
    _: bool = Depends(verify_admin_auth)
):
    """
    Отзыв токена доступа.
    
    Args:
        token_id: ID токена.
        _: Административный ключ из заголовка.
        
    Raises:
        HTTPException: Если токен не найден.
    """
    token_service = get_access_token_service()
    success = token_service.revoke_token(token_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Токен с ID {token_id} не найден",
        )
    
    logger.info(f"Отозван токен доступа: {token_id}")


@router.get("/scopes", response_model=AvailableScopesResponse)
async def get_available_scopes(
    _: bool = Depends(verify_admin_auth)
) -> AvailableScopesResponse:
    """
    Получение доступных скоупов для создания токенов.
    
    Args:
        _: Административный ключ из заголовка.
        
    Returns:
        Доступные скоупы.
    """
    token_service = get_access_token_service()
    scopes = token_service.get_available_scopes()
    
    return AvailableScopesResponse(scopes=scopes)
