"""
OpenAI провайдеры для нормализации контента.
"""
import asyncio
import base64
import io
import os
from typing import Any, Dict, List, Optional, Union

import openai
from openai import OpenAI, AsyncOpenAI

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings
from .base import (
    TranscriptProvider,
    CaptionProvider,
    EmbedProvider,
    ClassifierProvider
)

logger = get_logger(__name__)


class OpenAIClientFactory:
    """Фабрика для создания клиентов OpenAI."""
    
    @staticmethod
    def create_client(api_key: Optional[str] = None, async_client: bool = True) -> Union[OpenAI, AsyncOpenAI]:
        """
        Создает клиент OpenAI.
        
        Args:
            api_key: API ключ OpenAI
            async_client: Создать асинхронный клиент
            
        Returns:
            Клиент OpenAI
        """
        # Используем API ключ из параметров или из настроек
        key = api_key or settings.openai.api_key
        if not key:
            raise ValueError("API key for OpenAI is not provided")
            
        # Создаем клиент
        if async_client:
            return AsyncOpenAI(api_key=key, organization=settings.openai.organization_id)
        else:
            return OpenAI(api_key=key, organization=settings.openai.organization_id)


class OpenAITranscriptProvider(TranscriptProvider):
    """
    Провайдер для транскрипции аудио/видео с использованием OpenAI Whisper API.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализирует провайдер.
        
        Args:
            params: Параметры провайдера
        """
        super().__init__(params)
        self.api_key = params.get("api_key", settings.openai.api_key)
        self.model = params.get("model", settings.openai.whisper_model)
        
    async def transcribe(self, media_data: Optional[str], metadata: Dict[str, Any]) -> str:
        """
        Транскрибирует аудио/видео в текст.
        
        Args:
            media_data: Данные медиа в формате base64
            metadata: Метаданные (должны содержать 'filename')
            
        Returns:
            Текстовая транскрипция
        """
        if not media_data:
            return "No media data provided for transcription."
            
        filename = metadata.get("filename", "media.tmp")
        file_size = metadata.get("size_bytes", 0)
        file_ext = os.path.splitext(filename)[1].lower()
        main_type = metadata.get("main_type", "audio") # По умолчанию считаем аудио
        
        try:
            # Декодируем base64
            media_bytes = base64.b64decode(media_data)
            
            # Проверяем размер файла после декодирования
            decoded_size = len(media_bytes)
            if decoded_size > 25 * 1024 * 1024:  # 25MB лимит OpenAI
                logger.warning(f"File too large for OpenAI transcription: {decoded_size/1024/1024:.1f}MB > 25MB")
                return f"Media file is too large for transcription ({decoded_size/1024/1024:.1f}MB > 25MB limit)"
            
            # Создаем клиент
            client = OpenAIClientFactory.create_client(self.api_key)
            
            # Для видео файлов, которые Whisper может не принять напрямую как видео,
            # создаем временный аудио файл с расширением .mp3 для уверенности
            import tempfile
            
            tmp_filename = None
            
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_filename = tmp_file.name
                    tmp_file.write(media_bytes)
                 
                # Пробуем транскрибировать из временного файла
                # Важно: openai ожидает открытый файл, а не путь
                with open(tmp_filename, "rb") as audio_file:
                    logger.info(f"Sending media file for transcription: size={decoded_size/1024:.1f}KB, type={main_type}")
                    # Получаем транскрипцию
                    transcription_response = await client.audio.transcriptions.create(
                        file=audio_file,
                        model=self.model,
                        response_format="text"
                    )
             
                # С response_format="text" всегда ожидаем строку
                transcription = transcription_response
 
                logger.info(f"Successfully transcribed media '{filename}' with OpenAI Whisper ({len(transcription)} chars)")
                return transcription
            finally:
                # Удаляем временный файл после обработки
                if tmp_filename and os.path.exists(tmp_filename):
                    try:
                        os.unlink(tmp_filename)
                    except Exception as e_tmp:
                        logger.warning(f"Failed to delete temporary file {tmp_filename}: {e_tmp}")
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error during transcription for '{filename}': {e}")
            return f"Error transcribing media (API Error): {e}"
        except openai.BadRequestError as e:
            error_msg = str(e)
            if "whisper" in error_msg.lower() and "mp4" in error_msg.lower():
                logger.error(f"Invalid media format for Whisper API: {error_msg}")
                return f"Whisper API cannot process this media format. Only audio formats are supported."
            else:
                logger.error(f"Bad request error for Whisper API: {error_msg}")
                return f"Error with media transcription request: {error_msg}"
        except Exception as e:
            logger.error(f"Error transcribing media '{filename}' with OpenAI Whisper: {e}")
            # Возвращаем сообщение об ошибке
            return f"Error transcribing media: {str(e)}"


