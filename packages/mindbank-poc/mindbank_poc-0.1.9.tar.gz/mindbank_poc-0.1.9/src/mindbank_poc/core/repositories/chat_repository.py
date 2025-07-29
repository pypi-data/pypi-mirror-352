"""
Repository for chat and message persistence.
"""
import os
import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from mindbank_poc.core.models.chat import ChatModel, MessageModel

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class ChatRepository(ABC):
    """Abstract base class for chat repositories."""

    @abstractmethod
    def list_chats(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        connector_id: Optional[str] = None,
        participant: Optional[str] = None
    ) -> List[ChatModel]:
        """List chats with optional filtering."""
        pass

    @abstractmethod
    def get_chat(self, chat_id: str) -> Optional[ChatModel]:
        """Get a chat by ID."""
        pass

    @abstractmethod
    def save_chat(self, chat: ChatModel) -> ChatModel:
        """Save or update a chat."""
        pass

    @abstractmethod
    def append_message(self, chat_id: str, message: MessageModel) -> Optional[ChatModel]:
        """Add a message to an existing chat."""
        pass

    @abstractmethod
    def list_messages(
        self, 
        chat_id: str, 
        limit: int = 50, 
        offset: int = 0,
        sort_order: str = "desc"
    ) -> List[MessageModel]:
        """List messages for a chat with pagination."""
        pass
        
    @abstractmethod
    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and all its messages."""
        pass


class FileChatRepository(ChatRepository):
    """File-based implementation of ChatRepository."""

    def __init__(self, file_path: str):
        """Initialize the repository with a file path."""
        self.file_path = os.path.abspath(file_path)
        self._chats: Dict[str, ChatModel] = {}
        self._load_chats()

    def _load_chats(self) -> None:
        """Load chats from file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._chats = {
                        k: ChatModel.parse_obj(v) for k, v in data.items()
                    }
                logger.info(f"Loaded {len(self._chats)} chats from {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load chats from {self.file_path}: {e}")
                self._chats = {}
        else:
            logger.info(f"Chat file {self.file_path} not found, creating empty repository")
            self._chats = {}
            self._save_chats()

    def _save_chats(self) -> None:
        """Save chats to file."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            logger.debug(f"Attempting to save chats to file: {self.file_path}")
            
            # Convert ChatModel objects to dictionaries
            serializable = {k: v.dict() for k, v in self._chats.items()}
            
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
                
            logger.info(f"Saved {len(serializable)} chats to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save chats to {self.file_path}: {e}", exc_info=True)

    def list_chats(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        connector_id: Optional[str] = None,
        participant: Optional[str] = None
    ) -> List[ChatModel]:
        """List chats with optional filtering."""
        # Apply filters
        filtered_chats = self._chats.values()
        
        if connector_id:
            filtered_chats = [c for c in filtered_chats if c.connector_id == connector_id]
            
        if participant:
            filtered_chats = [c for c in filtered_chats if participant in c.participants]
        
        # Sort by most recent message (or creation date if no messages)
        sorted_chats = sorted(
            filtered_chats,
            key=lambda c: c.messages[-1].timestamp if c.messages else datetime.min,
            reverse=True  # Most recent first
        )
        
        # Apply pagination
        paginated = sorted_chats[offset:offset + limit]
        return paginated

    def get_chat(self, chat_id: str) -> Optional[ChatModel]:
        """Get a chat by ID."""
        return self._chats.get(chat_id)

    def save_chat(self, chat: ChatModel) -> ChatModel:
        """Save or update a chat."""
        self._chats[chat.id] = chat
        self._save_chats()
        return chat

    def append_message(self, chat_id: str, message: MessageModel) -> Optional[ChatModel]:
        """Add a message to an existing chat."""
        chat = self.get_chat(chat_id)
        if chat:
            chat.messages.append(message)
            # Re-sort messages by timestamp
            chat.messages = sorted(chat.messages, key=lambda m: m.timestamp)
            self._save_chats()
            return chat
        return None

    def list_messages(
        self, 
        chat_id: str, 
        limit: int = 50, 
        offset: int = 0,
        sort_order: str = "desc"
    ) -> List[MessageModel]:
        """List messages for a chat with pagination."""
        chat = self.get_chat(chat_id)
        if not chat:
            return []
            
        # Sort messages
        if sort_order.lower() == "asc":
            sorted_messages = sorted(chat.messages, key=lambda m: m.timestamp)
        else:  # Default to desc
            sorted_messages = sorted(chat.messages, key=lambda m: m.timestamp, reverse=True)
            
        # Apply pagination
        paginated = sorted_messages[offset:offset + limit]
        return paginated
        
    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat and all its messages.
        
        Args:
            chat_id: ID of the chat to delete
            
        Returns:
            True if deletion was successful, False if chat not found
        """
        if chat_id not in self._chats:
            logger.warning(f"Attempted to delete non-existent chat: {chat_id}")
            return False
            
        # Remove the chat from the dictionary
        del self._chats[chat_id]
        
        # Save the changes to file
        self._save_chats()
        
        logger.info(f"Successfully deleted chat: {chat_id}")
        return True


def generate_chat_title(first_message_content: str) -> str:
    """Generate a chat title based on the first message content."""
    # For PoC, just use a simple truncated version of the message
    if not first_message_content:
        return "New Chat"
        
    # Simple truncation
    max_length = 30
    title = first_message_content.strip()
    if len(title) > max_length:
        title = title[:max_length - 3] + "..."
    return title


def generate_id() -> str:
    """Generate a random UUID for chat/message IDs."""
    return str(uuid.uuid4())