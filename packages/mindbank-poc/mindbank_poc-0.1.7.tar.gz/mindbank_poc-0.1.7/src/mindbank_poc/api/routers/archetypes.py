"""
API роутер для управления архитипами.
"""
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from mindbank_poc.core.common.types import ArchetypeType
from mindbank_poc.core.services.archetype_service import get_archetype_service, ArchetypeService, ArchetypeInfo

router = APIRouter(
    prefix="/api/archetypes",
    tags=["archetypes"],
    responses={404: {"description": "Not found"}},
)

# Модель для ответа с информацией об архитипе
class ArchetypeResponse(BaseModel):
    """Схема для ответа с информацией об архитипе."""
    name: str = Field(description="Название архитипа")
    description: str = Field(description="Описание архитипа")
    is_system: bool = Field(description="Является ли архитип системным")
    usage_count: int = Field(default=0, description="Количество использований")
    last_used: Optional[str] = Field(default=None, description="Последнее использование (ISO формат)")

@router.get("/", response_model=List[ArchetypeResponse])
async def get_archetypes(
    archetype_service: ArchetypeService = Depends(get_archetype_service)
):
    """
    Получить список всех доступных архитипов.
    """
    archetypes = archetype_service.get_all_archetypes()
    
    # Преобразуем в формат ответа API
    result = []
    for archetype in archetypes:
        result.append(ArchetypeResponse(
            name=archetype.name,
            description=archetype.description,
            is_system=archetype.is_system,
            usage_count=archetype.usage_count,
            last_used=archetype.last_used.isoformat() if archetype.last_used else None
        ))
    
    return result

@router.get("/{name}", response_model=ArchetypeResponse)
async def get_archetype(
    name: str,
    archetype_service: ArchetypeService = Depends(get_archetype_service)
):
    """
    Получить информацию о конкретном архитипе.
    """
    archetype = archetype_service.get_archetype_info(name)
    
    if not archetype:
        raise HTTPException(
            status_code=404,
            detail=f"Архитип с именем '{name}' не найден"
        )
    
    return ArchetypeResponse(
        name=archetype.name,
        description=archetype.description,
        is_system=archetype.is_system,
        usage_count=archetype.usage_count,
        last_used=archetype.last_used.isoformat() if archetype.last_used else None
    )