class OpenAICaptionProvider(CaptionProvider):
    """
    Провайдер для генерации описаний изображений с использованием OpenAI API.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализирует провайдер.
        
        Args:
            params: Параметры провайдера
        """
        super().__init__(params)
        self.api_key = params.get("api_key", settings.openai.api_key)
        self.model = params.get("model", settings.openai.caption_model)
        self.max_tokens = params.get("max_tokens", settings.openai.caption_max_tokens)
        self.temperature = params.get("temperature", settings.openai.caption_temperature)
        
    async def generate_caption(self, image_data: Union[bytes, str], metadata: Dict[str, Any]) -> str:
        """
        Генерирует описание изображения.
        
        Args:
            image_data: Изображение (байты или путь к файлу)
            metadata: Метаданные изображения
            
        Returns:
            Текстовое описание изображения
        """
        try:
            # Создаем клиент
            client = OpenAIClientFactory.create_client(self.api_key)
            
            # Проверяем, является ли image_data уже строкой base64
            if isinstance(image_data, str):
                if len(image_data) > 100 and image_data.startswith('/9j/') or image_data.startswith('iVBOR'):
                    # Вероятно, это уже base64 строка
                    encoded_image = image_data
                else:
                    # Это путь к файлу
                    try:
                        with open(image_data, "rb") as f:
                            image_bytes = f.read()
                            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                    except (FileNotFoundError, PermissionError) as file_err:
                        logger.error(f"Cannot open image file: {file_err}")
                        return f"Error opening image file: {str(file_err)}"
            else:
                # Если переданы байты, кодируем их в base64
                encoded_image = base64.b64encode(image_data).decode("utf-8")
                
            # Получаем описание с GPT-4V
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI assistant that generates detailed and accurate descriptions of images."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this image in detail."},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}",
                            "detail": "high"
                        }}
                    ]}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            caption = response.choices[0].message.content
            logger.info(f"Successfully generated caption with OpenAI ({len(caption)} chars)")
            return caption
            
        except Exception as e:
            logger.error(f"Error generating caption with OpenAI: {e}")
            # Возвращаем сообщение об ошибке
            return f"Error generating image caption: {str(e)}"


