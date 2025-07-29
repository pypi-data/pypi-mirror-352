"""Telegram connector *client*.

Watches Telegram sources through :class:`TelegramConnector` and streams messages
to the Ingest API.  Messages are grouped into small buffers (``BULK_API_SIZE``)
and flushed either when the buffer is full or when ``BUFFER_FLUSH_TIMEOUT`` has
elapsed – this minimises HTTP overhead while still providing near-real-time
delivery.
"""
import uuid
import base64
import aiohttp
import asyncio
from datetime import timezone
from typing import Any, Dict, List, Optional
import os
import json

# Local package imports
from .connector import TelegramConnector, TelegramConfigManager
from .constants import (
    CONFIG_FILE,
    BATCH_LIMIT,
    BATCH_PAGE,
    BATCH_SLEEP,
    CONFIG_CHECK_SLEEP,
    WHITE_LIST,
    BULK_API_SIZE,
    BUFFER_FLUSH_TIMEOUT,
    AGGREGATE_GAP_SECONDS,
    AUTO_FLUSH_INTERVAL,
)
from .buffer import EntryBuffer
from .onboard_steps import TELEGRAM_ONBOARDING_STEP_MAP, TELEGRAM_ONBOARDING_STEPS
from .client_manager import ClientManager

# Pydantic models
from mindbank_poc.core.common.types import RawEntry

# Default settings
DEFAULT_API_URL = "http://localhost:8000"
STATE_FILE = os.path.join(os.path.dirname(__file__), "connector_state.json")

class ConnectorStateManager:
    def __init__(self, filepath="connector_state.json"):
        self.filepath = filepath
        self._state = {}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._state = json.load(f)
            except Exception as e:
                print(f"[STATE] Ошибка чтения состояния: {e}")
                self._state = {}
        else:
            self._state = {}

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[STATE] Ошибка сохранения состояния: {e}")

    def get(self, key, default=None):
        return self._state.get(key, default)

    def set(self, key, value):
        self._state[key] = value
        self.save()

    def update(self, **kwargs):
        self._state.update(kwargs)
        self.save()

    def as_dict(self):
        return dict(self._state)

class TelegramConnectorRegistration:
    """
    Класс для регистрации Telegram-коннектора в API, работы с access_token, connector_id и состоянием.
    """
    def __init__(self, api_url=DEFAULT_API_URL, integration_key=None, state_file=STATE_FILE):
        self.api_url = api_url
        self.integration_key = integration_key
        self.state_manager = ConnectorStateManager(state_file)

    @property
    def access_token(self):
        return self.state_manager.get("access_token")

    @access_token.setter
    def access_token(self, value):
        self.state_manager.set("access_token", value)

    @property
    def connector_id(self):
        return self.state_manager.get("connector_id")

    @connector_id.setter
    def connector_id(self, value):
        self.state_manager.set("connector_id", value)

    def load_state(self):
        # Для обратной совместимости, просто загружает state_manager
        self.state_manager.load()
        return bool(self.access_token and self.connector_id)

    def save_state(self):
        self.state_manager.save()

    async def register_connector(self, connector_type):
        """Регистрирует коннектор в API и сохраняет access_token и connector_id."""
        if not self.integration_key:
            raise ValueError("Integration key is required for registration")
        print("Registering connector...")
        registration_data = {
            "type": connector_type,
            "metadata": {
                "version": "1.0.0",
                "description": "Connector for monitoring Telegram sources"
            },
            "config_schema": {
                "type": "object",
                "properties": {
                    "available_sources": {
                        "type": "array",
                        "description": "Список доступных источников Telegram",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "description": "ID источника"},
                                "name": {"type": "string", "description": "Название источника"},
                                "monitoring_status": {
                                    "type": "string",
                                    "title": "Monitoring Status",
                                    "enum": ["inactive", "monitored"],
                                    "description": "Status related to monitoring activity"
                                },
                                "fetching_status": {
                                    "type": "string",
                                    "title": "Fetching Status",
                                    "enum": ["inactive", "fetching", "fetched"],
                                    "description": "Status related to fetching process"
                                },
                                "anchor_id": {"type": ["integer", "null"], "description": "Anchor ID для отслеживания"}
                            },
                            "required": ["id", "name", "monitoring_status", "fetching_status"]
                        }
                    }
                },
                "required": ["available_sources"]
            },
            "integration_key": self.integration_key,
            "capabilities": [
                "text",
                "image",
                "audio",
                "video",
                "file",
                "code",
                "link"
            ],
            "skip_periodic_handshake": False,
            "setup_details": {
                "setup_instructions": "Введите api_id/hash а потом телефон и код из телеграмма"
            }
            # FSM-based onboarding is used instead of a setup URL
            # This connector uses multi-step authentication via the Core's FSM mechanism
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/connectors/register",
                    json=registration_data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"Failed to register connector: {error_text}")
                        raise Exception(f"Registration failed with status {response.status}: {error_text}")
                    result = await response.json()
                    self.access_token = result.get("access_token")
                    self.connector_id = result.get("connector_id")
                    print(f"Connector registered successfully. Access token и connector_id получены.")
                    self.save_state()
        except Exception as e:
            print(f"Error registering connector: {e}")
            raise

