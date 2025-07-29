from typing import List, Optional, Any, Dict
import os
import logging
import uuid
from datetime import datetime
from functools import lru_cache
from pydantic import BaseModel

class ChatInfo(BaseModel):
    chat_id: str
    title: Optional[str]
    connector_id: Optional[str]
    participants: Optional[List[str]]
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True

class MessageInfo(BaseModel):
    message_id: str
    chat_id: str
    author: str
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True

class SendMessageRequest(BaseModel):
    content: str
    connector_id: Optional[str] = None
    metadata: Optional[dict] = None
    provider_id: Optional[str] = None  # LLM provider to use (optional, explicit)
    model: Optional[str] = None        # Model name to use (optional, explicit)
    sources: Optional[List[str]] = None  # List of connector/source IDs to use (optional)

from mindbank_poc.core.providers.llm_chat import (
    select_llm_chat_provider_instance,
    get_llm_chat_provider_instance_by_id,
    Message as LLMMessage,
    OfflineFallbackLLMChatProvider
)
from mindbank_poc.core.models.chat import ChatModel, MessageModel
from mindbank_poc.core.repositories.chat_repository import (
    ChatRepository, 
    FileChatRepository,
    generate_chat_title,
    generate_id
)
from mindbank_poc.core.config.settings import settings
from mindbank_poc.core.agent.summarizer import generate_title

logger = logging.getLogger(__name__)

