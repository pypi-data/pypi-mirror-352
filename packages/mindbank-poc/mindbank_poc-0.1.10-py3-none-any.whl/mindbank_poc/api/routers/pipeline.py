"""
Роутер для API визуализации и мониторинга пайплайна данных.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from mindbank_poc.core.models.access_token import AccessTokenType
from mindbank_poc.api.routers.access_tokens import get_current_token, require_token_type
from mindbank_poc.core.common.types import ArchetypeType

# Создаем роутер
router = APIRouter(
    prefix="/api/pipeline",
    tags=["Pipeline"],
    responses={404: {"description": "Not found"}},
)

# Модели данных для API
class ConnectorStatus(BaseModel):
    """Статус коннектора в пайплайне."""
    connector_id: str
    name: str
    status: str
    last_activity: datetime
    processed_entries: int
    error_count: int
    supported_archetypes: List[str] = []

class AggregateTypeStats(BaseModel):
    """Статистика по типу агрегата."""
    archetype: str
    count: int
    last_processed: Optional[datetime] = None

class PipelineOverview(BaseModel):
    """Обзор пайплайна данных."""
    active_connectors: List[ConnectorStatus]
    aggregate_types: List[AggregateTypeStats]
    total_raw_entries: int
    total_aggregates: int
    total_normalized_units: int

class ProcessingEvent(BaseModel):
    """Событие обработки данных."""
    event_id: str
    event_type: str
    timestamp: datetime
    connector_id: Optional[str] = None
    aggregate_id: Optional[str] = None
    archetype: Optional[str] = None
    details: Dict[str, Any] = {}

class PipelineStatus(BaseModel):
    """Статус пайплайна данных."""
    period_start: datetime
    period_end: datetime
    total_processed: int
    processing_rate: float  # entries per minute
    error_rate: float  # percentage
    processing_times: Dict[str, float]  # average processing time by stage in seconds
    queue_size: int

class PipelineEventsResponse(BaseModel):
    """Ответ с событиями пайплайна."""
    events: List[ProcessingEvent]

# Временные данные для PoC
MOCK_CONNECTORS_STATUS = [
    {
        "connector_id": "5bc74933-0601-4399-b85b-6d0452475703",
        "name": "Google Meet Connector",
        "status": "active",
        "last_activity": datetime.now() - timedelta(minutes=15),
        "processed_entries": 120,
        "error_count": 2,
        "supported_archetypes": ["meeting_notes", "transcription"]
    },
    {
        "connector_id": "bbba6dcb-cd58-4d29-acca-019c97de77e9",
        "name": "File System Connector",
        "status": "active",
        "last_activity": datetime.now() - timedelta(hours=1),
        "processed_entries": 45,
        "error_count": 0,
        "supported_archetypes": ["document", "note", "code_snippet"]
    }
]

MOCK_AGGREGATE_STATS = [
    {
        "archetype": "meeting_notes",
        "count": 78,
        "last_processed": datetime.now() - timedelta(minutes=15)
    },
    {
        "archetype": "document",
        "count": 32,
        "last_processed": datetime.now() - timedelta(hours=1)
    },
    {
        "archetype": "note",
        "count": 13,
        "last_processed": datetime.now() - timedelta(hours=2)
    }
]

MOCK_PIPELINE_STATUS = {
    "period_start": datetime.now() - timedelta(hours=24),
    "period_end": datetime.now(),
    "total_processed": 165,
    "processing_rate": 6.875,  # entries per minute
    "error_rate": 1.2,  # percentage
    "processing_times": {
        "aggregation": 0.5,  # seconds
        "normalization": 2.3,  # seconds
        "embedding": 1.8,  # seconds
        "classification": 1.2  # seconds
    },
    "queue_size": 5
}

MOCK_EVENTS = [
    {
        "event_id": "evt-001",
        "event_type": "raw_entry_received",
        "timestamp": datetime.now() - timedelta(minutes=15),
        "connector_id": "5bc74933-0601-4399-b85b-6d0452475703",
        "details": {
            "entry_id": "entry-123",
            "type": "text"
        }
    },
    {
        "event_id": "evt-002",
        "event_type": "aggregate_created",
        "timestamp": datetime.now() - timedelta(minutes=14),
        "connector_id": "5bc74933-0601-4399-b85b-6d0452475703",
        "aggregate_id": "agg-456",
        "archetype": "meeting_notes",
        "details": {
            "entries_count": 5
        }
    },
    {
        "event_id": "evt-003",
        "event_type": "normalization_completed",
        "timestamp": datetime.now() - timedelta(minutes=13),
        "aggregate_id": "agg-456",
        "archetype": "meeting_notes",
        "details": {
            "normalized_units": 3,
            "processing_time_ms": 1250
        }
    }
]

@router.get("/overview", response_model=PipelineOverview)
async def get_pipeline_overview(token: dict = Depends(get_current_token)):
    """
    Получение обзора пайплайна данных.
    """
    # В реальной системе здесь должна быть логика получения данных из базы
    return {
        "active_connectors": MOCK_CONNECTORS_STATUS,
        "aggregate_types": MOCK_AGGREGATE_STATS,
        "total_raw_entries": 250,
        "total_aggregates": 123,
        "total_normalized_units": 180
    }

@router.get("/status", response_model=PipelineStatus)
async def get_pipeline_status(
    period: int = Query(24, description="Период в часах для статистики"),
    token: dict = Depends(get_current_token)
):
    """
    Получение статуса пайплайна данных за указанный период.
    """
    # В реальной системе здесь должна быть логика получения данных из базы
    # с учетом указанного периода
    mock_status = dict(MOCK_PIPELINE_STATUS)
    mock_status["period_start"] = datetime.now() - timedelta(hours=period)
    
    return mock_status

@router.get("/events", response_model=PipelineEventsResponse)
async def get_pipeline_events(
    limit: int = Query(10, description="Максимальное количество событий"),
    offset: int = Query(0, description="Смещение для пагинации"),
    event_type: Optional[str] = Query(None, description="Фильтр по типу события"),
    connector_id: Optional[str] = Query(None, description="Фильтр по ID коннектора"),
    archetype: Optional[ArchetypeType] = Query(None, description="Фильтр по архитипу"),
    token: dict = Depends(get_current_token)
):
    """
    Получение событий пайплайна данных с возможностью фильтрации.
    """
    # В реальной системе здесь должна быть логика получения данных из базы
    # с учетом указанных фильтров и пагинации
    
    # Применяем фильтры
    filtered_events = MOCK_EVENTS
    
    if event_type:
        filtered_events = [e for e in filtered_events if e["event_type"] == event_type]
    
    if connector_id:
        filtered_events = [e for e in filtered_events if e.get("connector_id") == connector_id]
    
    if archetype:
        filtered_events = [e for e in filtered_events if e.get("archetype") == archetype]
    
    # Применяем пагинацию
    paginated_events = filtered_events[offset:offset + limit]
    
    return {"events": paginated_events}
