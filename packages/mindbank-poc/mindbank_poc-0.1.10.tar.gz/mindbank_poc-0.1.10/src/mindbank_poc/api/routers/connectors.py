from fastapi import APIRouter, HTTPException, status, Depends, Path, Body, Header
from typing import List, Optional, Dict, Any

from mindbank_poc.api.schemas import (
    ConnectorRegistrationRequest, ConnectorRegistrationResponse, 
    ConnectorHandshakeResponse, ConnectorConfigUpdate, 
    ConnectorToggle, ConnectorResponse, DynamicOptionsUpdate,
    ConnectorArchetypesUpdate
)
from mindbank_poc.core.connectors.service import get_connector_service, ConnectorService
from mindbank_poc.core.models.connector import Connector, ConnectorStage
from mindbank_poc.core.services.auth_service import verify_admin_auth
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.common.types import RawEntry

router = APIRouter(
    prefix="/connectors",
    tags=["Connectors"],
)

logger = get_logger(__name__)

async def verify_connector_token(
    connector_id: str = Path(..., description="ID коннектора"),
    authorization: str = Header(..., description="Токен доступа коннектора в формате 'Bearer TOKEN'"),
    connector_service: ConnectorService = Depends(get_connector_service)
) -> Connector:
    print(f"[VERIFY_CONNECTOR_TOKEN_DEBUG] connector_id: {connector_id}, authorization: {authorization}")
    """
    Зависимость для проверки токена доступа коннектора.
    
    Args:
        connector_id: ID коннектора
        authorization: Заголовок с токеном доступа
        connector_service: Сервис коннекторов
        
    Returns:
        Объект коннектора, если авторизация успешна
        
    Raises:
        HTTPException: Если авторизация не удалась
    """
    # Извлекаем токен из заголовка
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer TOKEN'"
        )
    token = authorization.split(" ")[1]
    
    is_valid = await connector_service.verify_any_token(connector_id, token)
    if not is_valid:
        # Проверяем токен, включая предыдущие токены
        is_valid = verify_admin_auth(token)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )
    # Получаем объект коннектора
    connector = await connector_service.get_connector(connector_id)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector {connector_id} not found"
        )
    return connector