class ChatService:
    """
    Service for chat operations: listing chats, fetching history, sending messages.
    """

    def __init__(self, repository: ChatRepository):
        """Initialize the service with a repository."""
        self.repository = repository

    async def list_chats(
        self,
        connector_id: Optional[str] = None,
        participant: Optional[str] = None,
        filters: Optional[dict] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ChatInfo]:
        """
        List chats with optional filtering by connector, participant, or custom filters.
        """
        chats = self.repository.list_chats(
            limit=limit,
            offset=offset,
            connector_id=connector_id,
            participant=participant,
        )
        
        # Convert from internal model to API model
        result = []
        for chat in chats:
            result.append(ChatInfo(
                chat_id=chat.id,
                title=chat.title,
                connector_id=chat.connector_id,
                participants=chat.participants,
                metadata=chat.metadata,
            ))
        
        return result

    async def get_chat_history(
        self,
        chat_id: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[dict] = None,
        sort_order: str = "desc",
    ) -> List[MessageInfo]:
        """
        Fetch chat history (messages) for a given chat_id, with pagination and filters.
        """
        # Ensure chat exists
        chat = self.repository.get_chat(chat_id)
        if not chat:
            return []
            
        # Get messages with pagination
        messages = self.repository.list_messages(
            chat_id=chat_id,
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )
        
        # Convert from internal model to API model
        result = []
        for msg in messages:
            result.append(MessageInfo(
                message_id=msg.message_id,
                chat_id=msg.chat_id,
                author=msg.author,
                content=msg.content,
                timestamp=msg.timestamp,
                metadata=msg.metadata,
            ))
        
        return result

    async def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat and all its messages.
        
        Args:
            chat_id: ID of the chat to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        # Check if chat exists
        chat = self.repository.get_chat(chat_id)
        if not chat:
            logger.warning(f"Attempted to delete non-existent chat: {chat_id}")
            return False
            
        # Delete the chat
        return self.repository.delete_chat(chat_id)

    def _ensure_chat_exists(self, chat_id: str, content: str = "") -> ChatModel:
        """
        Ensure a chat exists, creating it if needed.
        """
        chat = self.repository.get_chat(chat_id)
        if not chat:
            # Create a new chat
            title = generate_chat_title(content)
            chat = ChatModel(
                id=chat_id,
                title=title,
                messages=[],
            )
            self.repository.save_chat(chat)
            logger.info(f"Created new chat: {chat_id} with title: {title}")
        return chat

    async def generate_title_for_chat(self, chat_id: str) -> Optional[str]:
        """
        Generate or update a title for a chat based on the first user message.
        
        Args:
            chat_id: ID of the chat to generate title for
            
        Returns:
            The generated title or None if generation failed
        """
        chat = self.repository.get_chat(chat_id)
        if not chat:
            logger.warning(f"Cannot generate title for non-existent chat: {chat_id}")
            return None
            
        # Find the first user message
        first_user_message = None
        for msg in chat.messages:
            if msg.author == "user" and not (msg.metadata and msg.metadata.get("is_system_message")):
                first_user_message = msg
                break
                
        if not first_user_message:
            logger.info(f"No user message found in chat {chat_id} to generate title from")
            return None
            
        try:
            # Generate title using LLM
            new_title = await generate_title(first_user_message.content)
            
            # Update chat title
            chat.title = new_title
            self.repository.save_chat(chat)
            
            logger.info(f"Generated title for chat {chat_id}: {new_title}")
            return new_title
        except Exception as e:
            logger.error(f"Error generating title for chat {chat_id}: {e}", exc_info=True)
            return None

    async def send_message(
        self,
        chat_id: str,
        request: SendMessageRequest,
        author: str,
    ) -> MessageInfo:
        chat = self._ensure_chat_exists(chat_id, request.content if author == "user" else "")

        if author in ("agent", "ai"):
            llm_history = [
                LLMMessage(
                    message_id=m.message_id, chat_id=m.chat_id, author=m.author,
                    content=m.content, timestamp=m.timestamp, metadata=m.metadata or {}
                )
                for m in chat.messages if m.author != "system" or not m.metadata.get("is_initial")
            ]

            # Ensure last message from user is added to history for LLM context if agent is responding
            # This is a simplified logic; robust applications might need more complex context building.
            if not llm_history or llm_history[-1].author != "user":
                 # Try to find the last user message from the request if this is an agent response to it
                if request.content: # Assuming request.content holds the user's message that the agent is responding to
                    user_message_for_llm = LLMMessage(
                        message_id=generate_id(), chat_id=chat_id, author="user",
                        content=request.content, timestamp=datetime.utcnow(), metadata=request.metadata or {}
                    )
                    llm_history.append(user_message_for_llm)
            
            provider_instance: Optional[LLMChatProvider] = None
            if request.provider_id:
                provider_instance = get_llm_chat_provider_instance_by_id(request.provider_id)
                if not provider_instance:
                    logger.warning(f"Explicit provider_id '{request.provider_id}' not found, falling back.")
            
            if not provider_instance:
                provider_instance = select_llm_chat_provider_instance(archetype="chat") # Pass relevant context if available

            if not provider_instance:
                logger.error("No LLMChatProvider instance available after selection and fallback. Using direct OfflineFallback.")
                # As a very last resort, directly use the offline fallback instance.
                # This assumes OfflineFallbackLLMChatProvider is imported.
                provider_instance = OfflineFallbackLLMChatProvider() 

            config: Dict[str, Any] = {}
            if request.model:
                config["model"] = request.model
            if request.sources: config["sources"] = request.sources
            # If chat has persistent model/connector settings, retrieve them from chat.metadata
            # Fall back to request parameters if not in chat metadata
            if not request.model and chat.metadata and chat.metadata.get("selectedModelId"):
                 config["model"] = chat.metadata["selectedModelId"]
            
            # If sources not provided explicitly, try to get from chat metadata
            if not request.sources and chat.metadata and chat.metadata.get("selectedConnectors"):
                # Handle both array of objects with id/name and array of strings
                if isinstance(chat.metadata["selectedConnectors"], list):
                    if len(chat.metadata["selectedConnectors"]) > 0:
                        if isinstance(chat.metadata["selectedConnectors"][0], dict) and "id" in chat.metadata["selectedConnectors"][0]:
                            # Extract IDs from objects
                            config["sources"] = [connector["id"] for connector in chat.metadata["selectedConnectors"]]
                        elif isinstance(chat.metadata["selectedConnectors"][0], str):
                            # Already list of IDs
                            config["sources"] = chat.metadata["selectedConnectors"]

            # --- Normalize offline-fallback routing ---
            offline_modes = {"echo", "semantic-search", "fulltext-search", "full-text-search"}
            requested_mode = config.get("model")

            if requested_mode and requested_mode in offline_modes:
                # Ensure we use offline fallback provider
                provider_instance = get_llm_chat_provider_instance_by_id("offline-fallback-llm-chat") or OfflineFallbackLLMChatProvider()
                # Re-map mode and clean model key to avoid OpenAI provider treating it as model name
                config["mode"] = "fulltext-search" if requested_mode in {"fulltext-search", "full-text-search"} else requested_mode
                config.pop("model", None)

            try:
                llm_response = await provider_instance.generate_chat_response(llm_history, config=config)
                agent_message = MessageModel(
                    message_id=llm_response.message_id or generate_id(), chat_id=chat_id,
                    author=llm_response.author, content=llm_response.content,
                    timestamp=llm_response.timestamp, metadata=llm_response.metadata,
                )
                self.repository.append_message(chat_id, agent_message)
                return MessageInfo.from_orm(agent_message)
            except Exception as e:
                logger.error(f"Error during LLM response generation with {provider_instance.__class__.__name__}: {e}", exc_info=True)
                
                # Attempt to fallback to OfflineFallbackLLMChatProvider if the primary failed
                # and the primary was not already the offline fallback itself.
                if not isinstance(provider_instance, OfflineFallbackLLMChatProvider):
                    logger.warning(f"Attempting fallback to OfflineFallbackLLMChatProvider after {provider_instance.__class__.__name__} failed.")
                    try:
                        fallback_provider = OfflineFallbackLLMChatProvider()
                        # Use a simple echo mode for fallback to avoid further complex errors
                        fallback_config = {"mode": "echo"}
                        # Ensure llm_history is correctly passed; it should be the same history.
                        llm_response = await fallback_provider.generate_chat_response(llm_history, config=fallback_config)
                        
                        agent_message = MessageModel(
                            message_id=llm_response.message_id or generate_id(), chat_id=chat_id,
                            author=llm_response.author, content=llm_response.content,
                            timestamp=llm_response.timestamp, 
                            metadata={**(llm_response.metadata or {}), "original_error": str(e), "primary_provider_failed": provider_instance.__class__.__name__}
                        )
                        self.repository.append_message(chat_id, agent_message)
                        logger.info(f"Successfully generated response using OfflineFallbackLLMChatProvider after primary failed.")
                        return MessageInfo.from_orm(agent_message)
                    except Exception as fallback_e:
                        logger.error(f"Error during OfflineFallbackLLMChatProvider execution: {fallback_e}", exc_info=True)
                        # If fallback also fails, then return the original error message.
                        error_content = f"Error: Could not get response from AI assistant. Primary provider ({provider_instance.__class__.__name__}) failed: {e}. Fallback also failed: {fallback_e}."
                else:
                    # The error was already from the OfflineFallbackLLMChatProvider, so no further fallback.
                    error_content = f"Error: Offline fallback AI assistant failed: {e}."

                error_message = MessageModel(
                    message_id=generate_id(), chat_id=chat_id, author="system",
                    content=error_content, timestamp=datetime.utcnow(),
                    metadata={"error": True, "provider_errored": provider_instance.__class__.__name__, "original_exception": str(e)}
                )
                self.repository.append_message(chat_id, error_message)
                return MessageInfo.from_orm(error_message)
        else: # User or other authors
            # If it's a system message for updating metadata, don't save a visible message content
            # The metadata update will be handled by chat.metadata directly if needed.
            is_system_update = request.metadata.get("isSystemUpdate", False) if request.metadata else False
            
            if author == "system" and is_system_update:
                # This is a metadata update, not a real message to be displayed.
                # Update chat metadata directly and save.
                chat.metadata = chat.metadata or {}
                if "selectedModelId" in request.metadata:
                    chat.metadata["selectedModelId"] = request.metadata["selectedModelId"]
                if "selectedConnectors" in request.metadata:
                    chat.metadata["selectedConnectors"] = request.metadata["selectedConnectors"]
                
                self.repository.save_chat(chat)
                logger.info(f"Updated metadata for chat {chat_id} via system message.")
                
                # Return a representation of the system event, not a message to be displayed
                # For consistency, we can return a MessageInfo, but its content won't be used by client for display
                return MessageInfo(
                    message_id=generate_id(),
                    chat_id=chat_id,
                    author="system",
                    content="Chat metadata updated", # This content won't be shown if client filters systemUpdate
                    timestamp=datetime.utcnow(),
                    metadata=request.metadata # Include the triggering metadata
                )

            # For regular user messages or non-update system messages:
            user_message_content = request.content
            # ... (rest of the logic for saving normal messages, handling initial system message for chat creation etc.)
            # Ensure that the is_initial flag logic for chat creation remains if it was separate
            # For example, the part that sets title and connector_id for a new chat based on a system message:
            if author == "system" and request.metadata and request.metadata.get("is_initial"):
                if not chat.title and request.content != "New Chat":
                    chat.title = generate_chat_title(request.content)
                if not chat.connector_id and request.connector_id:
                    chat.connector_id = request.connector_id
                if "selectedModelId" in request.metadata:
                    chat.metadata = chat.metadata or {}
                    chat.metadata["selectedModelId"] = request.metadata["selectedModelId"]
                if "selectedConnectors" in request.metadata:
                    chat.metadata = chat.metadata or {}
                    chat.metadata["selectedConnectors"] = request.metadata["selectedConnectors"]
                self.repository.save_chat(chat)
                # Still need to save the initial system message to mark the chat as created
                # The client will filter it out based on is_initial
                message_to_save = MessageModel(
                    message_id=generate_id(), chat_id=chat_id,
                    author=author, content=user_message_content,
                    timestamp=datetime.utcnow(), metadata=request.metadata or {}
                )
                self.repository.append_message(chat_id, message_to_save)
                return MessageInfo.from_orm(message_to_save)
            
            # Standard message saving logic for user messages or other system messages
            message_to_save = MessageModel(
                message_id=generate_id(), chat_id=chat_id,
                author=author, content=user_message_content,
                timestamp=datetime.utcnow(), metadata=request.metadata or {}
            )
            
            # Check if this is the first message in the chat and it's from a user
            if not chat.messages and author == "user":
                if not chat.title or chat.title == "New Chat":
                    try:
                        # Try using the LLM title generator for first message
                        new_title = await generate_title(request.content)
                        chat.title = new_title
                        logger.info(f"Generated title for chat {chat_id} from first message: {new_title}")
                    except Exception as e:
                        # Fall back to simple title generator if LLM fails
                        chat.title = generate_chat_title(request.content)
                        logger.warning(f"LLM title generation failed, using fallback: {chat.title}. Error: {e}")
                self.repository.save_chat(chat)
            
            self.repository.append_message(chat_id, message_to_save)
            return MessageInfo.from_orm(message_to_save)


@lru_cache()
def get_chat_service() -> ChatService:
    """Get or create a singleton ChatService instance."""
    # Use the path from settings
    file_path = os.path.join(settings.storage.data_dir, settings.storage.chats_file)
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    logger.debug(f"Initializing chat repository with file path: {file_path}")
    repository = FileChatRepository(file_path)
    return ChatService(repository)