class TelegramConnectorOnboarding:
    """
    Класс для FSM-онбординга Telegram-коннектора (все шаги, связанные с сессией и ClientManager).
    
    Этот класс реализует пошаговый онбординг через FSM (Finite State Machine) механизм Core API.
    Вместо использования setup_url и перенаправления пользователя на веб-страницу,
    коннектор синхронизируется с Core API через эндпоинты /connectors/{id}/fsm/sync 
    и /connectors/{id}/fsm/sync_update, получая директивы и отправляя результаты обработки.
    
    Шаги онбординга определены в TELEGRAM_ONBOARDING_STEPS и включают:
    1. Ввод api_id и api_hash
    2. Ввод номера телефона
    3. Ввод кода подтверждения
    4. Опционально: Ввод пароля двухфакторной аутентификации
    5. Завершение процесса с сохранением session_string
    """
    def __init__(self, api_url=DEFAULT_API_URL, connector_id=None, access_token=None, state_file=STATE_FILE):
        self.api_url = api_url
        self.state_manager = ConnectorStateManager(state_file)
        self.client_manager = ClientManager(self.state_manager)
        self.step_idx = 0
        self._last_sent_step = None  # Track the last sent step to prevent duplicates

    @property
    def connector_id(self):
        return self.state_manager.get("connector_id")

    @property
    def access_token(self):
        return self.state_manager.get("access_token")

    @property
    def session_string(self):
        return self.state_manager.get("session_string")

    @session_string.setter
    def session_string(self, value):
        self.state_manager.set("session_string", value)

    async def fsm_onboarding(self):
        onboarding_data = {}
        
        print("[ONBOARDING] Запуск FSM-онбординга Telegram...")
        while True:
            try:
                directive = await self._get_directive()
                action_type = directive.get("action_type")
                step_id = directive.get("action_context_step_id")

                # Проверка на финальный шаг FSM
                is_final = False
                try:
                    is_final = directive.get('current_fsm_context_snapshot', {}) \
                        .get('last_provided_step_info_by_connector', {}) \
                        .get('is_final_step', False)
                except Exception:
                    pass
                print(f"[ONBOARDING] Получен шаг: {step_id}, action_type: {action_type}, is_final: {is_final}, step_idx: {self.step_idx}")
                if is_final or step_id in ('done', 'terminated_or_no_state'):
                    print("[ONBOARDING] Получен финальный шаг, онбординг завершён.")
                    return

                if action_type == "PROVIDE_STEP_DEFINITION":
                    print("[ONBOARDING] Получен шаг определения, отправляем его в API...")
                    # Only send if we haven't sent this step before
                    if step_id != self._last_sent_step:
                        await self._handle_provide_step_definition(self.step_idx)
                        self._last_sent_step = step_id
                elif action_type == "PROCESS_STEP_DATA":
                    print("[ONBOARDING] Получен шаг данных, обрабатываем его...")
                    data = directive.get("data_for_connector_processing", {})
                    onboarding_data.update(data)
                    result = await self._handle_process_step_data(step_id, onboarding_data)
                    if result == "done":
                        print("[ONBOARDING] Онбординг Telegram завершён, session_string сохранён.")
                        return
                    self.step_idx += 1
                    self._last_sent_step = None  # Reset last sent step when moving to next step
                elif action_type == "AWAIT_ONBOARDING_START":
                    print("[ONBOARDING] Ожидание старта онбординга от UI/админа...")
                    # Send response to indicate we're ready and waiting for onboarding to start
                    await self._post_update({
                        "processed_action_type": "AWAIT_ONBOARDING_START",
                        "status": "SUCCESS",
                        "processed_action_context_step_id": step_id or "awaiting_start"
                    })
                    # Reset last sent step when starting onboarding
                    self._last_sent_step = None
                    # Now send the first step definition
                    await self._handle_provide_step_definition(0)
                    self._last_sent_step = "api_id_hash"
                else:
                    await self._handle_unknown_action(action_type)
                await asyncio.sleep(2)  # Increased sleep time to reduce polling frequency
            except Exception as e:
                import traceback
                print(f"[ONBOARDING][ОШИБКА] {e}")
                print(traceback.format_exc())
                break

    async def reset_onboarding(self):
        # Сброс онбординга на сервере
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/connectors/{self.connector_id}/reset-setup",
                headers={"Authorization": f"Bearer {self.access_token}"}
            ) as resp:
                if resp.status != 200:
                    print(f"Ошибка сброса онбординга на сервере: {await resp.text()}")
                else:
                    print("[ONBOARDING] Онбординг успешно сброшен на сервере.")
        # Локальный сброс индекса шага
        self.step_idx = 0

    async def _get_directive(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/connectors/{self.connector_id}/fsm/sync",
                headers={"Authorization": f"Bearer {self.access_token}"}
            ) as resp:
                return await resp.json()

    async def _post_update(self, update):
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{self.api_url}/connectors/{self.connector_id}/fsm/sync_update",
                json=update,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )

    async def _handle_provide_step_definition(self, step_idx):
        from .onboard_steps import TELEGRAM_ONBOARDING_STEPS
        try:
            step = TELEGRAM_ONBOARDING_STEPS[step_idx]
            update = {
                "processed_action_type": "PROVIDE_STEP_DEFINITION",
                "processed_action_context_step_id": step.step_id,
                "status": "SUCCESS",
                "step_definition_provided": step.model_dump()
            }
            await self._post_update(update)
        except (KeyError, IndexError):
            print(f"Неизвестный шаг онбординга: {step_idx}")

    async def _handle_process_step_data(self, step_id, onboarding_data):
        try:
            if step_id == "api_id_hash":
                await self._process_api_id_hash(onboarding_data)
            elif step_id == "phone":
                await self._process_phone(onboarding_data)
            elif step_id == "code":
                result = await self._process_code(onboarding_data)
                if result == "done":
                    return "done"
            elif step_id == "password":
                await self._process_password(onboarding_data)
            elif step_id == "done":
                return "done"
            await self._post_success_update(step_id)
        except Exception as e:
            await self._process_step_failure(step_id, e)

    async def _process_api_id_hash(self, onboarding_data):
        await self.client_manager.set_api_id_hash(onboarding_data["api_id"], onboarding_data["api_hash"])

    async def _process_phone(self, onboarding_data):
        await self.client_manager.set_phone(onboarding_data["phone"])
        await self.client_manager.send_code_request()

    async def _process_code(self, onboarding_data):
        result = await self.client_manager.sign_in_with_code(onboarding_data["code"])
        if result is True:
            await self._save_session_string(onboarding_data)
            await self._post_success_update("code")
            return "done"
        elif result is False:
            await self._post_success_update("code")
            return None
        else:
            raise Exception(result)

    async def _process_password(self, onboarding_data):
        await self.client_manager.sign_in_with_password(onboarding_data["password"])
        await self._save_session_string(onboarding_data)

    async def _save_session_string(self, onboarding_data):
        session_string = self.client_manager.get_session_string()
        onboarding_data["session_string"] = session_string
        self.session_string = session_string
        await self.client_manager.save()

    async def _post_success_update(self, step_id):
        update = {
            "processed_action_type": "PROCESS_STEP_DATA",
            "processed_action_context_step_id": step_id,
            "status": "SUCCESS"
        }
        await self._post_update(update)

    async def _process_step_failure(self, step_id, error):
        update = {
            "processed_action_type": "PROCESS_STEP_DATA",
            "processed_action_context_step_id": step_id,
            "status": "FAILURE",
            "error_message": str(error)
        }
        await self._post_update(update)
        print(f"Ошибка при создании сессии Telegram: {error}")
        # Сбросить онбординг и начать заново
        await self.reset_onboarding()
        print("[ONBOARDING] Перезапуск онбординга Telegram...")
        await self.fsm_onboarding()

    async def _handle_unknown_action(self, action_type):
        print(f"Неизвестный action_type: {action_type}")
        await asyncio.sleep(1)

