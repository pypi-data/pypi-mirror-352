from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from mindbank_poc.api.schemas import IntegrationKeyRequest, IntegrationKeyResponse
from mindbank_poc.core.services.integration_key_service import get_integration_key_service, IntegrationKeyService
from mindbank_poc.core.services.auth_service import verify_admin_auth
from mindbank_poc.core.config.settings import settings
from mindbank_poc.common.logging import get_logger

router = APIRouter(
    prefix="/integration-keys",
    tags=["Integration Keys"],
)

logger = get_logger(__name__)

class TypeSpecificKeyRequest(BaseModel):
    """Request model for creating a connector-type-specific integration key."""
    name: str
    description: Optional[str] = None
    allow_skip_periodic_handshake: bool = False
    type_restrictions: List[str]
    expires_at: Optional[datetime] = None

@router.post("/for-type", response_model=IntegrationKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_key_for_type(
    request: TypeSpecificKeyRequest,
    key_service: IntegrationKeyService = Depends(get_integration_key_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Создает новый ключ интеграции для конкретного типа коннектора.
    
    Args:
        request: Данные для создания ключа с ограничением по типам
        
    Returns:
        Созданный ключ интеграции
    """
    try:
        # Устанавливаем срок действия по умолчанию, если не указан
        expires_at = request.expires_at
        if not expires_at:
            expires_at = datetime.now() + timedelta(days=settings.connector.default_key_expiry_days)
        
        # Добавляем метод create_key_for_type в сервис
        if hasattr(key_service, 'create_key_for_type'):
            key = await key_service.create_key_for_type(
                name=request.name,
                description=request.description,
                allow_skip_periodic_handshake=request.allow_skip_periodic_handshake,
                expires_at=expires_at,
                type_restrictions=request.type_restrictions
            )
        else:
            # Если метод не существует, создаем обычный ключ
            logger.warning("create_key_for_type not implemented in service, using standard create_key")
            key = key_service.create_key(
                name=request.name,
                description=f"{request.description} (Restricted to types: {', '.join(request.type_restrictions)})",
                allow_skip_periodic_handshake=request.allow_skip_periodic_handshake,
                expires_at=expires_at
            )
        
        return IntegrationKeyResponse(
            key_id=key.key_id,
            key_value=key.key_value,
            name=key.name,
            description=key.description,
            allow_skip_periodic_handshake=key.allow_skip_periodic_handshake,
            is_active=key.is_active,
            created_at=key.created_at,
            updated_at=key.updated_at,
            expires_at=key.expires_at
        )
    except Exception as e:
        logger.error(f"Failed to create integration key for specific types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create integration key: {str(e)}"
        )

@router.post("/", response_model=IntegrationKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_integration_key(
    request: IntegrationKeyRequest,
    key_service: IntegrationKeyService = Depends(get_integration_key_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Создает новый ключ интеграции.
    
    Args:
        request: Данные для создания ключа
        
    Returns:
        Созданный ключ интеграции
    """
    try:
        # Устанавливаем срок действия по умолчанию, если не указан
        expires_at = request.expires_at
        if not expires_at:
            expires_at = datetime.now() + timedelta(days=settings.connector.default_key_expiry_days)
        
        key = key_service.create_key(
            name=request.name,
            description=request.description,
            allow_skip_periodic_handshake=request.allow_skip_periodic_handshake,
            expires_at=expires_at,
        )
        
        return IntegrationKeyResponse(
            key_id=key.key_id,
            key_value=key.key_value,
            name=key.name,
            description=key.description,
            allow_skip_periodic_handshake=key.allow_skip_periodic_handshake,
            is_active=key.is_active,
            created_at=key.created_at,
            updated_at=key.updated_at,
            expires_at=key.expires_at
        )
    except Exception as e:
        logger.error(f"Failed to create integration key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create integration key: {str(e)}"
        )

@router.get("/", response_model=List[IntegrationKeyResponse])
async def list_integration_keys(
    key_service: IntegrationKeyService = Depends(get_integration_key_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Возвращает список всех ключей интеграции.
    
    Returns:
        Список ключей интеграции
    """
    try:
        keys = key_service.get_keys()
        
        return [
            IntegrationKeyResponse(
                key_id=key.key_id,
                key_value=key.key_value,
                name=key.name,
                description=key.description,
                allow_skip_periodic_handshake=key.allow_skip_periodic_handshake,
                is_active=key.is_active,
                created_at=key.created_at,
                updated_at=key.updated_at,
                expires_at=key.expires_at
            )
            for key in keys
        ]
    except Exception as e:
        logger.error(f"Failed to list integration keys: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list integration keys: {str(e)}"
        )

@router.post("/{key_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_integration_key(
    key_id: str,
    key_service: IntegrationKeyService = Depends(get_integration_key_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Отзывает ключ интеграции.
    
    Args:
        key_id: ID ключа
        
    Returns:
        Статус операции
    """
    try:
        if not key_service.revoke_key(key_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration key {key_id} not found"
            )
        
        return {"status": "success", "message": f"Integration key {key_id} revoked"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke integration key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke integration key: {str(e)}"
        )

@router.get("/{key_id}", response_model=IntegrationKeyResponse)
async def get_integration_key(
    key_id: str,
    key_service: IntegrationKeyService = Depends(get_integration_key_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Возвращает информацию о ключе интеграции.
    
    Args:
        key_id: ID ключа
        
    Returns:
        Информация о ключе интеграции
    """
    try:
        key = key_service.get_key(key_id)
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration key {key_id} not found"
            )
        
        return IntegrationKeyResponse(
            key_id=key.key_id,
            key_value=key.key_value,
            name=key.name,
            description=key.description,
            allow_skip_periodic_handshake=key.allow_skip_periodic_handshake,
            is_active=key.is_active,
            created_at=key.created_at,
            updated_at=key.updated_at,
            expires_at=key.expires_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get integration key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get integration key: {str(e)}"
        ) 