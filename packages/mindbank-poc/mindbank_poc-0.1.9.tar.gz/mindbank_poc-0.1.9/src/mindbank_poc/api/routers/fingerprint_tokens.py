from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from mindbank_poc.api.schemas import FingerprintTokenRequest, FingerprintTokenResponse
from mindbank_poc.core.services.fingerprint_token_service import get_fingerprint_token_service, FingerprintTokenService
from mindbank_poc.core.services.auth_service import verify_admin_auth
from mindbank_poc.core.models.fingerprint_token import FingerprintTokenType
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

router = APIRouter(
    prefix="/fingerprint-tokens",
    tags=["Fingerprint Tokens"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=FingerprintTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_fingerprint_token(
    request: FingerprintTokenRequest,
    token_service: FingerprintTokenService = Depends(get_fingerprint_token_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Создать новый fingerprint-токен.
    
    Требуется административная авторизация через X-Admin-API-Key.
    """
    try:
        # Устанавливаем срок действия по умолчанию, если не указан
        expires_at = request.expires_at
        if not expires_at:
            expires_at = datetime.now() + timedelta(days=settings.connector.default_key_expiry_days)
        
        # Создаем токен
        token = token_service.create_token(
            name=request.name,
            description=request.description,
            token_type=FingerprintTokenType(request.token_type),
            allowed_archetypes=request.allowed_archetypes or [],
            allowed_connector_ids=request.allowed_connector_ids or [],
            allowed_connector_types=request.allowed_connector_types or [],
            expires_at=expires_at,
            created_by="admin"  # TODO: реальный пользователь
        )
        
        return FingerprintTokenResponse(**token.model_dump())
    except Exception as e:
        logger.error(f"Failed to create fingerprint token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create fingerprint token: {str(e)}"
        )

@router.get("/", response_model=List[FingerprintTokenResponse])
async def list_fingerprint_tokens(
    token_type: Optional[str] = None,
    archetype: Optional[str] = None,
    connector_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    token_service: FingerprintTokenService = Depends(get_fingerprint_token_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Получить список fingerprint-токенов с фильтрами.
    
    Требуется административная авторизация через X-Admin-API-Key.
    """
    try:
        # Приводим token_type к перечислению, если указан
        token_type_enum = None
        if token_type:
            token_type_enum = FingerprintTokenType(token_type)
        
        # Получаем токены с фильтрацией
        tokens = token_service.list_tokens(token_type=token_type_enum, archetype=archetype, connector=connector_id)
        
        # Фильтруем по is_active, если указан
        if is_active is not None:
            tokens = [token for token in tokens if token.is_active == is_active]
        
        return [FingerprintTokenResponse(**token.model_dump()) for token in tokens]
    except Exception as e:
        logger.error(f"Failed to list fingerprint tokens: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list fingerprint tokens: {str(e)}"
        )

@router.get("/{token_id}", response_model=FingerprintTokenResponse)
async def get_fingerprint_token(
    token_id: str,
    token_service: FingerprintTokenService = Depends(get_fingerprint_token_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Получить fingerprint-токен по ID.
    
    Требуется административная авторизация через X-Admin-API-Key.
    """
    token = token_service.get_token(token_id)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fingerprint token {token_id} not found"
        )
    
    return FingerprintTokenResponse(**token.model_dump())

@router.post("/{token_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_fingerprint_token(
    token_id: str,
    token_service: FingerprintTokenService = Depends(get_fingerprint_token_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Отозвать fingerprint-токен.
    
    Требуется административная авторизация через X-Admin-API-Key.
    """
    if not token_service.revoke_token(token_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fingerprint token {token_id} not found"
        )
    
    return {"status": "success", "message": f"Fingerprint token {token_id} revoked"}

@router.patch("/{token_id}", response_model=FingerprintTokenResponse)
async def update_fingerprint_token(
    token_id: str,
    request: FingerprintTokenRequest,
    token_service: FingerprintTokenService = Depends(get_fingerprint_token_service),
    _: bool = Depends(verify_admin_auth)
):
    """
    Обновить fingerprint-токен.
    
    Требуется административная авторизация через X-Admin-API-Key.
    """
    try:
        # Создаем словарь с обновлениями на основе request
        updates = {}
        if request.name:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.token_type:
            updates["token_type"] = FingerprintTokenType(request.token_type)
        if request.allowed_archetypes is not None:
            updates["allowed_archetypes"] = request.allowed_archetypes
        if request.allowed_connector_ids is not None:
            updates["allowed_connector_ids"] = request.allowed_connector_ids
        if request.allowed_connector_types is not None:
            updates["allowed_connector_types"] = request.allowed_connector_types
        if request.expires_at is not None:
            updates["expires_at"] = request.expires_at
        
        # Обновляем токен
        token = token_service.update_token(token_id, **updates)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fingerprint token {token_id} not found"
            )
        
        return FingerprintTokenResponse(**token.model_dump())
    except Exception as e:
        logger.error(f"Failed to update fingerprint token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update fingerprint token: {str(e)}"
        ) 