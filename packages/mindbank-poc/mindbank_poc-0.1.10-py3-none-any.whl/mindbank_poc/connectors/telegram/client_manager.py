import json
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from pydantic import BaseModel


class Dialog(BaseModel):
    chat_id: int
    username: str
    title: str
    chat_type: str
    last_message_id: int


class ClientSchema(BaseModel):
    api_id: int
    api_hash: str
    session_string: str
    dialogs: list[Dialog]


class ClientManager:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.client = None
        self._init_client()

    def _init_client(self):
        api_id = self.state_manager.get("api_id")
        api_hash = self.state_manager.get("api_hash")
        session_string = self.state_manager.get("session_string", "")
        if api_id and api_hash:
            self.client = TelegramClient(StringSession(session_string), int(api_id), str(api_hash))

    async def set_api_id_hash(self, api_id: int, api_hash: str):
        self.state_manager.set("api_id", int(api_id))
        self.state_manager.set("api_hash", str(api_hash))
        self._init_client()

    async def set_phone(self, phone: str):
        self.state_manager.set("phone", phone)
        self._init_client()

    async def send_code_request(self):
        phone = self.state_manager.get("phone")
        if not self.client or not phone:
            raise ValueError("Client or phone not set")
        await self.client.connect()
        await self.client.send_code_request(phone)
        await self.client.disconnect()

    async def sign_in_with_code(self, code: str):
        """
            Регистрация с кодом.
            Возвращает True, если регистрация прошла успешно, False, если требуется ввод пароля.
        """
        phone = self.state_manager.get("phone")
        if not self.client or not phone:
            raise ValueError("Client or phone not set")
        await self.client.connect()
        try:
            if not await self.client.is_user_authorized():
                await self.client.sign_in(phone=phone, code=code)
            session_string = self.client.session.save()
            self.state_manager.set("session_string", session_string)
            await self.client.disconnect()
            return True
        except Exception as e:
            from telethon.errors import SessionPasswordNeededError
            if isinstance(e, SessionPasswordNeededError) or "password is required" in str(e) or "SESSION_PASSWORD_NEEDED" in str(e):
                await self.client.disconnect()
                return False
            await self.client.disconnect()
            return f"error: {str(e)}"

    async def sign_in_with_password(self, password: str):
        phone = self.state_manager.get("phone")
        if not self.client or not phone:
            raise ValueError("Client or phone not set")
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.sign_in(phone=phone, password=password)
        session_string = self.client.session.save()
        self.state_manager.set("session_string", session_string)
        await self.client.disconnect()

    def get_session_string(self):
        return self.state_manager.get("session_string")

    async def get_dialogs(self):
        await self.client.connect()
        dialogs = await self.client.get_dialogs()
        await self.client.disconnect()
        dialog_objs = [
            Dialog(
                chat_id=dialog.id,
                username=dialog.name,
                title=dialog.title,
                chat_type=dialog.entity.__class__.__name__.lower(),
                last_message_id=str(dialog.message.id) if dialog.message else 0,
            ) for dialog in dialogs
        ]
        self.state_manager.set("dialogs", [d.model_dump() for d in dialog_objs])
        return dialog_objs

    async def save(self):
        # Сохраняет все актуальные данные в state_manager (dialogs уже сохраняются в get_dialogs)
        pass
