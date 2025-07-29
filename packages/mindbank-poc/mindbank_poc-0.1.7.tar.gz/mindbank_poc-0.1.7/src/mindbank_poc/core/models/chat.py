from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class MessageModel(BaseModel):
    """Internal message model for chat persistence."""
    message_id: str = Field(..., description="Unique message ID")
    chat_id: str = Field(..., description="Associated chat ID")
    author: str = Field(..., description="Author of the message (user/agent)")
    content: str = Field(..., description="Raw content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class ChatModel(BaseModel):
    """Internal chat model for repository storage."""
    id: str = Field(..., description="Chat/thread unique identifier")
    title: Optional[str] = Field(default=None, description="Display title of chat")
    connector_id: Optional[str] = Field(default=None, description="Primary connector/source id")
    participants: List[str] = Field(default_factory=list, description="Participants identifiers")
    messages: List[MessageModel] = Field(default_factory=list, description="Messages in chronological order")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    @validator("messages", pre=True, each_item=False)
    def ensure_sorted(cls, v):
        """Ensure messages are sorted by timestamp ascending."""
        if isinstance(v, list):
            return sorted(v, key=lambda m: m["timestamp"] if isinstance(m, dict) else getattr(m, "timestamp", 0))
        return v 