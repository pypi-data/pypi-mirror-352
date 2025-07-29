import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import uuid
from pathlib import Path
import aiofiles
from fastapi import HTTPException
from mindbank_poc.core.models.connector import (
    Connector, ConnectorStage, ConfigValidation, 
    ConnectorMessage
)
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings
from mindbank_poc.core.services.integration_key_service import get_integration_key_service
# from mindbank_poc.api.schemas import SetupDetails # Этот импорт больше не нужен здесь, так как setup_details передается как dict

# Added imports
from mindbank_poc.core.connectors.schemas_onboarding import (
    ConnectorOnboardingState as OnboardingState, # Импортируем и переименовываем
    OnboardingStepInfo,
    StepSubmissionPayload,
    StepSubmissionResult,
    ConnectorDirectiveActionType,
    ConnectorDirective,
    ConnectorFSMUpdateStatus,
    ConnectorFSMUpdate,
)
from mindbank_poc.core.connectors.onboarding_repository import OnboardingStateRepository
# End of added imports

logger = get_logger(__name__)

class ConnectorService:
    """
    Сервис для управления коннекторами.
    Хранит информацию о коннекторах и их этапах, обрабатывает запросы коннекторов.
    """
    
    def __init__(self, 
                 onboarding_repo: OnboardingStateRepository,
                 storage_path: Optional[str] = None, 
                 check_interval_seconds: Optional[int] = None,
                 max_silence_minutes: Optional[int] = None):
        self._onboarding_repo = onboarding_repo
        self.storage_path = Path(storage_path or settings.connector.storage_path)
        self.connectors: Dict[str, Connector] = {}
        self.check_interval_seconds = check_interval_seconds or settings.connector.check_interval_seconds
        self.max_silence_seconds = (max_silence_minutes or settings.connector.max_silence_minutes) * 60
        self._checker_task = None
        
        # Field to store last known step definition provided by connector
        # This could also be part of ConnectorOnboardingState if preferred for persistence
        # For simplicity here, let's assume ConnectorOnboardingState.onboarding_context can store it.
        # Example key: onboarding_context["last_provided_step_info_by_connector"]
        # Example key: onboarding_context["pending_user_submission_for_connector"]
        # Example key: onboarding_context["dynamic_config_refresh_needed"]
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ConnectorService initialized with settings: "
                   f"polling_interval={settings.connector.polling_interval_seconds}s, "
                   f"max_silence={settings.connector.max_silence_minutes}m, "
                   f"check_interval={settings.connector.check_interval_seconds}s")
    
    async def start(self):
        if self._checker_task is None:
            await self._load_connectors()
            self._checker_task = asyncio.create_task(self._check_timeouts())
            logger.info("Connector service started and connectors loaded")
    
    async def stop(self):
        if self._checker_task:
            self._checker_task.cancel()
            try:
                await self._checker_task
            except asyncio.CancelledError:
                pass
            self._checker_task = None
        await self._save_connectors()
        logger.info("Connector service stopped")
    
    async def register_connector(
        self, 
        type: str,
        metadata: Dict[str, Any],
                                 config_schema: Dict[str, Any], 
                                 integration_key: str,
                                 capabilities: Optional[List[str]] = None,
        passed_initial_config: Optional[Dict[str, Any]] = None,
                                 skip_periodic_handshake: bool = False,
        setup_details: Optional[Dict[str, Any]] = None,
        dynamic_options: Optional[Dict[str, Any]] = None,
        supported_archetypes: Optional[List[str]] = None
    ) -> Connector:
        """
        Регистрирует новый коннектор в системе.
        
        Args:
            type: Тип коннектора (уникальный идентификатор типа)
            metadata: Метаданные коннектора (версия, описание и т.д.)
            config_schema: Схема конфигурации коннектора
            integration_key: Ключ интеграции для доступа
            capabilities: Список возможностей коннектора
            passed_initial_config: Начальная конфигурация (опционально)
            skip_periodic_handshake: Флаг для пропуска периодических handshake (опционально)
            setup_details: Детали настройки коннектора (опционально)
            dynamic_options: Динамические опции коннектора (опционально)
            
        Returns:
            Зарегистрированный объект коннектора
            
        Raises:
            ValueError: Если ключ интеграции невалиден
        """
        # Проверяем ключ интеграции
        key_service = get_integration_key_service()
        if not key_service.verify_key(integration_key):
            logger.warning(f"Attempt to register connector with invalid integration key")
            raise ValueError(f"Invalid integration key")
        
        key_object = key_service.get_key_by_value(integration_key)
        if skip_periodic_handshake and (not key_object or not key_object.allow_skip_periodic_handshake):
            logger.warning(f"Attempt to register connector with skip_periodic_handshake=True, but integration key doesn't allow it")
            raise ValueError("This integration key doesn't allow skipping periodic handshake")
        
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] passed_initial_config provided to service: {passed_initial_config}")
        config_to_set = passed_initial_config if passed_initial_config is not None else {}
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] config_to_set prepared: {config_to_set}")

        setup_details_obj = None
        if setup_details:
            setup_details_obj = {
                "setup_url": setup_details.get("setup_url"),
                "setup_instructions": setup_details.get("setup_instructions")
            }
        
        connector = Connector(
            type=type,
            metadata=metadata,
            config_schema=config_schema,
            capabilities=capabilities or [],
            setup_url=setup_details_obj["setup_url"] if setup_details_obj else None,
            setup_instructions=setup_details_obj["setup_instructions"] if setup_details_obj else None,
            dynamic_options=dynamic_options or {},
            supported_archetypes=supported_archetypes or []
        )
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] Connector.config after direct assignment (before explicit set): {connector.config}")
        
        if config_to_set:
            connector.config = config_to_set.copy()
            logger.info(f"[REGISTER_CONNECTOR_DEBUG] connector.config explicitly set to (a copy of config_to_set): {connector.config}")
        elif passed_initial_config is not None and not config_to_set: 
             connector.config = {}.copy()
             logger.info(f"[REGISTER_CONNECTOR_DEBUG] connector.config explicitly set to an empty dict copy because passed_initial_config was {{}}")

        config_validation = connector.validate_config()
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] Validation result after potential config set: {config_validation.valid}, errors: {config_validation.errors}")
        
        if skip_periodic_handshake:
            if not config_validation.valid:
                raise ValueError("Cannot skip periodic handshake with invalid/missing initial_config when config_schema has requirements.")
            if setup_details_obj and setup_details_obj.get("setup_url"):
                logger.warning(f"Connector {type} registered with skip_periodic_handshake=True and valid initial_config, "
                               f"but also provided setup_details. Setup_details will be IGNORED and stage set to READY.")
            stage = ConnectorStage.READY
        elif setup_details_obj:
            stage = ConnectorStage.SETUP_REQUIRED
            print(f"[REGISTER_CONNECTOR_DEBUG] Stage set to SETUP_REQUIRED because setup_details_obj is provided: {stage}")
        else: 
            if config_validation.valid:
                stage = ConnectorStage.READY
            else:
                stage = ConnectorStage.CONFIGURATION
        
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] For connector type '{type}':")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG]   passed_initial_config: {passed_initial_config}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG]   config_to_set: {config_to_set}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG]   connector.config after potential set: {connector.config}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG]   config_validation.valid: {config_validation.valid}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG]   setup_details_obj: {setup_details_obj}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG]   skip_periodic_handshake: {skip_periodic_handshake}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG]   Determined stage: {stage}")
        
        connector.update_stage(stage)
        connector.config_validation = config_validation
        
        # Добавляем коннектор в словарь и сохраняем его
        self.connectors[connector.connector_id] = connector
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] Connector {connector.connector_id} added to self.connectors. Its config: {self.connectors[connector.connector_id].config}")
        
        # Обновляем динамические опции, если они предоставлены
        if dynamic_options:
            connector.dynamic_options = dynamic_options
            connector.dynamic_options_updated_at = datetime.now()
            
        # Если установлен флаг skip_periodic_handshake, запоминаем, чтобы
        # не проверять timeout для этого коннектора
        if skip_periodic_handshake:
            # Убедимся, что это set, если он еще не был инициализирован
            if not hasattr(self, 'skip_periodic_handshake_connectors'):
                self.skip_periodic_handshake_connectors = set()
            self.skip_periodic_handshake_connectors.add(connector.connector_id)
        
        # Создаем структуру FSM для онбординга, если коннектор требует сложной настройки
        if stage == ConnectorStage.SETUP_REQUIRED:
            # Создаем запись в OnboardingStateRepository
            state = OnboardingState(
                connector_id=uuid.UUID(connector.connector_id),
                is_completed=False,
                onboarding_context={},
                current_step_id="AWAITING_ONBOARD_START"
            )
            await self._onboarding_repo.save_state(state)
        
        # Сохраняем в хранилище
        await self._save_connectors()
        
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] Final config in connector obj: {connector.config}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] Stage set in new Connector: {connector.stage}")
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] Config_validation set in new Connector: {connector.config_validation.model_dump()}")

        logger.info(f"Connector {connector.connector_id} ({type}) registered. Stage: {connector.stage}")
        
        logger.info(f"[REGISTER_CONNECTOR_DEBUG] Returning original connector object: {connector.model_dump(mode='json')}") # Логируем то, что возвращаем
        return connector # Возвращаем оригинальный, измененный объект
    
    async def handle_handshake(self, connector_id: str, token: str) -> Dict[str, Any]:
        connector = await self.get_connector(connector_id)
        if not connector:
            raise ValueError("Коннектор не найден")
        # logger.info(f"[HANDLE_HANDSHAKE_DEBUG] Initial connector.config for {connector_id}: {connector.config}")

        # Проверяем, является ли токен текущим или предыдущим
        is_current_token = connector.verify_token(token)
        is_previous_token = connector.previous_token and token == connector.previous_token
        
        # Общая проверка на валидность токена
        if not (is_current_token or is_previous_token):
                raise ValueError("Неверный токен доступа")
        
        connector.record_handshake()
        
        # Валидируем текущую конфигурацию при каждом handshake
        # logger.info(f"[HANDLE_HANDSHAKE_DEBUG] connector.config BEFORE validate_config: {connector.config}")
        connector.config_validation = connector.validate_config()
        # logger.info(f"[HANDLE_HANDSHAKE_DEBUG] connector.config AFTER validate_config: {connector.config}")
        # logger.info(f"[HANDLE_HANDSHAKE_DEBUG] connector.config_validation AFTER validate_config: {connector.config_validation.model_dump()}")
        
        await self._save_connectors() # Сохраняем last_handshake

        response_data = {
            "stage": connector.stage,
            "enabled": connector.enabled,
            "current_config": connector.config.copy() if connector.config is not None else {},
            "config_validation": connector.config_validation.model_dump(),
            "messages": [msg.model_dump() for msg in connector.messages],
            "capabilities": connector.capabilities,
        }

        if connector.setup_url:
            response_data["setup_url_resolved"] = connector.setup_url.replace("{connector_id}", connector.connector_id)

        if connector.stage == ConnectorStage.SETUP_REQUIRED and not any(msg.text.startswith("Пожалуйста, завершите настройку") for msg in connector.messages):
             connector.add_message("info", f"Пожалуйста, завершите настройку коннектора по адресу: {response_data.get('setup_url_resolved')}" if response_data.get('setup_url_resolved') else "Пожалуйста, завершите первоначальную настройку коннектора.")
             response_data["messages"] = [msg.model_dump() for msg in connector.messages]

        if is_previous_token:
            logger.info(f"[HANDLE_HANDSHAKE_DEBUG] Condition is_previous_token is TRUE for {connector_id}.")
            logger.info(f"[HANDLE_HANDSHAKE_DEBUG] Current connector.access_token to be returned as auth_token: {connector.access_token}")
            response_data["auth_token"] = connector.access_token # Используем alias напрямую как ключ

        connector.clear_messages()
        # logger.info(f"[HANDLE_HANDSHAKE_DEBUG] Final response_data before return: {response_data}")
        return response_data
    
    async def verify_connector_token(self, connector_id: str, token: str) -> bool:
        if connector_id not in self.connectors:
            return False
        connector = self.connectors[connector_id]
        return connector.verify_token(token)
    
    async def verify_any_token(self, connector_id: str, token: str) -> bool:
        if connector_id not in self.connectors:
            return False
        print(f"[VERIFY_ANY_TOKEN_DEBUG] connector_id: {connector_id}, token: {token}")
        connector = self.connectors[connector_id]
        is_current = connector.verify_token(token)
        is_previous = connector.previous_token and token == connector.previous_token
        logger.info(f"Token verification for {connector_id}:")
        logger.info(f"- Current token: {connector.access_token}")
        logger.info(f"- Previous token: {connector.previous_token}")
        logger.info(f"- Provided token: {token}")
        logger.info(f"- Is current: {is_current}, Is previous: {is_previous}, Final result: {is_current or is_previous}")
        return is_current or is_previous

    async def verify_can_push_data(self, connector_id: str) -> bool:
        if connector_id not in self.connectors:
            return False
        connector = self.connectors[connector_id]
        return (connector.stage == ConnectorStage.READY and 
                connector.enabled and 
                connector.config_validation.valid)
    
    async def update_connector_config(self, connector_id: str, new_config: Dict[str, Any]):
        connector = await self.get_connector(connector_id)
        if not connector:
            raise ValueError("Коннектор не найден")
        
        connector.update_config(new_config) # Этот метод генерирует новый токен и устанавливает previous_token
        
        validation_result = connector.validate_config()
        connector.config_validation = validation_result
        
        if validation_result.valid:
            # Если был SETUP_REQUIRED, и админ залил валидный конфиг, то READY
            # Также если был CONFIGURATION и стал валидным, то READY
            if connector.stage in [ConnectorStage.SETUP_REQUIRED, ConnectorStage.CONFIGURATION, ConnectorStage.READY, ConnectorStage.DISABLED]: # Разрешаем обновление конфига из любого состояния, если он валиден
                 if connector.enabled: # Если был disabled, но конфиг стал валидным, он не станет READY автоматически без toggle
                    connector.update_stage(ConnectorStage.READY)
        else:
            # Если конфиг стал невалидным, переводим в CONFIGURATION
            # (даже если был SETUP_REQUIRED, но админ залил невалидный конфиг)
            connector.update_stage(ConnectorStage.CONFIGURATION)
            
        await self._save_connectors()
        logger.info(f"Полная конфигурация для коннектора {connector_id} обновлена администратором. Stage: {connector.stage}")

    async def set_full_config_from_connector(self, connector_id: str, new_config: Dict[str, Any]) -> None:
        """
        Устанавливает полную конфигурацию коннектора (обычно когда коннектор сам сообщает о конфигурации).
        
        Args:
            connector_id: ID коннектора
            new_config: Новая конфигурация
            
        Raises:
            ValueError: Если коннектор не найден
        """
        # По сравнению с обычным метод обновления конфигурации, этот метод требует 
        # дополнительной проверки, что вызов исходит от самого коннектора
        # Такая проверка выполняется на уровне API путем проверки токена доступа коннектора
        
        connector = await self.get_connector(connector_id)
        if not connector:
            raise ValueError(f"Connector {connector_id} not found")
        
        # Обновляем конфигурацию коннектора
        connector.config = new_config
        
        # Обновляем токен доступа
        # connector.rotate_token()
        
        # Получаем состояние онбординга, если оно используется
        try:
            onboarding_state = await self._onboarding_repo.get_state(uuid.UUID(connector_id))
        except Exception as e:
            logger.warning(f"Error getting onboarding state for {connector_id}: {e}")
            onboarding_state = None
        
        # Валидируем новую конфигурацию
        validation_result = connector.validate_config()
        connector.config_validation = validation_result

        # Обновляем состояние коннектора на основе результатов валидации
        if validation_result.valid and connector.enabled:
                    connector.update_stage(ConnectorStage.READY)
        else:
            connector.update_stage(ConnectorStage.CONFIGURATION)
        
        # Если коннектор находится в этапе SETUP_REQUIRED, обрабатываем состояние онбординга
        if onboarding_state and not onboarding_state.is_completed:
            # Обновляем контекст онбординга
            onboarding_state.onboarding_context["config"] = new_config
            onboarding_state.is_completed = True
            await self._onboarding_repo.save_state(onboarding_state)
        
        # Сохраняем изменения коннектора
        await self._save_connectors()
        
        logger.info(f"Full configuration for connector {connector_id} set successfully. New stage: {connector.stage}")

    async def update_connector(self, connector: Connector) -> None:
        """
        Обновляет существующий коннектор в хранилище
        
        Args:
            connector: Объект коннектора для обновления
            
        Raises:
            ValueError: Если коннектор не существует
        """
        # Проверяем, существует ли коннектор с таким ID
        existing_connector = await self.get_connector(connector.connector_id)
        if not existing_connector:
            raise ValueError(f"Connector {connector.connector_id} not found")
        
        # Обновляем коннектор в словаре
        self.connectors[connector.connector_id] = connector
        
        # Сохраняем обновленный коннектор
        await self._save_connectors()
        
        logger.info(f"Connector {connector.connector_id} updated")

    async def update_partial_config(self, connector_id: str, partial_config: Dict[str, Any]):
        """Обновляет часть конфигурации или полную конфигурацию, если ключ не partial_config."""
        # Этот метод теперь может быть не нужен, если POST /config всегда шлет полную конфигурацию.
        # Или его можно оставить для внутреннего использования / админских частичных обновлений, если таковые понадобятся.
        # Пока что оставим его логику, но вызов из POST /config теперь идет в set_full_config_from_connector.
        connector = await self.get_connector(connector_id)
        
    async def update_connector_archetypes(self, connector_id: str, supported_archetypes: List[str]):
        """
        Обновляет список поддерживаемых архитипов коннектора.
        
        Args:
            connector_id: ID коннектора
            supported_archetypes: Новый список поддерживаемых архитипов
            
        Returns:
            Обновленный коннектор
            
        Raises:
            ValueError: Если коннектор не найден
        """
        connector = await self.get_connector(connector_id)
        if not connector:
            raise ValueError("Коннектор не найден")
            
        connector.supported_archetypes = supported_archetypes
        connector.updated_at = datetime.now()
        
        await self.update_connector(connector)
        return connector
        if not connector:
            raise ValueError("Коннектор не найден")

        is_full_config_submission = not ("partial_config" in partial_config and len(partial_config) == 1)
        config_to_apply = partial_config.get("partial_config", partial_config) if not is_full_config_submission else partial_config

        if is_full_config_submission:
            # Это трактуется как полная отправка конфигурации коннектором после setup_required
            connector.config = config_to_apply # Заменяем конфиг полностью
            logger.info(f"Коннектор {connector_id} отправил полную конфигурацию.")
        else:
            # Это частичное обновление, как и раньше
            connector.update_partial_config(config_to_apply)
            logger.info(f"Коннектор {connector_id} обновил часть конфигурации.")

        validation_result = connector.validate_config()
        connector.config_validation = validation_result

        if validation_result.valid:
            if connector.stage in [ConnectorStage.SETUP_REQUIRED, ConnectorStage.CONFIGURATION]:
                if connector.enabled: # Если коннектор был выключен, он не станет READY
                    connector.update_stage(ConnectorStage.READY)
            # Если уже был READY и конфиг остался валидным, stage не меняется
        else:
            connector.update_stage(ConnectorStage.CONFIGURATION)
            
        await self._save_connectors()
        logger.info(f"Конфигурация для коннектора {connector_id} обновлена. Stage: {connector.stage}, Valid: {validation_result.valid}")

    async def reset_config(self, connector_id: str):
        connector = await self.get_connector(connector_id)
        if not connector:
            raise ValueError("Коннектор не найден")
        
        connector.config = {} # Очищаем конфиг
        connector.config_validation = connector.validate_config() # Валидируем пустой конфиг

        # if connector.setup_instructions: # Если был setup_url, значит нужен полный ресетап
        #     connector.update_stage(ConnectorStage.SETUP_REQUIRED)
        # else: # Иначе просто ожидаем конфигурацию от админа
        connector.update_stage(ConnectorStage.CONFIGURATION)
        
        # connector.rotate_token()
        await self._save_connectors()
        logger.info(f"Конфигурация для {connector_id} сброшена. Stage: {connector.stage}")

    async def reset_setup(self, connector_id: str):
        connector = await self.get_connector(connector_id)
        if not connector:
            raise ValueError("Коннектор не найден")
        logger.info(f"[RESET_SETUP_DEBUG] Connector before reset: {connector}")
        connector.config = {}
        connector.config_validation = connector.validate_config()
        connector.enabled = False # Отключаем коннектор
        
        if connector.setup_instructions: # Если был setup_url, значит нужен полный ресетап
            print(1)
            connector.update_stage(ConnectorStage.SETUP_REQUIRED)
        else: # Иначе просто ожидаем конфигурацию от админа (setup stage был для старой логики шагов)
              # Теперь, если нет setup_url, то SETUP эквивалентен CONFIGURATION при пустом конфиге
            print(2)
            connector.update_stage(ConnectorStage.CONFIGURATION)
        print(f"CONNECTOR: {connector}")
        # connector.rotate_token()
        await self._save_connectors()
        logger.info(f"Полный сброс для {connector_id}. Stage: {connector.stage}, Enabled: {connector.enabled}")

    async def toggle_connector(self, connector_id: str, enabled: bool):
        connector = await self.get_connector(connector_id)
        if not connector:
            raise ValueError(f"Коннектор {connector_id} не найден")

        connector.toggle(enabled)
        
        if enabled and connector.stage != ConnectorStage.READY: 
            is_config_valid = connector.validate_config().valid
            if connector.setup_url:
                if is_config_valid:
                    # Если есть setup_url, но конфиг УЖЕ валиден (например, был установлен админом или коннектором во время DISABLED)
                    # то при включении он должен стать READY.
                    connector.update_stage(ConnectorStage.READY)
                else:
                    # Если есть setup_url и конфиг все еще не валиден, то SETUP_REQUIRED.
                    connector.update_stage(ConnectorStage.SETUP_REQUIRED)
            elif is_config_valid:
                # Если нет setup_url и конфиг валиден, то READY.
                connector.update_stage(ConnectorStage.READY)
            else:
                # Если нет setup_url и конфиг не валиден, то CONFIGURATION.
                connector.update_stage(ConnectorStage.CONFIGURATION)

        # Логирование состояний
        if enabled:
            logger.info(f"Connector {connector_id} enabled. New stage: {connector.stage}.")
            if connector.stage == ConnectorStage.SETUP_REQUIRED:
                 logger.info(f"Connector {connector_id} requires setup via {connector.setup_url} or instructions.")
            elif connector.stage == ConnectorStage.CONFIGURATION:
                 logger.info(f"Connector {connector_id} requires configuration.")
        else:
            logger.info(f"Connector {connector_id} disabled. Stage set to {connector.stage}.")

        await self._save_connectors()

    async def get_all_connectors(self) -> List[Connector]:
        return list(self.connectors.values())

    async def get_connector(self, connector_id: str) -> Optional[Connector]:
        return self.connectors.get(connector_id)

    async def _check_timeouts(self):
        while True:
            await asyncio.sleep(self.check_interval_seconds)
            now = datetime.now()
            for connector_id, connector in list(self.connectors.items()):
                if connector.enabled and connector.check_timeout(self.max_silence_seconds):
                    logger.warning(f"Connector {connector_id} timed out. Last handshake: {connector.last_handshake}. Disabling.")
                    connector.toggle(False) # Используем toggle для корректного изменения stage
                    # Можно добавить сообщение коннектору
                    connector.add_message("warning", "Connector disabled due to inactivity timeout.")
                    await self._save_connectors()

    async def _save_connectors(self):
        try:
            connectors_to_save = {}
            for cid, c in self.connectors.items():
                connector_dump = c.model_dump(mode='json')
                logger.info(f"[SAVE_CONNECTORS_DEBUG] Saving connector {cid}. Config in dump: {connector_dump.get('config')}")
                connectors_to_save[cid] = connector_dump
            
            async with aiofiles.open(self.storage_path, 'w') as f:
                await f.write(json.dumps(connectors_to_save, indent=4, ensure_ascii=False))
            logger.debug(f"Connectors saved to {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to save connectors: {e}")

    async def _load_connectors(self):
        if self.storage_path.exists():
            try:
                async with aiofiles.open(self.storage_path, 'r') as f:
                    content = await f.read()
                    if not content.strip(): # Если файл пустой
                        logger.info(f"Connector storage file {self.storage_path} is empty. Initializing with empty list.")
                        self.connectors = {}
                        return
                    loaded_data = json.loads(content)
                    temp_connectors = {}
                    logger.info(f"[LOAD_CONNECTORS_DEBUG] Loading from {self.storage_path}. Data: {loaded_data}") # Лог всего файла
                    for cid, cdata in loaded_data.items():
                        logger.info(f"[LOAD_CONNECTORS_DEBUG] Loading connector {cid}. Config in cdata: {cdata.get('config')}")
                        temp_connectors[cid] = Connector(**cdata)
                        logger.info(f"[LOAD_CONNECTORS_DEBUG] Connector {cid} loaded. Resulting connector.config: {temp_connectors[cid].config}, stage: {temp_connectors[cid].stage}")
                    self.connectors = temp_connectors
                logger.info(f"Connectors loaded from {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to load connectors from {self.storage_path}: {e}. Initializing with empty list.")
                self.connectors = {}
        else:
            logger.info(f"Connector storage file not found at {self.storage_path}. Initializing with empty list.")
            self.connectors = {}

    # New methods for onboarding FSM
    async def initiate_onboarding(self, connector_id: uuid.UUID) -> OnboardingStepInfo:
        """
        Initiates or retrieves the current state of the onboarding process for a connector.
        This reflects the last information provided by the connector or the FSM's current waiting state.
        """
        logger.debug(f"Initiating onboarding for connector_id: {connector_id}")
        state = await self._onboarding_repo.get_state(connector_id)
        if state and not state.is_completed and not state.is_failed and not state.current_step_id == "AWAITING_ONBOARD_START":
            logger.info(f"Resuming onboarding for {connector_id} at step {state.current_step_id}")
            # If resuming, the UI will call /status which should reflect the last known step
            # or the fact we are awaiting connector input.
            # The initiate call primarily ensures the FSM process is active.
            # We might not immediately have the step_info if we're awaiting it from connector.
            last_known_step_info = state.onboarding_context.get("last_provided_step_info_by_connector")
            if last_known_step_info:
                print(f"LAST KNOWN STEP INFO: {last_known_step_info}")
                return OnboardingStepInfo(**last_known_step_info) # Return the last step connector defined
            else:
                # If no specific step info from connector yet, indicate we're waiting for it.
                # The get_connector_fsm_directive will instruct connector to provide first step.
                return OnboardingStepInfo(
                    step_id=state.current_step_id or "awaiting_connector_initial_step",
                    description="Onboarding process is active. Waiting for connector to define the current step.",
                    messages=["Awaiting initial step definition from connector."]
                )

        state = OnboardingState(
            connector_id=connector_id,
            current_step_id="awaiting_connector_step_definition:initial", # New state: FSM waits for connector
            onboarding_context={ "dynamic_config_refresh_needed": False },
            is_completed=False,
            is_failed=False
        )

        await self._onboarding_repo.save_state(state)
        logger.info(f"New onboarding process started for {connector_id}. State: {state.current_step_id}")
        return OnboardingStepInfo(
            step_id=state.current_step_id,
            description="Onboarding initiated. Waiting for connector to provide the first step details via FSM sync.",
            messages=["Awaiting initial step definition from connector via FSM sync mechanism."]
        )

    async def get_onboarding_status(self, connector_id: uuid.UUID) -> OnboardingStepInfo:
        """
        Gets the current status of the onboarding process for a connector.
        This reflects the last information provided by the connector or the FSM's current waiting state.
        """
        logger.debug(f"Getting onboarding status for connector_id: {connector_id}")
        state = await self._onboarding_repo.get_state(connector_id)
        if not state:
            logger.warning(f"No onboarding state found for connector {connector_id} in get_onboarding_status. Returning 'not_initiated'.")
            # Do NOT initiate onboarding here - this should be an explicit action from the Hub
            return OnboardingStepInfo(
                step_id="not_initiated", # Standardized step_id for Hub to recognize
                description="Onboarding process has not been initiated for this connector.",
                messages=["Please initiate the onboarding process from the Hub."],
                is_final_step=False 
            )

        if state.is_completed:
            return OnboardingStepInfo(
                step_id="completed",
                description="Onboarding is complete.",
                is_final_step=True,
                messages=["Connector onboarding successfully completed."]
            )

        if state.is_failed:
            return OnboardingStepInfo(
                step_id="failed",
                description="Onboarding has failed.",
                is_final_step=True,
                messages=[state.last_error_message or "An unspecified error occurred during onboarding."]
            )
        
        # Try to return the last step info provided by the connector IF we are awaiting user input for that step
        if state.current_step_id and state.current_step_id.startswith("awaiting_user_input:"):
            last_provided_step_info_dict = state.onboarding_context.get("last_provided_step_info_by_connector")
            if last_provided_step_info_dict:
                try:
                    # This is the step definition the UI should render for user input
                    return OnboardingStepInfo(**last_provided_step_info_dict)
                except Exception as e:
                    logger.error(f"Failed to parse last_provided_step_info_by_connector for {connector_id} when in awaiting_user_input state: {e}. State: {state.current_step_id}")
                    # Fallback to a generic message for this state
                    return OnboardingStepInfo(
                        step_id=state.current_step_id,
                        description=f"Error parsing step definition. FSM is awaiting user input for step: {state.current_step_id.split(':',1)[-1]}.",
                        messages=[f"Internal error: Could not display step details for {state.current_step_id.split(':',1)[-1]}."],
                        is_final_step=False
                    )
        
        # Fallback for other states (e.g., awaiting_connector_step_definition, awaiting_connector_processing)
        # or if last_provided_step_info_by_connector is missing when it shouldn't be.
        description_message = f"Onboarding is at FSM state: {state.current_step_id}. Waiting for further action."
        current_step_messages = [description_message]

        if state.current_step_id == "AWAITING_ONBOARD_START":
            description_message = "Onboarding is awaiting initiation from the Hub."
            current_step_messages = ["Please initiate the onboarding process from the Hub."]
        elif "awaiting_connector_processing" in state.current_step_id:
            step_being_processed = state.current_step_id.split(':',1)[-1]
            description_message = f"Awaiting connector to process submitted data for step: {step_being_processed}."
            current_step_messages = [description_message, "The connector is currently processing your input."]
        elif "awaiting_connector_step_definition" in state.current_step_id:
            step_ctx = state.current_step_id.split(':',1)[-1]
            description_message = f"Awaiting connector to define step: {step_ctx}."
            current_step_messages = [description_message, "The connector needs to provide the next step details."]
        
        return OnboardingStepInfo(
            step_id=state.current_step_id, 
            description=description_message,
            messages=current_step_messages,
            is_final_step=False 
        )

    async def submit_onboarding_step(self, connector_id: uuid.UUID, payload: StepSubmissionPayload) -> StepSubmissionResult:
        """
        Receives data from the UI for a step defined by the connector.
        Stores this data and sets the FSM state to await connector processing.
        """
        logger.debug(f"UI submitting onboarding step for connector_id: {connector_id}, payload step_id: {payload.step_id}")
        state = await self._onboarding_repo.get_state(connector_id)

        if not state:
            logger.warning(f"No onboarding state found for connector {connector_id} during submit_onboarding_step.")
            return StepSubmissionResult(success=False, error_message="Onboarding not initiated. Please initiate first.")

        if state.is_completed:
            return StepSubmissionResult(success=True, is_onboarding_complete=True, messages=["Onboarding is already complete."])
        if state.is_failed:
            return StepSubmissionResult(success=False, error_message=f"Onboarding has failed: {state.last_error_message}")

        last_provided_step_info_dict = state.onboarding_context.get("last_provided_step_info_by_connector")
        if not last_provided_step_info_dict or last_provided_step_info_dict.get("step_id") != payload.step_id:
            logger.warning(f"Step ID mismatch or no step defined by connector for {connector_id}. Expected {last_provided_step_info_dict.get('step_id') if last_provided_step_info_dict else 'N/A'}, UI sent {payload.step_id}.")
            return StepSubmissionResult(success=False, error_message=f"Step ID mismatch or step not yet defined by connector. Please refresh status.")

        # Store the user's submission and change FSM state to await connector processing via sync
        state.onboarding_context["pending_user_submission_for_connector"] = payload.model_dump()
        # The part after ":" is the original step_id from the connector that this data pertains to.
        state.current_step_id = f"awaiting_connector_processing:{payload.step_id}" 
        state.onboarding_context.pop("last_provided_step_info_by_connector", None) # Clear old step def
        await self._onboarding_repo.save_state(state)

        logger.info(f"Data for step {payload.step_id} received for {connector_id}. FSM state: {state.current_step_id}. Awaiting connector sync.")
        # The UI will now poll /status, which will indicate that we are waiting for the connector.
        # The actual next_step_info will come after the connector processes this submission via sync.
        return StepSubmissionResult(
            success=True, 
            messages=["Data submitted. Awaiting connector to process and provide next step via FSM sync."],
            # No next_step_info here, it will be available after connector syncs and processes.
            is_onboarding_complete=False 
        )

    # --- New methods for FSM Sync with Connector ---

    async def get_connector_fsm_directive(self, connector_id: uuid.UUID) -> ConnectorDirective:
        """
        Called by the connector polling for FSM directives.
        Determines what the FSM needs from the connector based on current state.
        """
        state = await self._onboarding_repo.get_state(connector_id)
        if not state or state.is_completed or state.is_failed:
            logger.debug(f"No active onboarding FSM for {connector_id} or already terminal. Sending no-op directive or error.")
            # Potentially return a specific directive like 'NO_OP' or 'ONBOARDING_TERMINATED'
            # For now, this might indicate an issue if connector polls unexpectedly.
            # Or, if state is None, it could be an unregistered connector trying to sync.
            if not state:
                raise HTTPException(status_code=404, detail="Connector not found or onboarding not initiated.")
        
            action_type = ConnectorDirectiveActionType.PROVIDE_STEP_DEFINITION # Default or error placeholder
            if state.is_completed:
                 #This should ideally be handled by connector not polling anymore, or a specific NO_OP directive type
                logger.info(f"Onboarding for {connector_id} is completed. Connector should ideally not poll /fsm/sync.")
                action_type = ConnectorDirectiveActionType.PROVIDE_STEP_DEFINITION # Placeholder - or add NO_OP
            elif state.is_failed:
                logger.info(f"Onboarding for {connector_id} has failed. Connector should ideally not poll /fsm/sync.")
                action_type = ConnectorDirectiveActionType.PROVIDE_STEP_DEFINITION # Placeholder - or add NO_OP
            
            # Fallback/error directive, should ideally have specific NO_OP type.
            return ConnectorDirective(
                action_type=action_type, # Should be a NO_OP or specific terminal state signal
                action_context_step_id="terminated_or_no_state",
                current_fsm_context_snapshot=state.onboarding_context if state else None
            )

        # --- Новая обработка: если FSM в состоянии ожидания старта онбординга ---
        if state.current_step_id == "AWAITING_ONBOARD_START":
            logger.info(f"FSM for {connector_id} is in AWAITING_ONBOARD_START. Sending AWAIT_ONBOARDING_START directive to connector.")
            return ConnectorDirective(
                action_type=ConnectorDirectiveActionType.AWAIT_ONBOARDING_START,
                action_context_step_id="awaiting_onboard_start",
                current_fsm_context_snapshot=state.onboarding_context
            )

        logger.info(f"Connector {connector_id} is in FSM state: {state.current_step_id}. Determining directive.")

        if state.onboarding_context.get("dynamic_config_refresh_needed", False):
            return ConnectorDirective(
                action_type=ConnectorDirectiveActionType.PROVIDE_DYNAMIC_CONFIG_OPTIONS,
                current_fsm_context_snapshot=state.onboarding_context
            )

        # Handle awaiting_user_input state - connector should wait for user input
        if state.current_step_id and state.current_step_id.startswith("awaiting_user_input:"):
            # When FSM is waiting for user input, connector should not be asked to provide step definition again
            # Instead, it should wait (NO_OP or AWAIT_USER_INPUT)
            step_id = state.current_step_id.split(":", 1)[-1]
            logger.info(f"FSM for {connector_id} is in awaiting_user_input state for step {step_id}. Sending AWAIT_USER_INPUT directive.")
            return ConnectorDirective(
                action_type=ConnectorDirectiveActionType.AWAIT_USER_INPUT,
                action_context_step_id=step_id,
                current_fsm_context_snapshot=state.onboarding_context
            )
            
        if "awaiting_connector_step_definition" in state.current_step_id:
            # FSM needs the connector to define the current or next step.
            # The part after ":" is a context for the connector (e.g., "initial", or a previous step_id)
            step_context_for_connector = state.current_step_id.split(":", 1)[-1]
            return ConnectorDirective(
                action_type=ConnectorDirectiveActionType.PROVIDE_STEP_DEFINITION,
                action_context_step_id=step_context_for_connector, # e.g., "initial" or previous_step_id
                current_fsm_context_snapshot=state.onboarding_context
            )
        
        if "awaiting_connector_processing" in state.current_step_id:
            # FSM has data from UI and needs connector to process it.
            pending_submission = state.onboarding_context.get("pending_user_submission_for_connector")
            if pending_submission:
                original_step_id_for_data = state.current_step_id.split(":",1)[-1]
                return ConnectorDirective(
                    action_type=ConnectorDirectiveActionType.PROCESS_STEP_DATA,
                    action_context_step_id=original_step_id_for_data, # The step_id this data belongs to
                    data_for_connector_processing=pending_submission.get("data"),
                    current_fsm_context_snapshot=state.onboarding_context
                )
            else:
                # This is an inconsistent state, should not happen if FSM logic is correct
                logger.error(f"FSM state for {connector_id} is {state.current_step_id} but no pending_user_submission found.")
                # Fallback: ask connector to define a step, maybe it can recover or clarify.
                state.current_step_id = "awaiting_connector_step_definition:error_recovery"
                await self._onboarding_repo.save_state(state)
                return ConnectorDirective(
                    action_type=ConnectorDirectiveActionType.PROVIDE_STEP_DEFINITION,
                    action_context_step_id="error_recovery",
                    current_fsm_context_snapshot=state.onboarding_context
                )

        # Fallback or default directive if state is unexpected
        logger.warning(f"Unexpected FSM state {state.current_step_id} for {connector_id}. Defaulting to PROVIDE_STEP_DEFINITION.")
        return ConnectorDirective(
            action_type=ConnectorDirectiveActionType.PROVIDE_STEP_DEFINITION,
            action_context_step_id="default_fallback",
            current_fsm_context_snapshot=state.onboarding_context
        )

    async def process_connector_fsm_update(self, connector_id: uuid.UUID, update: ConnectorFSMUpdate) -> None:
        """
        Processes an FSM update sent by the connector.
        Updates the ConnectorOnboardingState based on the connector's input.
        """
        state = await self._onboarding_repo.get_state(connector_id)
        if not state or state.is_completed or state.is_failed:
            logger.warning(f"Received FSM update from {connector_id} but no active FSM or FSM is terminal. Ignoring update: {update.model_dump_json()}")
            return

        logger.info(f"Processing FSM update from {connector_id} for action {update.processed_action_type}, context step: {update.processed_action_context_step_id}, status: {update.status}")

        if update.status == ConnectorFSMUpdateStatus.FAILURE:
            state.last_error_message = update.error_message or "Connector reported an unspecified failure."
            # Potentially set state.is_failed = True if error is critical / repeated
            logger.error(f"Connector {connector_id} reported failure for action {update.processed_action_type} on step {update.processed_action_context_step_id}: {state.last_error_message}")
            # For now, we keep the FSM in the current step, or revert to awaiting definition.
            # UI will see the error via /status through last_error_message or a specific step info.
            # Let's assume it stays in a state where it might retry or admin intervenes.
            # If it was processing data, clear pending submission to avoid reprocessing same error.
            if update.processed_action_type == ConnectorDirectiveActionType.PROCESS_STEP_DATA:
                 state.onboarding_context.pop("pending_user_submission_for_connector", None)
                 # Revert to let connector define what to do next, or if it can redefine current step with error context
                 state.current_step_id = f"awaiting_connector_step_definition:{update.processed_action_context_step_id}_after_error"
                 state.onboarding_context["last_error_from_connector_processing"] = state.last_error_message
            await self._onboarding_repo.save_state(state)
            return

        # Clear last error on success
        state.last_error_message = None

        if update.processed_action_type == ConnectorDirectiveActionType.PROVIDE_STEP_DEFINITION:
            if update.step_definition_provided:
                logger.info(f"Connector {connector_id} provided step definition for: {update.step_definition_provided.step_id}")
                state.onboarding_context["last_provided_step_info_by_connector"] = update.step_definition_provided.model_dump()
                # FSM state should now reflect that we are awaiting user input for this specific step.
                state.current_step_id = f"awaiting_user_input:{update.step_definition_provided.step_id}"
                
                if update.step_definition_provided.is_final_step:
                    logger.info(f"Connector {connector_id} provided a final step definition: {update.step_definition_provided.step_id}.")
                    # If it's final AND requires no input, then it could be complete.
                    if not update.step_definition_provided.input_schema:
                        state.is_completed = True
                        state.current_step_id = "completed_by_connector_final_step_definition"
                        logger.info(f"Onboarding for {connector_id} marked as completed by final step definition without input.")
            else:
                logger.warning(f"Connector {connector_id} successful PROVIDE_STEP_DEFINITION but no step_definition_provided. FSM state remains: {state.current_step_id}")

        elif update.processed_action_type == ConnectorDirectiveActionType.PROCESS_STEP_DATA:
            logger.info(f"Connector {connector_id} successfully processed data for step: {update.processed_action_context_step_id}")
            state.onboarding_context.pop("pending_user_submission_for_connector", None)
            if update.processing_result_data_to_update_context:
                state.onboarding_context.update(update.processing_result_data_to_update_context)
            
            if update.step_definition_provided:
                # Connector processed data AND provided the next step definition
                state.onboarding_context["last_provided_step_info_by_connector"] = update.step_definition_provided.model_dump()
                state.current_step_id = f"awaiting_user_input:{update.step_definition_provided.step_id}" # Awaiting input for the new step

                if update.step_definition_provided.is_final_step and not update.step_definition_provided.input_schema:
                    state.is_completed = True
                    state.current_step_id = "completed_by_connector_processing"
                    logger.info(f"Onboarding for {connector_id} marked as completed after processing and final step definition without input.")
            else:
                # Connector processed data but didn't define next step. FSM must ask for it.
                state.current_step_id = f"awaiting_connector_step_definition:after_processing_{update.processed_action_context_step_id}"
                state.onboarding_context.pop("last_provided_step_info_by_connector", None) # Clear old one
                logger.info(f"Connector {connector_id} processed data, now awaiting next step definition. FSM state: {state.current_step_id}")


        elif update.processed_action_type == ConnectorDirectiveActionType.PROVIDE_DYNAMIC_CONFIG_OPTIONS:
            logger.info(f"Connector {connector_id} provided dynamic config options.")
            if update.dynamic_config_options_provided:
                # Store this somewhere appropriate, e.g., in the main Connector model's config or a dedicated field
                # This part needs integration with how Connector model stores its runtime display/choice options
                logger.info(f"Dynamic options from {connector_id}: {update.dynamic_config_options_provided}")
                
                # Получаем экземпляр Connector из коллекции коннекторов 
                # connector_id передается как UUID, но хранится как str в collection
                connector = await self.get_connector(str(connector_id))
                if connector:
                    # Обновляем динамические опции и, возможно, схему
                    connector.update_dynamic_options(
                        new_options=update.dynamic_config_options_provided,
                        new_schema=update.new_full_config_schema_provided
                    )
                    logger.info(f"Updated dynamic options and schema for connector {connector_id}")
                else:
                    logger.warning(f"Could not find connector {connector_id} to update dynamic options")
                
            if update.new_full_config_schema_provided:
                # Update the connector's main config_schema if connector provides a new one
                logger.info(f"Connector {connector_id} provided new full config_schema.")
                
            state.onboarding_context["dynamic_config_refresh_needed"] = False # Reset the flag
            state.onboarding_context["last_dynamic_config_refresh_timestamp"] = datetime.utcnow().isoformat()

        await self._onboarding_repo.save_state(state)
        logger.debug(f"FSM state for {connector_id} after update: {state.current_step_id}, completed: {state.is_completed}, context keys: {list(state.onboarding_context.keys())}")

    async def mark_connector_for_dynamic_config_refresh(self, connector_id: uuid.UUID) -> None:
        """
        Marks a connector as needing its dynamic configuration options refreshed.
        The actual refresh will happen via the FSM sync mechanism.
        """
        state = await self._onboarding_repo.get_state(connector_id)
        if not state:
            # If connector is operational, it should have an onboarding state (even if completed).
            # If no state, we might need to create a minimal one just for this flag, or log an error.
            # For now, assume operational connectors might not have an *active* FSM state object if onboarding was simple.
            # This needs refinement: should all connectors retain an FSM state object indefinitely for such flags?
            # Alternative: Store this flag directly on the main Connector model if it exists and is accessible here.
            logger.warning(f"Attempted to mark dynamic_config_refresh for {connector_id}, but no FSM state found. This feature might need FSM state to persist or an alternative flag location.")
            # Let's try to create/update a state just for this flag if it's missing
            state = OnboardingState(connector_id=connector_id, onboarding_context={}, current_step_id="operational_config_refresh_pending")
        
        state.onboarding_context["dynamic_config_refresh_needed"] = True
        await self._onboarding_repo.save_state(state)
        logger.info(f"Connector {connector_id} marked for dynamic configuration refresh.")

    # End of new FSM Sync methods

    async def verify_integration_key(self, key_value: str, connector_type: Optional[str] = None) -> bool:
        """
        Проверяет, действителен ли ключ интеграции для указанного типа коннектора.
        
        Args:
            key_value: значение ключа интеграции
            connector_type: тип коннектора (если указан, проверяется соответствие ограничениям)
            
        Returns:
            True если ключ действителен, False в противном случае
        """
        if not key_value:
            return False
        
        # Получаем ключ по его значению
        integration_key_service = get_integration_key_service()
        key = integration_key_service.get_key_by_value(key_value)
        
        # Проверяем, что ключ существует и действителен
        if key is None:
            return False
        
        # Проверяем, может ли ключ быть использован для регистрации коннектора
        # Передаем тип коннектора для проверки соответствия ограничениям
        return key.can_register_connector(connector_type)

