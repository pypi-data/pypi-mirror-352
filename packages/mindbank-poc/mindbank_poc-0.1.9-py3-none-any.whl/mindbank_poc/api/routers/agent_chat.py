from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from typing import List, Optional, Dict, Any
from mindbank_poc.core.services.chat_service import (
    ChatService,
    ChatInfo,
    MessageInfo,
    SendMessageRequest,
    get_chat_service,
)
from mindbank_poc.core.providers.llm_chat import get_llm_chat_providers_info_and_instance
from mindbank_poc.core.models.chat import ChatModel
from pydantic import BaseModel
import uuid


class CreateChatRequest(BaseModel):
    title: Optional[str] = None
    connector_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DeleteChatResponse(BaseModel):
    """Response model for chat deletion."""
    success: bool
    chat_id: str
    message: str


router = APIRouter(
    prefix="/agent_chat",
    tags=["agent_chat"],
)

@router.get("/providers")
async def list_llm_chat_providers():
    """
    List all available LLMChatProviders and their supported models/configs.
    """
    providers_with_instances = get_llm_chat_providers_info_and_instance()
    result = []
    for p_data in providers_with_instances:
        info = p_data["info"]
        # Extract models and default_model from config or info
        models = info.get("current_config", {}).get("models") or [info.get("current_config", {}).get("model")] if info.get("current_config", {}).get("model") else []
        default_model = info.get("current_config", {}).get("default_model") or (models[0] if models else None)
        
        # Ensure models is always a list
        if isinstance(models, str): # if only one model string is provided
            models = [models]
        elif models is None:
            models = []
            
        result.append({
            "id": info.get("id"),
            "name": info.get("name"),
            "models": models,
            "default_model": default_model,
            "config_schema": info.get("config_schema", {}),
        })
    return result

@router.post("/create", response_model=ChatInfo)
async def create_chat(
    request: CreateChatRequest = Body(...),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Create a new chat/thread directly without an initial system message.
    The title and metadata are taken from the request.
    """
    chat_id = str(uuid.uuid4())
    
    # Directly create or get chat using a new/modified service method
    # For now, we'll adapt by creating a ChatModel and saving it.
    # Ideally, ChatService would have a method like `create_empty_chat`.
    
    chat_model = ChatModel(
        id=chat_id,
        title=request.title or "New Chat", # Use provided title or default
        connector_id=request.connector_id, # Persist connector_id if provided
        messages=[], # No initial system message
        metadata=request.metadata or {} # Persist metadata (selectedModelId, etc.)
    )
    
    saved_chat_model = chat_service.repository.save_chat(chat_model)
    
    if not saved_chat_model:
        raise HTTPException(status_code=500, detail="Failed to create and save chat directly.")

    # Convert to ChatInfo for the response
    # Ensure all fields match ChatInfo model
    return ChatInfo(
        chat_id=saved_chat_model.id,
        title=saved_chat_model.title,
        connector_id=saved_chat_model.connector_id,
        participants=saved_chat_model.participants, # Assuming participants is part of ChatModel or defaults to empty
        metadata=saved_chat_model.metadata
    )

@router.get("/list", response_model=List[ChatInfo])
async def list_chats(
    connector_id: Optional[str] = Query(None),
    participant: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    List chats with optional filtering by connector or participant.
    """
    return await chat_service.list_chats(
        connector_id=connector_id,
        participant=participant,
        limit=limit,
        offset=offset,
    )

@router.get("/{chat_id}/history", response_model=List[MessageInfo])
async def get_chat_history(
    chat_id: str = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Fetch chat history (messages) for a given chat_id, with pagination and sorting.
    """
    return await chat_service.get_chat_history(
        chat_id=chat_id,
        limit=limit,
        offset=offset,
        sort_order=sort_order,
    )

@router.post("/{chat_id}/send", response_model=MessageInfo)
async def send_message(
    chat_id: str = Path(...),
    request: SendMessageRequest = None,
    author: str = Query(..., description="Author of the message (agent or user)"),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Send a message to a chat as the agent or user.
    """
    if request is None:
        raise HTTPException(status_code=400, detail="Request body required")
    
    try:
        return await chat_service.send_message(
            chat_id=chat_id,
            request=request,
            author=author,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{chat_id}", response_model=DeleteChatResponse)
async def delete_chat(
    chat_id: str = Path(..., description="The ID of the chat to delete"),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Delete a chat and all its messages.
    
    Args:
        chat_id: The ID of the chat to delete
        
    Returns:
        DeleteChatResponse indicating success or failure
    """
    try:
        success = await chat_service.delete_chat(chat_id)
        
        if success:
            return DeleteChatResponse(
                success=True,
                chat_id=chat_id,
                message="Chat successfully deleted"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Chat with ID {chat_id} not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat: {str(e)}"
        )
