"""
Telegram connector for processing messages from Telegram channels

This connector monitors specified Telegram channels and sends their messages to Ingest API.
"""
import asyncio
from typing import Dict, List, Any, AsyncGenerator, Callable, Awaitable, Optional

from telethon.tl.types import MessageService
from telethon import events
from telethon.client import TelegramClient
from .constants import (
    BATCH_LIMIT, BATCH_PAGE, BATCH_SLEEP,
    CONFIG_CHECK_SLEEP
)
import aiohttp

class TelegramConfigManager:
    """
    Класс для управления конфигурацией Telegram-коннектора через API (без локального файла).
    Работает только с available_sources, получаемыми и отправляемыми через сервер.
    """
    def __init__(self, api_url, connector_id, access_token):
        self.api_url = api_url
        self.connector_id = connector_id
        self.access_token = access_token
        self.config = {}
        self.is_changed = False

    async def fetch_config(self):
        """Получить config с сервера (через handshake)."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/connectors/{self.connector_id}/handshake",
                headers={"Authorization": f"Bearer {self.access_token}"}
            ) as resp:
                data = await resp.json()
                new_config = data.get("current_config", {})
                if self.config != new_config:
                    self.is_changed = True
                self.config = new_config
        return self.config

    async def update_config(self, new_config=None):
        """Отправить config на сервер (через POST /config)."""
        if new_config is not None and self.config != new_config:
            self.config = new_config
            self.is_changed = True
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/connectors/{self.connector_id}/config",
                json=self.config,
                headers={"Authorization": f"Bearer {self.access_token}"}
            ) as resp:
                if resp.status != 200:
                    print(f"[CONFIG SYNC] Ошибка обновления config: {await resp.text()}")
                else:
                    print("[CONFIG SYNC] Config успешно обновлён на сервере.")

    def get_available_sources(self):
        return self.config.get("available_sources", [])

    def set_available_sources(self, sources):
        self.config["available_sources"] = sources

    def update_source_status(self, source_id, monitoring_status=None, fetching_status=None, anchor_id=None):
        """Обновить monitoring_status, fetching_status и anchor_id для источника по id."""
        sources = self.get_available_sources()
        for src in sources:
            if src["id"] == source_id:
                if monitoring_status is not None:
                    src["monitoring_status"] = monitoring_status
                if fetching_status is not None:
                    src["fetching_status"] = fetching_status
                if anchor_id is not None:
                    src["anchor_id"] = anchor_id
        self.set_available_sources(sources)

    def find_source(self, source_id):
        """Найти источник по id."""
        for src in self.get_available_sources():
            if src["id"] == source_id:
                return src
        return None
    
    def is_config_changed(self):
        """Проверить, изменился ли config."""
        self.is_changed = False
        return self.is_changed

class TelegramConnector:
    """
    Base connector for Telegram that handles API communication and message processing.
    """
    
    def __init__(
        self,
        batch_limit: int = BATCH_LIMIT,
        batch_page: int = BATCH_PAGE,
        batch_sleep: float = BATCH_SLEEP,
        check_sleep: float = CONFIG_CHECK_SLEEP,
        config_manager: 'TelegramConfigManager' = None,
    ):
        """
        Initialize Telegram connector.
        Args:
            batch_limit: Maximum number of messages per batch
            batch_page: Number of messages per API request
            batch_sleep: Sleep duration between API requests
            check_sleep: Sleep duration between config checks
            config_manager: Экземпляр TelegramConfigManager (API-версия)
            sources: List of sources to monitor (для обратной совместимости)
        """
        self.batch_limit = batch_limit
        self.batch_page = batch_page
        self.batch_sleep = batch_sleep
        self.check_sleep = check_sleep
        self.config_manager = config_manager
        # Runtime state
        self.client = None
        self.anchor: Dict[int, int] = {}     # first live message id per source
        self._active_sources = set()        # ids we are listening to
        self._source_names: Dict[int, str] = {}

    def _get_media_type(self, message: Any) -> Optional[str]:
        """Determine media type from message."""
        if not message.media or hasattr(message.media, 'webpage'):
            return None

        if hasattr(message.media, 'photo'):
            return "photo"
            
        if hasattr(message.media, 'document'):
            if hasattr(message.media.document, 'mime_type'):
                mime_type = message.media.document.mime_type
                if mime_type.startswith('video/'):
                    return "video"
                elif mime_type.startswith('audio/'):
                    return "voice"
                else:
                    return "document"
                    
        return None

    async def _get_dialog_map(self) -> Dict[str, Any]:
        """Возвращает отображение <идентификатор источника> -> dialog.

        В качестве идентификатора используется:
        1. username (если задан)
        2. название чата (title / name)
        Все ключи приводятся к нижнему регистру для унифицированного поиска.
        """
        dialogs = await self.client.get_dialogs()
        dialog_map: Dict[str, Any] = {}
        for dialog in dialogs:
            # username
            if hasattr(dialog.entity, "username") and dialog.entity.username:
                dialog_map[dialog.entity.username.lower()] = dialog
            # title / name (для приватных источников без username)
            name_val = getattr(dialog, "name", None) or getattr(dialog.entity, "title", None)
            if name_val:
                dialog_map[name_val.lower()] = dialog
            # Сохраняем ID источника
            if hasattr(dialog.entity, "id"):
                self._source_names[dialog.entity.id] = name_val or dialog.entity.username
                # print(f"Found source: {name_val or dialog.entity.username} with ID {dialog.entity.id}")
        return dialog_map

    async def _setup_message_handler(self, message_callback: Callable[[str, Any, Any], Awaitable[None]]) -> None:
        print(f"Setting up message handler for {len(self._active_sources)} sources")
        """Setup global message handler."""
        async def _callback(ev):
            try:
                chat = await ev.get_chat()
                if not hasattr(chat, "id"):
                    return
                source_id = chat.id

                if source_id not in self._active_sources:
                    return
                print(f"Received message from source ID: {source_id}")
                # Получаем оригинальное название источника
                source_name = self._source_names.get(source_id)
                if not source_name:
                    source_name = getattr(chat, "username", None) or getattr(chat, "title", None) or str(source_id)
                    self._source_names[source_id] = source_name
                # Log message content
                content_type = self._get_media_type(ev.message)
                if content_type:
                    print(f"[LIVE {source_name}] {ev.id}: MEDIA Type={content_type}")
                else:
                    snippet = getattr(ev.message, 'text', getattr(ev.message, 'message', ''))
                    print(f"[LIVE {source_name}] {ev.id}: {snippet[:40]}")
                self.anchor.setdefault(source_id, ev.id)
                await message_callback(source_name, ev.message, self.client)
            except Exception as e:
                print(f"Error in handler: {e}")

        self.client.add_event_handler(_callback, events.NewMessage(incoming=True, outgoing=True))

    async def refresh_handlers(self, sources: List[dict]) -> None:
        """Update active sources list."""
        self._active_sources = set()
        for source_config in sources:
            if "id" in source_config and source_config.get("monitoring_status") == "monitored":
                source_id = source_config["id"]
                self._active_sources.add(int(source_id))
                print(f"Added source ID {source_id} to active sources")

    async def batch_fetch(self, source: Any, anchor_id: int = None, reverse: bool = True) -> AsyncGenerator[Any, None]:
        """Возвращает сообщения из диапазона [start_id, anchor_id] по одному.

        После каждых 10 сообщений делает паузу batch_sleep.
        """
        print(f"[batch_fetch] start for source={source}, anchor_id={anchor_id}")
        try:
            entity = await self.client.get_input_entity(int(source))
        except Exception:
            return

        start_id = 1
        if anchor_id is not None:
            start_id = max(anchor_id - self.batch_limit + 1, 1)

        count = 0
        async for msg in self.client.iter_messages(
            entity,
            reverse=True,
            min_id=start_id - 1 if start_id > 1 else 0,
            max_id=anchor_id if anchor_id else 0,
            limit=self.batch_limit
        ):
            if isinstance(msg, MessageService):
                continue
            content_type = self._get_media_type(msg)
            if content_type:
                print(f"[BATCH {source}] {msg.id}: MEDIA Type={content_type}")
            else:
                snippet = getattr(msg, 'text', getattr(msg, 'message', ''))
                print(f"[BATCH {source}] {msg.id}: {snippet[:40]}")
            yield msg
            count += 1
            if count % 10 == 0:
                print(f"[batch_fetch] sleep after {count} messages")
                await asyncio.sleep(self.batch_sleep)

    async def get_anchor_id(self, meta: dict) -> int:
        """
        Получает anchor_id для источника. Если anchor_id не задан, определяет самый новый id источника.
        Возвращает anchor_id или 0, если не удалось определить.
        """
        anchor = meta.get("anchor_id") or self.anchor.get(meta.get("id"))
        if anchor:
            return anchor
        source_id = meta.get("id")
        if not source_id:
            return 0
        try:
            latest = await self.client.get_messages(source_id, limit=1)
            if latest:
                anchor = latest[0].id
                meta["anchor_id"] = anchor
                await self.config_manager.update_config()
                print(f"Anchor for source {meta.get('id')} set to {anchor}")
                self.config_manager.update_source_status(source_id, anchor_id=anchor)
                return anchor
        except Exception as e:
            print(f"Cannot determine anchor for {meta.get('id')}: {e}")
        return 0

    async def _process_batch_fetch(self, src: str, meta: dict, message_callback: Callable[[str, Any, Any], Awaitable[None]]) -> None:
        """Process batch fetch for a single source."""
        anchor = await self.get_anchor_id(meta)
        print(f"[PROCESS BATCH FETCH] anchor: {anchor}")
        if not anchor:
            return
        source_id = meta.get("id")
        if not source_id:
            return
        async for message in self.batch_fetch(source_id, anchor):
            await message_callback(src, message, self.client)
            content_type = self._get_media_type(message)
            if content_type:
                print(f"[BATCH {src}] {message.id}: MEDIA Type={content_type}")
            else:
                snippet = getattr(message, 'text', getattr(message, 'message', ''))
                print(f"[BATCH {src}] {message.id}: {snippet[:40]}")
        self.config_manager.update_source_status(source_id, fetching_status="fetched")
        await self.config_manager.update_config()

    async def _process_config_changes(self, message_callback: Callable[[str, Any, Any], Awaitable[None]]) -> None:
        """Process configuration changes."""
        await self.config_manager.fetch_config()
        if not self.config_manager.is_changed:
            return
        print("Config was changed")
        config = self.config_manager.config
        available_sources = config.get("available_sources")
        # Если available_sources пустой или отсутствует, выгружаем все источники через self.save_all_available_sources()
        if not available_sources:
            print("[CONFIG SYNC] available_sources пустой, выгружаем все источники через TelegramConnector...")
            await self.save_all_available_sources()
            # После выгрузки обновляем конфиг
            await self.config_manager.fetch_config()
            available_sources = self.config_manager.config.get("available_sources")
        sources = self.config_manager.get_available_sources()
        await self.refresh_handlers(sources)
        for source in sources:
            if source.get("fetching_status") == "fetching":
                print(f"[PROCESS CONFIG CHANGES] fetching source: {source['name']}")
                await self._process_batch_fetch(source["name"], source, message_callback)
        self.config_manager.is_changed = False

    async def run(self, client: TelegramClient, message_callback: Callable[[str, Any, Any], Awaitable[None]]) -> None:
        """
        Run the connector.
        
        Args:
            message_callback: Async callback function that will be called for each message
                            with signature (source: str, message: Any, client: Any) -> None
        """
        try:
            # Initialize Telegram client
            await client.connect()
            self.client = client
            # Инициализируем конфигурацию и активные источники
            await self.config_manager.fetch_config()
                
            sources = self.config_manager.get_available_sources()
            await self.refresh_handlers(sources)
            
            # Setup message handler
            await self._setup_message_handler(message_callback)
            
            while True:
                await self._process_config_changes(message_callback)
                await asyncio.sleep(self.check_sleep)

        except KeyboardInterrupt:
            print("\nInterrupted – shutting down.")
        except Exception as e:
            print(f"Error: {e}")
            raise

    @property
    def sources(self) -> list:
        """Возвращает список источников, которые отслеживает коннектор."""
        return list(self.config_manager.get_available_sources())

    async def save_all_available_sources(self):
        """
        Получает все доступные диалоги пользователя через self.client (Telethon),
        формирует available_sources и отправляет их в config на сервер через config_manager.
        """
        print("[CONFIG SYNC] Получение всех доступных диалогов Telegram через TelegramConnector...")
        await self.client.connect()
        dialogs = await self.client.get_dialogs()
        available_sources = []
        for d in dialogs:
            available_sources.append({
                "id": d.entity.id,
                "name": getattr(d, "name", None) or getattr(d.entity, "title", None),
                "monitoring_status": "inactive",
                "fetching_status": "inactive",
                "anchor_id": None
            })
        await self.client.disconnect()
        # Получаем актуальный config с сервера через config_manager
        config = await self.config_manager.fetch_config()
        config["available_sources"] = available_sources
        # Отправляем обновлённый config на сервер через config_manager
        await self.config_manager.update_config(config)
        print(f"[CONFIG SYNC] Сохранено {len(available_sources)} источников в config через TelegramConnector.")