_connector_service_singleton: Optional[ConnectorService] = None

def initialize_connector_service(onboarding_repo: OnboardingStateRepository, 
                                 storage_path: Optional[str] = None,
                                 check_interval_seconds: Optional[int] = None,
                                 max_silence_minutes: Optional[int] = None) -> ConnectorService:
    global _connector_service_singleton
    if _connector_service_singleton is None:
        _connector_service_singleton = ConnectorService(
            onboarding_repo=onboarding_repo,
            storage_path=storage_path,
            check_interval_seconds=check_interval_seconds,
            max_silence_minutes=max_silence_minutes
        )
        logger.info("ConnectorService initialized with OnboardingRepository.")
    return _connector_service_singleton

# Update get_connector_service to use the new singleton
# This ensures that an initialized instance is always returned, provided initialize_connector_service was called.
def get_onboarding_service():
    """
    Returns the onboarding service, which is actually the connector service
    since it handles onboarding functionality.
    
    Returns:
        ConnectorService instance that handles onboarding
    """
    return get_connector_service()

def get_connector_service() -> ConnectorService: # Re-defining to replace the old one
    global _connector_service_singleton
    if _connector_service_singleton is None:
        # Detect if we are running in a test environment
        # Common way to detect test environment is to check if 'pytest' is running
        import sys
        is_pytest = any(arg.startswith('pytest') for arg in sys.argv) or 'PYTEST_CURRENT_TEST' in os.environ
        
        if is_pytest:
            # Automatically initialize for tests with InMemoryOnboardingStateRepository
            logger.warning("Automatically initializing ConnectorService for tests with InMemoryOnboardingStateRepository.")
            from mindbank_poc.core.connectors.onboarding_repository import InMemoryOnboardingStateRepository
            repo = InMemoryOnboardingStateRepository()
            _connector_service_singleton = ConnectorService(onboarding_repo=repo) 
            # We don't call _connector_service_singleton.start() here as it's async and this is a sync function.
            # Tests should handle this separately if needed.
        else:
            # In production, we expect initialize_connector_service to be called explicitly
            logger.critical("FATAL: get_connector_service() called before initialize_connector_service(). This indicates a setup error.")
            raise RuntimeError("ConnectorService has not been initialized. Call initialize_connector_service() first.")
    
    return _connector_service_singleton