class TelegramConnectorClient(TelegramConnectorRegistration, TelegramConnectorOnboarding):
    """
    Главный клиент Telegram-коннектора. Наследует регистрацию и онбординг, реализует бизнес-логику работы с сообщениями.
    """
    def __init__(self, 
                 api_url: str = DEFAULT_API_URL,
                 batch_limit: int = BATCH_LIMIT,
                 batch_page: int = BATCH_PAGE,
                 batch_sleep: float = BATCH_SLEEP,
                 check_sleep: float = CONFIG_CHECK_SLEEP,
                 collector_id: str = "telegram-connector",
                 integration_key: str = None,
                 state_file: str = None):
        # Если state_file не указан, используем значение по умолчанию
        if state_file is None:
            state_file = STATE_FILE
            
        TelegramConnectorRegistration.__init__(self, api_url=api_url, integration_key=integration_key, state_file=state_file)
        TelegramConnectorOnboarding.__init__(self, api_url=api_url, state_file=state_file)
        self.batch_limit = batch_limit
        self.batch_page = batch_page
        self.batch_sleep = batch_sleep
        self.check_sleep = check_sleep
        self.collector_id = collector_id
        
        self.config_manager = None
        self.connector = None
        self._source_buffers = {}
        self._registration_required = False
        self._onboarding_required = False
        self._check_state_on_init()

    def _check_state_on_init(self):
        state_loaded = self.load_state()
        if not state_loaded:
            self._registration_required = True
            print("Требуется регистрация коннектора.")
        if not self.session_string:
            self._onboarding_required = True
            print("Требуется онбординг Telegram.")
        else:
            print("Сессия Telegram уже создана.")

    def _get_source_buffer(self, source: str) -> EntryBuffer:
        """
        Возвращает буфер для указанного источника или создает новый,
        если он еще не существует.
        """
        if source not in self._source_buffers:
            print(f"Создание нового буфера для источника: {source}")
            buffer = EntryBuffer(
                api_url=self.api_url,
                bulk_size=BULK_API_SIZE,
                flush_timeout=BUFFER_FLUSH_TIMEOUT,
                access_token=self.access_token,
                gap_seconds=AGGREGATE_GAP_SECONDS,
                auto_flush_interval=AUTO_FLUSH_INTERVAL,
            )
            self._source_buffers[source] = buffer
            # Запускаем буфер сразу после создания
            asyncio.create_task(buffer.start())
        
        return self._source_buffers[source]

    def _get_media_type(self, message: Any) -> str:
        """Determine media type from message."""
        try:
            if not message.media or hasattr(message.media, 'webpage'):
                return "text"

            if hasattr(message.media, 'photo'):
                return "image"
                
            if hasattr(message.media, 'document'):
                if hasattr(message.media.document, 'mime_type'):
                    mime_type = message.media.document.mime_type
                    if mime_type.startswith('video/'):
                        return "video"
                    elif mime_type.startswith('audio/'):
                        return "audio"
                    else:
                        return "file"
                        
            # Detect sticker
            if hasattr(message.media.document, "attributes"):
                from telethon.tl.types import DocumentAttributeSticker
                if any(isinstance(attr, DocumentAttributeSticker) for attr in message.media.document.attributes):
                    return "sticker"
                        
            return "text"
        except Exception as e:
            print(f"Error determining media type for message {getattr(message, 'id', 'unknown')}: {e}")
            return "text"  # Fallback to text type

    async def _download_media(self, message: Any, client: Any) -> Optional[Dict[str, Any]]:
        """Download media and return **base64-encoded** content."""
        try:
            content_type = self._get_media_type(message)
            if content_type == "text":
                return None

            print(f"Downloading media for message {message.id} (type: {content_type})...")
            media_data = await client.download_media(message, bytes)
            if not media_data:
                print(f"No media data received for message {message.id}")
                return None

            base64_data = base64.b64encode(media_data).decode('utf-8')
            return {
                "content": base64_data,
                "filename": f"media_{message.id}"
            }

        except Exception as e:
            print(f"Error processing media for message {getattr(message, 'id', 'unknown')}: {str(e)}")
            return None

    async def _send_message_to_api(self, source: str, message: Any, client: Any) -> None:
        """
        Обрабатывает сообщение и отправляет его в API через буфер конкретного источника.
        
        Логика работы:
        1. Определяет тип контента (медиа или текст)
        2. Извлекает текст из разных типов сообщений
        3. Формирует одну или две записи в зависимости от типа контента
        4. Отправляет сформированные записи в буфер источника
        
        Все записи группируются по общему group_id и обрабатываются вместе.
        Буфер автоматически отправляет их в API в зависимости от настроек.
        """
        try:
            # 1. Определяем тип контента
            media_type = self._get_media_type(message)
            print(f"Сообщение {message.id} из {source}: тип={media_type}")

            # 2. Извлекаем текст
            text = self._extract_message_text(message)

            # Пропускаем стикеры
            if media_type == "sticker":
                print(f"Пропускаем стикер {message.id}")
                return

            # Используем chat_id как group_id для всех частей сообщения
            chat_id_val = getattr(message, "chat_id", None) or getattr(message, "peer_id", None)
            group_id = str(chat_id_val) if chat_id_val is not None else str(uuid.uuid4())
            entries = []

            # 3. Формируем записи в зависимости от типа контента
            if media_type != "text" and text.strip():
                # Добавляем текстовую запись, если есть медиа И текст
                entries.append(self._create_text_entry(
                    source=source,
                    message=message,
                    text=text,
                    group_id=group_id,
                    is_last=False
                ))

            # 4. Добавляем основную запись (медиа или текст)
            if media_type != "text":
                # Для медиа - скачиваем и формируем медиа-запись
                media_entry = await self._create_media_entry(
                    source=source,
                    message=message,
                    client=client,
                    media_type=media_type,
                    text=text,
                    group_id=group_id
                )
                entries.append(media_entry)
            else:
                # Для текста - формируем текстовую запись
                entries.append(self._create_text_entry(
                    source=source,
                    message=message,
                    text=text,
                    group_id=group_id,
                    is_last=True
                ))

            # 5. Получаем буфер для этого источника и отправляем записи
            source_buffer = self._get_source_buffer(source)
            await source_buffer.add(entries)
        except Exception as e:
            print(f"Ошибка обработки сообщения {getattr(message, 'id', 'unknown')}: {e}")

    def _extract_message_text(self, message: Any) -> str:
        """Извлекает текст из разных типов сообщений."""
        try:
            if getattr(message, "text", None):
                return message.text
            elif getattr(message, "caption", None):
                return message.caption
            elif getattr(message, "message", None):
                return message.message
        except Exception as e:
            print(f"Ошибка извлечения текста из сообщения {message.id}: {e}")
        return ""

    def _create_text_entry(self, source: str, message: Any, text: str, group_id: str, is_last: bool) -> RawEntry:
        """Создаёт объект RawEntry (text)."""
        return RawEntry(
            collector_id=self.collector_id,
            group_id=group_id,
            entry_id=str(uuid.uuid4()),
            type="text",
            payload={"content": text},
            metadata=self._create_metadata(source, message, is_last),
        )

    async def _create_media_entry(self, source: str, message: Any, client: Any, media_type: str, text: str, group_id: str) -> RawEntry:
        """Создает медиа-запись для отправки в API."""
        try:
            # Скачиваем медиа
            media_data = await self._download_media(message, client)
            if media_data:
                # Формируем payload для медиа
                media_payload = {
                    "content_base64": media_data["content"],
                    "filename": media_data["filename"],
                }
                
                # Добавляем дополнительные поля для аудио/видео
                if media_type in ("audio", "video"):
                    media_attr = getattr(message, media_type, None)
                    duration_val = getattr(media_attr, "duration", None) if media_attr else None
                    if duration_val:
                        media_payload["duration"] = duration_val
                        
                # Для файлов добавляем превью текста
                if media_type == "file" and text.strip():
                    media_payload["text_preview"] = text[:1000]
                    
                return RawEntry(
                    collector_id=self.collector_id,
                    group_id=group_id,
                    entry_id=str(uuid.uuid4()),
                    type=media_type,
                    payload=media_payload,
                    metadata=self._create_metadata(source, message, True),
                )
            else:
                # Если медиа не удалось скачать, создаем текстовую запись
                print(f"Не удалось скачать медиа для {message.id}, создаем текстовую запись")
                return self._create_text_entry(source, message, text, group_id, True)
        except Exception as e:
            print(f"Ошибка создания медиа-записи для {message.id}: {e}")
            # В случае ошибки возвращаем текстовую запись
            return self._create_text_entry(source, message, text, group_id, True)

    def _create_metadata(self, source: str, message: Any, is_last: bool) -> Dict[str, Any]:
        """Создает метаданные для записи."""
        # Обрабатываем реакции
        reactions = None
        if hasattr(message, "reactions"):
            try:
                reactions = {
                    "count": getattr(message.reactions, "count", 0),
                    "reactions": [
                        {
                            "emoji": getattr(reaction, "emoji", ""),
                            "count": getattr(reaction, "count", 0)
                        }
                        for reaction in getattr(message.reactions, "reactions", [])
                    ]
                }
            except Exception:
                pass

        # Определяем тип и название чата
        chat_type = "private"
        if getattr(message, "is_channel", False):
            chat_type = "channel"
        elif getattr(message, "is_group", False):
            chat_type = "group"

        chat_title = None
        try:
            chat_obj = getattr(message, "chat", None)
            if chat_obj is not None:
                chat_title = getattr(chat_obj, "title", None) or getattr(chat_obj, "username", None)
        except Exception:
            pass

        meta = {
            "message_id": message.id,
            "source": source,
            "author_id": getattr(message, "sender_id", None),
            "date": message.date.replace(tzinfo=timezone.utc).isoformat(),
            "chat_type": chat_type,
            "chat_title": chat_title,
            "views": getattr(message, "views", None),
            "forwards": getattr(message, "forwards", None),
            "reactions": reactions,
            "is_last": is_last,
        }
        return meta

    async def save_available_sources_to_config(self):
        """
        Получает все доступные диалоги пользователя через Telethon,
        формирует available_sources и отправляет их в config на сервер.
        """
        print("[CONFIG SYNC] Получение всех доступных диалогов Telegram...")
        client = self.client_manager.client
        await client.connect()
        dialogs = await client.get_dialogs()
        available_sources = []
        for d in dialogs:
            available_sources.append({
                "id": d.entity.id,
                "name": getattr(d, "name", None) or getattr(d.entity, "title", None),
                "monitoring_status": "inactive",
                "fetching_status": "inactive",
                "anchor_id": None
            })
        await client.disconnect()
        # Получаем актуальный config с сервера через handshake
        config = await self._get_config_via_handshake()
        config["available_sources"] = available_sources
        # Отправляем обновлённый config на сервер через PATCH
        await self._update_config_on_server(config)
        print(f"[CONFIG SYNC] Сохранено {len(available_sources)} источников в config.")

    async def _get_config_via_handshake(self):
        """Получить актуальный config с сервера через handshake."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            print(f"Getting config via handshake for connector {self.connector_id} with token {self.access_token}")
            async with session.get(
                f"{self.api_url}/connectors/{self.connector_id}/handshake",
                headers={"Authorization": f"Bearer {self.access_token}"}
            ) as resp:
                data = await resp.json()
                return data.get("current_config", {})

    async def _update_config_on_server(self, config):
        """Отправить обновлённый config на сервер через PATCH."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/connectors/{self.connector_id}/config",
                json=config,
                headers={"Authorization": f"Bearer {self.access_token}"}
            ) as resp:
                if resp.status != 200:
                    print(f"[CONFIG SYNC] Ошибка обновления config: {await resp.text()}")
                else:
                    print("[CONFIG SYNC] Config успешно обновлён на сервере.")

    async def run(self):
        try:
            if self._registration_required:
                await self.register_connector("telegram")
                self._registration_required = False
                self.connector_id = self.connector_id
                self.access_token = self.access_token
            if self._onboarding_required:
                self.connector_id = self.connector_id
                self.access_token = self.access_token
                await self.fsm_onboarding()
                self._onboarding_required = False
                print("Готово к запуску основной работы Telegram-коннектора.")
            await self.save_available_sources_to_config()
            self.config_manager = TelegramConfigManager(self.api_url, self.connector_id, self.access_token)
            self.connector = TelegramConnector(
                batch_limit=self.batch_limit,
                batch_page=self.batch_page,
                batch_sleep=self.batch_sleep,
                check_sleep=self.check_sleep,
                config_manager=self.config_manager
            )
            await self.connector.run(self.client_manager.client, self._send_message_to_api)
        except KeyboardInterrupt:
            print("\nInterrupted – shutting down.")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    async def close(self):
        """Flush every pending entry and close HTTP session."""
        # Закрываем все буферы для каждого источника
        for source, buffer in self._source_buffers.items():
            try:
                await buffer.close()
                print(f"Буфер для источника '{source}' успешно закрыт")
            except Exception as e:
                print(f"Ошибка при закрытии буфера для источника '{source}': {e}")
