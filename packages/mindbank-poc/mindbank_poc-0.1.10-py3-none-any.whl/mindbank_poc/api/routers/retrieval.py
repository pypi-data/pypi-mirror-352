# src/mindbank_poc/api/routers/retrieval.py
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from mindbank_poc.api.schemas import AggregateInput, NormalizedUnitSchema, FilterRequest
from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.retrieval.service import get_retrieval_service, RetrievalService, SearchResultItemInternal

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"],
    responses={404: {"description": "Not found"}},
)

logger = get_logger(__name__)

# Модель запроса поиска
class SearchRequest(BaseModel):
    """Схема для запроса поиска."""
    query_text: Optional[str] = Field(
        default=None,
        description="Текст запроса для поиска"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Фильтры по метаданным"
    )
    archetype: Optional[str] = Field(
        default=None,
        description="Фильтр по архетипу"
    )
    mode: str = Field(
        default="hybrid",
        description="Режим поиска: 'semantic', 'fulltext', 'hybrid'"
    )
    limit: int = Field(
        default=10,
        description="Максимальное количество результатов"
    )

# Модель результата поиска
class SearchResultItem(BaseModel):
    """Схема для результата поиска."""
    score: float = Field(
        description="Релевантность результата (от 0 до 1)"
    )
    normalized_unit: NormalizedUnitSchema = Field(
        description="Нормализованная единица знаний"
    )
    raw_aggregate: Optional[AggregateInput] = Field(
        default=None,
        description="Исходный агрегат"
    )

# Модель ответа API поиска
class SearchResponse(BaseModel):
    """Схема для ответа API поиска."""
    results: List[SearchResultItem] = Field(
        default_factory=list,
        description="Список результатов поиска"
    )

@router.post("/search", response_model=SearchResponse)
async def search_normalized_units(
    request: SearchRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Выполняет поиск по нормализованным данным.
    
    - Можно указать текст для поиска (query_text)
    - Можно указать фильтры по метаданным (filters)
    - Можно указать фильтр по архетипу (archetype)
    - Можно выбрать режим поиска: семантический, полнотекстовый или гибридный
    - Можно ограничить количество результатов (limit)
    """
    try:
        # Вызываем сервис поиска
        internal_results: List[SearchResultItemInternal] = await retrieval_service.search(
            query_text=request.query_text,
            metadata_filters=request.filters,
            archetype=request.archetype,
            search_mode=request.mode,
            limit=request.limit
        )

        # Преобразуем внутренние результаты в схему ответа API
        api_results: List[SearchResultItem] = []
        for item in internal_results:
            # Проверяем, что агрегат был найден (на случай ошибок при загрузке)
            if item.raw_aggregate:
                 # Создаем копию NormalizedUnitSchema с уникальным ID если нужно
                 unit_schema = NormalizedUnitSchema.model_validate(item.unit)
                 
                 # Если такой aggregate_id уже был добавлен в результаты, сделаем его уникальным
                 existing_ids = [r.normalized_unit.aggregate_id for r in api_results]
                 if unit_schema.aggregate_id in existing_ids:
                     # Добавляем уникальный суффикс к ID для API ответа
                     unique_suffix = f"-{id(item.unit)}"
                     unit_schema.aggregate_id = f"{unit_schema.aggregate_id}{unique_suffix}"
                     logger.info(f"Made aggregate_id unique for API: {unit_schema.aggregate_id}")
                 
                 api_results.append(
                     SearchResultItem(
                         score=item.score,
                         normalized_unit=unit_schema,
                         raw_aggregate=item.raw_aggregate # AggregateInput уже является Pydantic схемой
                     )
                 )

        return SearchResponse(results=api_results)
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/filter", response_model=SearchResponse)
async def filter_normalized_units(
    request: FilterRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Выполняет поиск по нормализованным данным только по фильтрам без текстового запроса.
    
    - Можно указать архетип контента (архетип)
    - Можно указать источник данных (source)
    - Можно указать автора контента (author)
    - Можно указать диапазон дат создания (date_from, date_to)
    - Можно указать типы классификации (classification_types)
    - Можно указать дополнительные метаданные (custom_metadata)
    - Можно указать теги (tags)
    - Можно указать максимальное количество результатов (limit)
    - Можно указать поле и порядок сортировки (sort_by, sort_order)
    """
    try:
        # Вызываем сервис фильтрации
        internal_results: List[SearchResultItemInternal] = await retrieval_service.filter_search(
            archetype=request.archetype,
            source=request.source,
            source_name=request.source_name,
            author=request.author,
            date_from=request.date_from,
            date_to=request.date_to,
            classification_types=request.classification_types,
            custom_metadata=request.custom_metadata,
            tags=request.tags,
            limit=request.limit,
            sort_by=request.sort_by,
            sort_order=request.sort_order
        )

        # Преобразуем внутренние результаты в схему ответа API
        api_results: List[SearchResultItem] = []
        for item in internal_results:
            # Проверяем, что агрегат был найден (на случай ошибок при загрузке)
            if item.raw_aggregate:
                 # Создаем копию NormalizedUnitSchema с уникальным ID если нужно
                 unit_schema = NormalizedUnitSchema.model_validate(item.unit)
                 
                 # Если такой aggregate_id уже был добавлен в результаты, сделаем его уникальным
                 existing_ids = [r.normalized_unit.aggregate_id for r in api_results]
                 if unit_schema.aggregate_id in existing_ids:
                     # Добавляем уникальный суффикс к ID для API ответа
                     unique_suffix = f"-{id(item.unit)}"
                     unit_schema.aggregate_id = f"{unit_schema.aggregate_id}{unique_suffix}"
                     logger.info(f"Made aggregate_id unique for API: {unit_schema.aggregate_id}")
                 
                 api_results.append(
                     SearchResultItem(
                         score=item.score,
                         normalized_unit=unit_schema,
                         raw_aggregate=item.raw_aggregate # AggregateInput уже является Pydantic схемой
                     )
                 )

        return SearchResponse(results=api_results)
    except Exception as e:
        logger.error(f"Error during filter search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
