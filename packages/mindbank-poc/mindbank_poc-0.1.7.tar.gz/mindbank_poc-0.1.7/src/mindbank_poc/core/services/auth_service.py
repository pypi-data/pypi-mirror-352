import os
import secrets
from typing import Optional, List, Any
import hashlib
import base64
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

def verify_admin_auth(x_admin_api_key: str = Header(None, alias="X-Admin-API-Key")):
    """
    Проверяет административный API-ключ из заголовка X-Admin-API-Key через Depends(Header).
    Args:
        x_admin_api_key: значение заголовка X-Admin-API-Key
    Returns:
        True, если ключ валиден, иначе вызывает HTTPException 401
    """
    admin_api_key = settings.auth.admin_api_key
    if not x_admin_api_key or x_admin_api_key != admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return True

def generate_admin_password_hash(password: str) -> str:
    """
    Генерирует хеш пароля администратора.
    
    Args:
        password: Пароль в открытом виде
        
    Returns:
        Хеш пароля
    """
    password_bytes = password.encode("utf-8")
    hashed_password = hashlib.sha256(password_bytes).hexdigest()
    return hashed_password

async def verify_fingerprint_token(
    x_api_key: str = Header(None, alias="X-API-Key"),
    archetype: Optional[str] = None,
    connector_id: Optional[str] = None,
    connector_type: Optional[str] = None,
    required_types: Optional[List[str]] = None
) -> Any:
    """
    Проверяет fingerprint-токен из заголовка X-API-Key.
    
    Args:
        x_api_key: значение заголовка X-API-Key
        archetype: ограничение доступа по архетипу
        connector_id: ограничение доступа по ID коннектора
        connector_type: ограничение доступа по типу коннектора
        required_types: список разрешенных типов токенов; если None, разрешены все типы
        
    Returns:
        Объект fingerprint-токена, если токен валиден и имеет необходимые права
        
    Raises:
        HTTPException: 401 если токен отсутствует или невалиден,
                       403 если токен не имеет необходимых прав
    """
    from mindbank_poc.core.services.fingerprint_token_service import get_fingerprint_token_service
    from mindbank_poc.core.models.fingerprint_token import FingerprintTokenType
    
    # Проверка наличия токена
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Проверка административного API-ключа 
    # (альтернатива fingerprint-токену, всегда имеет полный доступ)
    admin_api_key = settings.auth.admin_api_key
    if x_api_key == admin_api_key:
        return True
    
    # Получение и проверка fingerprint-токена
    token_service = get_fingerprint_token_service()
    token = token_service.get_token_by_value(x_api_key)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Проверка срока действия
    if token.is_expired():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Проверка типа токена, если требуется
    if required_types and token.token_type not in required_types:
        # Master-токен имеет доступ всегда
        if token.token_type != FingerprintTokenType.MASTER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key doesn't have required type ({', '.join(required_types)})",
            )
    
    # Проверка доступа по фильтрам (архетип, коннектор и т.д.)
    if not token.has_access(archetype=archetype, connector_id=connector_id, connector_type=connector_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key doesn't have access to the requested resource",
        )
    
    return token

def require_fp_token(
    archetype: Optional[str] = None, 
    connector_id: Optional[str] = None, 
    connector_type: Optional[str] = None,
    required_types: Optional[List[str]] = None
):
    """
    Фабрика для создания зависимости FastAPI, проверяющей fingerprint-токен с заданными ограничениями.
    
    Args:
        archetype: ограничение доступа по архетипу
        connector_id: ограничение доступа по ID коннектора
        connector_type: ограничение доступа по типу коннектора
        required_types: список разрешенных типов токенов
        
    Returns:
        Функция-зависимость для FastAPI, возвращающая объект токена при успешной проверке
    """
    async def check_fingerprint_token(x_api_key: str = Header(None, alias="X-API-Key")):
        return await verify_fingerprint_token(
            x_api_key=x_api_key,
            archetype=archetype,
            connector_id=connector_id,
            connector_type=connector_type,
            required_types=required_types
        )
    
    return check_fingerprint_token 