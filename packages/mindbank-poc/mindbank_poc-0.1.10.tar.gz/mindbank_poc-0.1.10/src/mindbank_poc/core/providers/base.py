"""
Базовые классы для провайдеров нормализации.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BaseProvider(ABC):
    """Базовый класс для всех провайдеров."""
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализирует провайдер с параметрами.
        
        Args:
            params: Параметры для конфигурации провайдера
        """
        self.params = params


class TranscriptProvider(BaseProvider):
    """Базовый класс для провайдеров транскрипции."""
    @abstractmethod
    async def transcribe(self, media_data: Optional[Union[bytes, str]], metadata: Dict[str, Any]) -> str:
        """
        Транскрибирует аудио/видео данные.
        
        Args:
            media_data: Байты аудио/видео или путь к файлу, или base64 строка
            metadata: Метаданные файла
            
        Returns:
            Текстовая транскрипция
        """
        pass


class CaptionProvider(BaseProvider):
    """Базовый класс для провайдеров описания изображений."""
    @abstractmethod
    async def generate_caption(self, image_data: Optional[Union[bytes, str]], metadata: Dict[str, Any]) -> str:
        """
        Генерирует описание изображения.
        
        Args:
            image_data: Байты изображения или путь к файлу, или base64 строка
            metadata: Метаданные изображения
            
        Returns:
            Текстовое описание
        """
        pass


class EmbedProvider(BaseProvider):
    """Базовый класс для провайдеров векторизации."""
    @abstractmethod
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Создает векторное представление текста.
        
        Args:
            text: Текст для векторизации
            
        Returns:
            Список float чисел (вектор) или None
        """
        pass


class ClassifierProvider(BaseProvider):
    """Базовый класс для провайдеров классификации."""
    @abstractmethod
    async def classify(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Классифицирует контент.
        
        Args:
            text: Текст для классификации
            metadata: Метаданные контента
            
        Returns:
            Словарь с результатами классификации
        """
        pass

class FilePreviewProvider(BaseProvider):
    """Базовый класс для провайдеров превью файлов."""
    @abstractmethod
    async def get_preview(self, payload: Dict[str, Any]) -> str:
        """
        Генерирует текстовое превью для файла.
        
        Args:
            payload: Payload записи с типом 'file'
            
        Returns:
            Строка с превью файла
        """
        pass