class OpenAIEmbedProvider(EmbedProvider):
    """
    Провайдер для векторизации текста с использованием OpenAI API.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализирует провайдер.
        
        Args:
            params: Параметры провайдера
        """
        super().__init__(params)
        self.api_key = params.get("api_key", settings.openai.api_key)
        self.model = params.get("model", settings.openai.embedding_model)
        
    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Создает векторное представление текста.
        
        Args:
            text: Текст для векторизации
            
        Returns:
            Векторное представление текста
        """
        try:
            # Ограничиваем длину текста для векторизации (max ~8000 токенов для большинства моделей)
            MAX_CHARS = 24000  # Примерный лимит в символах (3-4 символа на токен)
            if len(text) > MAX_CHARS:
                logger.warning(f"Text too long for embedding ({len(text)} chars), truncating to {MAX_CHARS} chars")
                text = text[:MAX_CHARS]
            
            # Создаем клиент
            client = OpenAIClientFactory.create_client(self.api_key)
            
            # Выполняем запрос к API для получения эмбеддингов
            embedding_response = await client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            embedding = embedding_response.data[0].embedding

            # Пост-обработка (центрирование и L2-нормализация) БОЛЬШЕ НЕ НУЖНА для text-embedding-3 моделей
            # logger.info(
            #     f"Successfully embedded text with OpenAI BEFORE post-processing "
            #     f"({len(embedding)} dimensions)"
            # )

            # -- УДАЛЕНО: Пост-обработка embeddings -----------------------------------
            # if embedding and not used_norm: ... (старый код центрирования/нормализации) ...
            # -- КОНЕЦ УДАЛЕНО -------------------------------------------------------

            logger.info(
                f"Successfully embedded text with OpenAI model {self.model} "
                f"({len(embedding)} dimensions)"
            )
            return embedding
            
        except Exception as e:
            logger.error(f"Error embedding text with OpenAI: {e}")
            # Возвращаем None в случае ошибки
            return None


class OpenAIClassifierProvider(ClassifierProvider):
    """
    Провайдер для классификации контента с использованием OpenAI API.
    """
    
    def __init__(self, params: Dict[str, Any]):
        """
        Инициализирует провайдер.
        
        Args:
            params: Параметры провайдера
        """
        super().__init__(params)
        self.api_key = params.get("api_key", settings.openai.api_key)
        self.model = params.get("model", settings.openai.classifier_model)
        self.max_tokens = params.get("max_tokens", settings.openai.classifier_max_tokens)
        self.temperature = params.get("temperature", settings.openai.classifier_temperature)
        
    async def classify(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Классифицирует контент.
        
        Args:
            text: Текст для классификации
            metadata: Метаданные контента
            
        Returns:
            Результат классификации
        """
        import json
        
        try:
            # Создаем клиент
            client = OpenAIClientFactory.create_client(self.api_key)
            
            # Ограничиваем длину текста для классификации
            truncated_text = text[:4000] if len(text) > 4000 else text
            
            # Базовая классификация на основе метаданных
            main_type = metadata.get("main_type", "unknown")
            
            # Определяем тип контента напрямую
            try:
                prompt = f"""Analyze this content and return only a single word for content type 
                (text, article, code, video, audio, image, conversation):

                {truncated_text[:1000]}
                
                Content type:"""
                
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a content type classifier."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                
                content_type = response.choices[0].message.content.strip().lower()
                # Нормализуем ответ
                for type_name in ["text", "article", "code", "video", "audio", "image", "conversation"]:
                    if type_name in content_type:
                        content_type = type_name
                        break
                else:
                    content_type = main_type
                
                # Определяем темы
                prompt = f"""Analyze this content and list up to 3 main topics as comma-separated values:

                {truncated_text[:1500]}
                
                Topics:"""
                
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a content topic analyzer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=50,
                    temperature=0.3
                )
                
                topics_text = response.choices[0].message.content.strip()
                topics = [topic.strip() for topic in topics_text.split(',')]
                if not topics or not any(topic for topic in topics):
                    topics = ["general"]
                
                # Формируем результат
                classification = {
                    "content_type": content_type,
                    "topics": topics[:5],  # Ограничиваем до 5 тем
                    "sentiment": "neutral",
                    "complexity": "medium",
                    "language": "english" if all(c.isascii() for c in text[:100]) else "unknown"
                }
                
                logger.info(f"Successfully classified content with OpenAI")
                return classification
                
            except Exception as inner_err:
                logger.error(f"Error in OpenAI classification process: {inner_err}")
                # Возвращаем базовую классификацию в случае внутренней ошибки
                return {
                    "content_type": main_type,
                    "topics": ["general"],
                    "sentiment": "neutral",
                    "complexity": "medium", 
                    "language": "unknown",
                    "error": str(inner_err)
                }
                
        except Exception as e:
            logger.error(f"Error classifying content with OpenAI: {e}")
            # Возвращаем базовую классификацию в случае ошибки
            return {
                "content_type": "unknown",
                "topics": ["general"],
                "sentiment": "neutral",
                "complexity": "unknown",
                "language": "unknown",
                "error": str(e)
            } 