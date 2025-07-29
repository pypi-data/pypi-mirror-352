"""
Модели данных для нормализованных единиц.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NormalizedUnit(BaseModel):
    """
    Модель нормализованной единицы знаний.
    Представляет собой результат обработки агрегата в единую единицу,
    готовую для сохранения в базу знаний.
    """
    aggregate_id: str = Field(
        description="Идентификатор исходного агрегата"
    )
    text_repr: str = Field(
        description="Текстовое представление содержимого"
    )
    vector_repr: Optional[List[float]] = Field(
        default=None,
        description="Векторное представление для поиска по семантике"
    )
    archetype: Optional[str] = Field(
        default=None,
        description="Семантический тип (архитип) контента"
    )
    classification: Dict[str, Any] = Field(
        default_factory=dict,
        description="Классификация контента по типу, теме и другим параметрам"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Метаданные единицы знаний"
    )
    normalized_at: datetime = Field(
        default_factory=datetime.now,
        description="Время нормализации"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "aggregate_id": "group-12345",
                "text_repr": "Текстовое представление контента, возможно получено через транскрипцию или описание",
                "vector_repr": [0.1, 0.2, 0.3, 0.4, 0.5],  # Может быть null
                "classification": {"type": "text", "topic": "business"},
                "metadata": {
                    "source": "slack",
                    "channel": "general",
                    "author": "user123"
                },
                "normalized_at": "2023-07-01T12:34:56.789Z"
            }
        }


class ProviderConfig(BaseModel):
    """Конфигурация для провайдера нормализации."""
    name: str = Field(
        description="Имя провайдера"
    )
    enabled: bool = Field(
        default=False,
        description="Включен ли провайдер"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Дополнительные параметры провайдера"
    )
    
    
class NormalizerConfig(BaseModel):
    """Конфигурация нормализатора."""
    transcript: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(name="fallback", enabled=True),
        description="Провайдер для транскрипции аудио/видео"
    )
    caption: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(name="fallback", enabled=True),
        description="Провайдер для генерации описаний изображений"
    )
    embed: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(name="fallback", enabled=True),
        description="Провайдер для векторизации текста"
    )
    classifier: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(name="fallback", enabled=True),
        description="Провайдер для классификации контента"
    )
