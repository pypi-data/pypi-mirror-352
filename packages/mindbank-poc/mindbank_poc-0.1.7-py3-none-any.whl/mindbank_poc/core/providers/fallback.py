"""
Fallback-провайдеры для нормализации контента в offline-режиме.
"""
from typing import Any, Dict, List, Optional
from .base import (
    TranscriptProvider,
    CaptionProvider,
    EmbedProvider,
    ClassifierProvider,
    FilePreviewProvider
)


class FallbackCaptionProvider(CaptionProvider):
    """Fallback-провайдер для описаний изображений."""
    async def generate_caption(self, image_data: Optional[bytes], metadata: Dict[str, Any]) -> str:
        filename = metadata.get("filename", "unknown file")
        width = metadata.get("width")
        height = metadata.get("height")
        size_bytes = metadata.get("size_bytes")
        
        parts = [f"Image file: {filename}"]
        if width and height:
            parts.append(f"dimensions: {width}x{height}")
        if size_bytes:
            parts.append(f"size: {size_bytes} bytes")
            
        return ", ".join(parts)


class FallbackTranscriptProvider(TranscriptProvider):
    """Fallback-провайдер для транскрипции аудио/видео."""
    async def transcribe(self, media_data: Optional[bytes], metadata: Dict[str, Any]) -> str:
        filename = metadata.get("filename", "unknown file")
        duration = metadata.get("duration")
        size_bytes = metadata.get("size_bytes")
        media_type = metadata.get("media_type", "Media") # Определить бы тип из payload/metadata

        parts = [f"{media_type.capitalize()} file: {filename}"]
        if duration:
            # Преобразуем секунды в минуты/секунды для читаемости
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            parts.append(f"duration: {minutes}m {seconds}s")
        if size_bytes:
            parts.append(f"size: {size_bytes} bytes")

        return ", ".join(parts)


class FallbackEmbedProvider(EmbedProvider):
    """Fallback-провайдер для векторизации текста."""
    async def embed_text(self, text: str) -> Optional[List[float]]:
        # Возвращает None, так как в offline-режиме векторизация невозможна
        return None


class FallbackClassifierProvider(ClassifierProvider):
    """Fallback-провайдер для классификации контента."""
    async def classify(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Возвращает базовую классификацию
        content_type = metadata.get("main_type", "unknown")
        return {
            "type": content_type,
            "topic": "general",
            "sentiment": "neutral",
            "language": "unknown",
            "complexity": "unknown"
        }


class FallbackFilePreviewProvider(FilePreviewProvider):
    """Fallback-провайдер для превью файлов."""
    async def get_preview(self, payload: Dict[str, Any]) -> str:
        text_preview = payload.get("text_preview")
        filename = payload.get("filename", "unknown file")
        size_bytes = payload.get("size_bytes")
        
        parts = []
        if text_preview:
            parts.append(f"File preview: {text_preview}")
        else:
            parts.append(f"File: {filename}")
            
        if size_bytes:
            parts.append(f"size: {size_bytes} bytes")
            
        return ", ".join(parts) 