@router.post("/register", response_model=ConnectorRegistrationResponse, status_code=status.HTTP_200_OK)
async def register_connector(
    request: ConnectorRegistrationRequest,
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Регистрирует новый коннектор в системе.
    
    Args:
        request: Данные для регистрации коннектора
        
    Returns:
        Информация о зарегистрированном коннекторе
    """
    # Проверяем обязательные поля в метаданных
    if "version" not in request.metadata or "description" not in request.metadata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metadata must contain at least 'version' and 'description' fields"
        )
    
    try:
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Received request.config: {request.config}") # Отладочный лог
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Received request.skip_periodic_handshake: {request.skip_periodic_handshake}") # Отладочный лог
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Received request.setup_details: {request.setup_details}") # Отладочный лог
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Received request.dynamic_options: {request.dynamic_options}") # Отладочный лог

        connector = await connector_service.register_connector(
            type=request.type,
            metadata=request.metadata,
            config_schema=request.config_schema,
            integration_key=request.integration_key,
            capabilities=request.capabilities,
            passed_initial_config=request.config,
            skip_periodic_handshake=request.skip_periodic_handshake,
            setup_details=request.setup_details.model_dump() if request.setup_details else None,
            dynamic_options=request.dynamic_options,
            supported_archetypes=request.supported_archetypes
        )
        
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Connector object from service: id={connector.connector_id}, config={connector.config}, stage={connector.stage}")

        # Формируем setup_url_resolved для ответа, если нужно
        setup_url_resolved = None
        if connector.setup_url:
            setup_url_resolved = connector.setup_url.replace("{connector_id}", connector.connector_id)
            
        response_payload = ConnectorRegistrationResponse(
            connector_id=connector.connector_id,
            access_token=connector.access_token,
            config=connector.config.copy() if connector.config is not None else {},
            stage=connector.stage,
            setup_url_resolved=setup_url_resolved
        )
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Response payload (Pydantic object): {response_payload}")
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Response payload model_dump(): {response_payload.model_dump()}")
        logger.info(f"[ROUTER_REGISTER_CONNECTOR] Response payload model_dump(mode='json'): {response_payload.model_dump(mode='json')}")
        return response_payload.model_dump()
    except ValueError as e:
        logger.warning(f"Invalid registration request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to register connector: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register connector"
        )

@router.get("/{connector_id}/handshake", response_model=ConnectorHandshakeResponse)
async def connector_handshake(
    connector_id: str = Path(..., description="ID коннектора"),
    authorization: str = Header(..., description="Токен доступа коннектора в формате 'Bearer TOKEN'"),
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Обрабатывает handshake запрос от коннектора.
    
    Args:
        connector_id: ID коннектора
        authorization: Заголовок авторизации с токеном
        
    Returns:
        Статус коннектора и конфигурация (если требуется)
    """
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer TOKEN'"
            )
        print(f"connector_handshake: authorization = {authorization}")
        token = authorization.split(" ")[1]
        
        try:
            is_valid = await connector_service.verify_any_token(connector_id, token)
            if not is_valid:
                # Логгируем перед выбросом исключения, чтобы видеть, какой токен был невалиден
                logger.warning(f"connector_handshake: Invalid token provided for connector {connector_id}. Token: {token[:10]}..."
                               f" Current: { (await connector_service.get_connector(connector_id)).access_token[:10] if await connector_service.get_connector(connector_id) else 'N/A' }..."
                               f" Previous: { (await connector_service.get_connector(connector_id)).previous_token[:10] if await connector_service.get_connector(connector_id) and (await connector_service.get_connector(connector_id)).previous_token else 'N/A' }...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token"
                )
            
            handshake_data_dict = await connector_service.handle_handshake(connector_id, token)
            # logger.info(f"[ROUTER_HANDSHAKE_DEBUG] Data from service (handshake_data_dict): {handshake_data_dict}")
            
            response_obj = ConnectorHandshakeResponse(**handshake_data_dict)
            # logger.info(f"[ROUTER_HANDSHAKE_DEBUG] Pydantic response_obj created. Direct field access response_obj.auth_token: {response_obj.auth_token}")
            # logger.info(f"[ROUTER_HANDSHAKE_DEBUG] Pydantic response_obj.model_dump(mode='json'): {response_obj.model_dump(mode='json')}")
            
            return response_obj
        except ValueError as e:
            logger.warning(f"Handshake failed for connector {connector_id}: {e}")
            status_code = status.HTTP_401_UNAUTHORIZED if "token" in str(e).lower() else status.HTTP_404_NOT_FOUND
            raise HTTPException(status_code=status_code, detail=str(e))
    except HTTPException as http_exc:
        # Пробрасываем HTTP исключения как есть
        raise http_exc
    except Exception as e:
        # Логируем любые другие ошибки и возвращаем 500
        logger.error(f"Handshake error for connector {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process handshake"
        )

