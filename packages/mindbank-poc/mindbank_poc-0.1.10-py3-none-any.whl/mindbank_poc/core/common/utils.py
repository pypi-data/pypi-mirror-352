"""
Общие утилиты.
"""
from typing import Literal
from .types import ContentType

# Карта расширений для определения типа контента
# Можно расширять по мере необходимости
EXTENSION_TO_CONTENT_TYPE: dict[str, ContentType] = {
    # Text formats
    ".txt": "text", ".md": "text", ".log": "text", ".csv": "text", ".tsv": "text",
    ".xml": "text", ".html": "text", ".css": "text", ".json": "text",
    # Image formats
    ".jpg": "image", ".jpeg": "image", ".png": "image", ".gif": "image", ".bmp": "image",
    ".webp": "image", ".svg": "image",
    # Audio formats
    ".mp3": "audio", ".wav": "audio", ".ogg": "audio", ".flac": "audio", ".m4a": "audio",
    # Video formats
    ".mp4": "video", ".avi": "video", ".mov": "video", ".mkv": "video", ".wmv": "video",
    ".flv": "video",
    # Code formats
    ".py": "code", ".js": "code", ".java": "code", ".c": "code", ".cpp": "code", ".cs": "code",
    ".php": "code", ".rb": "code", ".go": "code", ".rs": "code", ".swift": "code", ".kt": "code",
    ".scala": "code",
    # Document/File formats
    ".pdf": "file", ".doc": "file", ".docx": "file", ".xls": "file", ".xlsx": "file",
    ".ppt": "file", ".pptx": "file", ".zip": "file", ".rar": "file", ".7z": "file",
    # Links are typically not based on extension but handled differently
}

# Карта расширений для языков программирования
EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python", ".js": "javascript", ".java": "java", ".c": "c", ".cpp": "cpp",
    ".cs": "csharp", ".php": "php", ".rb": "ruby", ".go": "go", ".rs": "rust",
    ".swift": "swift", ".kt": "kotlin", ".scala": "scala", ".html": "html", ".css": "css"
}

def get_content_type_from_extension(file_extension: str) -> ContentType:
    """Определяет ContentType по расширению файла."""
    ext = file_extension.lower()
    return EXTENSION_TO_CONTENT_TYPE.get(ext, "file") # По умолчанию считаем файлом

def get_language_from_extension(file_extension: str) -> str:
    """Определяет язык программирования по расширению файла."""
    ext = file_extension.lower()
    return EXTENSION_TO_LANGUAGE.get(ext, "unknown") 