@router.post("/{connector_id}/data", response_model=ConnectorResponse)
async def submit_connector_data(
    data: Any = Body(..., description="Данные от коннектора (RawEntry или массив RawEntry)"),
    connector: Connector = Depends(verify_connector_token),
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Принимает данные от коннектора.
    
    Args:
        data: Данные от коннектора (RawEntry или массив RawEntry)
        connector: Объект коннектора (получен через зависимость verify_connector_token)
        
    Returns:
        Статус обработки данных
    """
    connector_id = connector.connector_id # Получаем ID из объекта коннектора
    logger.info(f"[SUBMIT_DATA_DEBUG] For connector {connector_id}: stage={connector.stage}, enabled={connector.enabled}, config_valid={connector.config_validation.valid}")
    
    can_push = await connector_service.verify_can_push_data(connector_id)
    logger.info(f"[SUBMIT_DATA_DEBUG] verify_can_push_data returned: {can_push}")
    if not can_push:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Connector {connector_id} is not ready for data submission: stage={connector.stage}, enabled={connector.enabled}, config_valid={connector.config_validation.valid}"
        )
    
    # Импортируем только схемы из ingest модуля
    from mindbank_poc.api.schemas import RawEntryInput, AggregateInput
    # Импортируем backend напрямую
    from mindbank_poc.api.backends import jsonl_backend
    # Получаем буфер через функцию, а не инжекцию зависимости
    from mindbank_poc.api.routers.ingest import get_buffer
    
    try:
        # Получаем экземпляр буфера
        buffer = await get_buffer()
        
        # Обрабатываем данные в зависимости от их формата
        # Если это массив записей, обрабатываем как агрегат
        if isinstance(data, list):
            # Создаем агрегат из массива записей
            if len(data) > 0:
                # Используем group_id от первой записи, если она есть
                group_id = data[0].get("group_id", connector_id)
                
                # Дополняем метаданные данными о коннекторе
                for entry_payload in data:
                    if "metadata" not in entry_payload:
                        entry_payload["metadata"] = {}
                    
                    # Добавляем информацию о коннекторе в метаданные
                    entry_payload["metadata"]["connector_id"] = connector_id
                    entry_payload["metadata"]["connector_type"] = connector.type
                
                # Преобразуем в AggregateInput
                aggregate = AggregateInput(
                    group_id=group_id,
                    entries=[RawEntryInput(**entry_payload) for entry_payload in data],
                    metadata={"connector_id": connector_id, "connector_type": connector.type}
                )
                
                # Сохраняем агрегат
                await jsonl_backend.save_aggregate(aggregate)
                
                # Также сохраняем каждую запись отдельно
                for entry_schema in aggregate.entries:
                    raw_entry = RawEntry(**entry_schema.model_dump())
                    await buffer.add_entry(raw_entry)
            
        # Если это одиночная запись, обрабатываем как raw entry
        else:
            # Дополняем метаданные данными о коннекторе
            if "metadata" not in data:
                data["metadata"] = {}
            
            data["metadata"]["connector_id"] = connector_id
            data["metadata"]["connector_type"] = connector.type
            
            # Преобразуем в RawEntryInput и сохраняем
            entry_input = RawEntryInput(**data)
            await jsonl_backend.save_raw_entry(entry_input)
            
            # Преобразуем в RawEntry и добавляем в буфер
            raw_entry = RawEntry(**entry_input.model_dump())
            await buffer.add_entry(raw_entry)
        
        logger.info(f"Processed data from connector {connector_id}")
        return ConnectorResponse(status="accepted")
    
    except Exception as e:
        logger.error(f"Error processing data from connector {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process data"
        )

@router.patch("/{connector_id}", response_model=ConnectorResponse)
async def update_connector_config(
    connector_id: str,
    config_update: ConnectorConfigUpdate,
    connector_service: ConnectorService = Depends(get_connector_service),
    _: str = Depends(verify_admin_auth)
):
    """
    Обновляет полную конфигурацию коннектора.
    
    Args:
        connector_id: ID коннектора
        config_update: Новая конфигурация
        
    Returns:
        Статус обновления
    """
    try:
        await connector_service.update_connector_config(connector_id, config_update.config)
        return ConnectorResponse(
            status="success", 
            message=f"Configuration for connector {connector_id} updated. New access token generated."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Update config error for {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update configuration"
        )

@router.post("/{connector_id}/config", response_model=ConnectorResponse)
async def set_connector_config_by_connector(
    new_config: Dict[str, Any] = Body(..., description="Полный объект конфигурации от коннектора"),
    connector: Connector = Depends(verify_connector_token),
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Устанавливает полную конфигурацию коннектора (обычно после этапа SETUP_REQUIRED).
    Вызывается самим коннектором.
    """
    connector_id = connector.connector_id
    
    try:
        # Вызываем новый или измененный метод в сервисе
        await connector_service.set_full_config_from_connector(connector_id, new_config)
        return ConnectorResponse(
            status="success", 
            message=f"Full configuration for connector {connector_id} set successfully."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Set full config error for {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set full configuration"
        )

@router.post("/{connector_id}/reset-config", response_model=ConnectorResponse)
async def reset_config(
    connector: Connector = Depends(verify_connector_token),
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Сбрасывает конфигурацию коннектора и переводит его в этап configuration.
    
    Args:
        connector: Объект коннектора (получен через зависимость verify_connector_token)
        
    Returns:
        Статус операции
    """
    # Получаем ID из объекта коннектора
    connector_id = connector.connector_id
    print(f"[RESET_CONFIG] connector_id = {connector_id}")
    try:
        await connector_service.reset_config(connector_id)
        return ConnectorResponse(
            status="success", 
            message=f"Configuration for connector {connector_id} reset. Connector is now in configuration stage."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Reset config error for {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset configuration"
        )

@router.post("/{connector_id}/reset-setup", response_model=ConnectorResponse)
async def reset_setup(
    connector: Connector = Depends(verify_connector_token),
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Сбрасывает настройку коннектора и переводит его в этап setup.
    
    Args:
        connector: Объект коннектора (получен через зависимость verify_connector_token)
        
    Returns:
        Статус операции
    """
    # Получаем ID из объекта коннектора
    connector_id = connector.connector_id
    
    try:
        await connector_service.reset_setup(connector_id)
        return ConnectorResponse(
            status="success", 
            message=f"Setup for connector {connector_id} reset. Connector is now in setup stage and disabled."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Reset setup error for {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset setup"
        )

@router.post("/{connector_id}/toggle", response_model=ConnectorResponse)
async def toggle_connector(
    connector_id: str,
    toggle_data: ConnectorToggle,
    connector_service: ConnectorService = Depends(get_connector_service),
    _: str = Depends(verify_admin_auth)
):
    """
    Включает или отключает коннектор.

    Args:
        connector_id: ID коннектора
        toggle_data: Данные для изменения статуса активности

    Returns:
        Статус операции
    """
    try:
        await connector_service.toggle_connector(connector_id, toggle_data.enabled)
        return ConnectorResponse(
            status="success",
            message=f"Connector {connector_id} {'enabled' if toggle_data.enabled else 'disabled'}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/{connector_id}/archetypes", response_model=ConnectorResponse)
async def update_connector_archetypes(
    connector_id: str,
    archetypes_update: ConnectorArchetypesUpdate,
    connector_service: ConnectorService = Depends(get_connector_service),
    _: str = Depends(verify_admin_auth)
):
    """
    Обновляет список поддерживаемых архитипов коннектора.
    
    Args:
        connector_id: ID коннектора
        archetypes_update: Новый список поддерживаемых архитипов
        
    Returns:
        Статус операции
    """
    try:
        await connector_service.update_connector_archetypes(connector_id, archetypes_update.supported_archetypes)
        
        return ConnectorResponse(
            status="success", 
            message=f"Supported archetypes for connector {connector_id} updated successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Toggle connector error for {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle connector"
        )

@router.get("/", response_model=List[Connector])
async def list_connectors(
    connector_service: ConnectorService = Depends(get_connector_service),
    _: str = Depends(verify_admin_auth)
):
    """
    Возвращает список всех зарегистрированных коннекторов.
    
    Returns:
        Список коннекторов
    """
    connectors = await connector_service.get_all_connectors()
    # Добавляем поле id для совместимости с фронтом (React key)
    result = []
    for c in connectors:
        data = c.model_dump(mode='json')
        data['id'] = data.get('connector_id')
        result.append(data)
    return result

@router.get("/{connector_id}", response_model=Dict[str, Any])
async def get_connector(
    connector_id: str,
    connector_service: ConnectorService = Depends(get_connector_service),
    _: dict = Depends(verify_admin_auth)
):
    """
    Получить детальную информацию о коннекторе.
    Только админский доступ.
    
    Args:
        connector_id: ID коннектора
        
    Returns:
        JSON с данными коннектора
    """
    connector = await connector_service.get_connector(connector_id)
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector {connector_id} not found"
        )
    
    # Отладочный лог для инспекции config
    logger.info(f"[DEBUG_GET_CONNECTOR] connector.config = {connector.config}")
    logger.info(f"[DEBUG_GET_CONNECTOR] connector.config class = {connector.config.__class__}")
    
    # В Pydantic v2 используем model_dump для сериализации
    # Включаем все поля, включая те, что не заданы (exclude_unset=False)
    connector_data = connector.model_dump(mode='json')
    
    # Дополнительная проверка конфига после сериализации
    logger.info(f"[DEBUG_GET_CONNECTOR] connector_data['config'] = {connector_data.get('config')}")
    logger.info(f"[DEBUG_GET_CONNECTOR] connector_data['config'] class = {connector_data.get('config').__class__ if connector_data.get('config') is not None else None}")
    
    return connector_data

@router.get("/{connector_id}/dynamic-options", response_model=Dict[str, Any])
async def get_connector_dynamic_options(
    connector: Connector = Depends(verify_connector_token),
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Получает динамические опции коннектора
    
    Args:
        connector: Объект коннектора (получен через зависимость verify_connector_token)
        
    Returns:
        Словарь с динамическими опциями коннектора
    """
    # Получаем ID из объекта коннектора
    connector_id = connector.connector_id
    
    # Проверяем наличие динамических опций
    if not connector.dynamic_options:
        logger.warning(f"No dynamic options available for connector {connector_id}")
        return {}
    
    # Логируем и возвращаем динамические опции
    logger.info(f"Retrieved dynamic options for connector {connector_id}")
    return {
        "dynamic_options": connector.dynamic_options,
        "updated_at": connector.dynamic_options_updated_at,
    }

@router.post("/{connector_id}/dynamic-options", response_model=ConnectorResponse)
async def update_connector_dynamic_options(
    update: DynamicOptionsUpdate,
    connector: Connector = Depends(verify_connector_token),
    connector_service: ConnectorService = Depends(get_connector_service)
):
    """
    Обновляет динамические опции коннектора
    
    Args:
        update: Новые динамические опции и, опционально, новая схема
        connector: Объект коннектора (получен через зависимость verify_connector_token)
        
    Returns:
        Статус обновления
    """
    # Получаем ID из объекта коннектора
    connector_id = connector.connector_id
    
    try:
        # Обновляем динамические опции
        connector.update_dynamic_options(
            new_options=update.dynamic_options,
            new_schema=update.new_config_schema
        )
        
        # Обновляем коннектор в хранилище
        await connector_service.update_connector(connector)
        
        logger.info(f"Updated dynamic options for connector {connector_id}")
        return ConnectorResponse(
            status="success",
            message=f"Dynamic options for connector {connector_id} updated successfully"
        )
    except Exception as e:
        logger.error(f"Failed to update dynamic options for connector {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update dynamic options: {str(e)}"
        )


@router.post("/{connector_id}/integration-key", response_model=Dict[str, str])
async def generate_connector_integration_key(
    connector_id: str,
    connector_service: ConnectorService = Depends(get_connector_service),
    _: str = Depends(verify_admin_auth)
):
    """
    Генерирует новый интеграционный ключ для указанного коннектора.
    
    Args:
        connector_id: ID коннектора
        
    Returns:
        Новый интеграционный ключ
    """
    try:
        # Проверяем существование коннектора
        connector = await connector_service.get_connector(connector_id)
        if not connector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Connector {connector_id} not found"
            )
        
        # Получаем тип коннектора для генерации ключа
        connector_type = connector.type
        
        # Запрашиваем сервис интеграционных ключей
        from mindbank_poc.core.services.integration_key_service import get_integration_key_service
        integration_key_service = get_integration_key_service()
        
        # Создаем название и описание для ключа
        key_name = f"Key for {connector_type} ({connector_id})"
        key_description = f"Auto-generated key for connector {connector_id} (type: {connector_type})"
        
        # Проверяем, есть ли метод create_key_for_type, иначе используем стандартный create_key
        integration_key = None
        try:
            if hasattr(integration_key_service, 'create_key_for_type'):
                logger.info(f"Using create_key_for_type for connector {connector_id}")
                integration_key = await integration_key_service.create_key_for_type(
                    name=key_name,
                    description=key_description,
                    allow_skip_periodic_handshake=False,
                    type_restrictions=[connector_type]
                )
            else:
                logger.info(f"Method create_key_for_type not found, using standard create_key for connector {connector_id}")
                integration_key = integration_key_service.create_key(
                    name=key_name,
                    description=key_description,
                    allow_skip_periodic_handshake=False
                )
        except Exception as key_error:
            logger.error(f"Error calling key generation method: {key_error}", exc_info=True)
            # Если возникла ошибка в специализированном методе, пробуем стандартный
            if hasattr(integration_key_service, 'create_key_for_type') and integration_key is None:
                logger.info(f"Falling back to standard create_key for connector {connector_id}")
                integration_key = integration_key_service.create_key(
                    name=key_name,
                    description=key_description,
                    allow_skip_periodic_handshake=False
                )
        
        # Проверка на успешное создание ключа
        if not integration_key:
            raise ValueError("Failed to generate integration key - key generation method returned None")
        
        logger.info(f"Generated new integration key for connector {connector_id}")
        
        # Возвращаем только ключ в формате, который ожидает Hub
        return {
            "integration_key": integration_key.key_value
        }
    except HTTPException:
        # Пробрасываем HTTP исключения дальше
        raise
    except ValueError as ve:
        logger.error(f"Value error in integration key generation for connector {connector_id}: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Failed to generate integration key for connector {connector_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate integration key: {str(e)}"
        )
