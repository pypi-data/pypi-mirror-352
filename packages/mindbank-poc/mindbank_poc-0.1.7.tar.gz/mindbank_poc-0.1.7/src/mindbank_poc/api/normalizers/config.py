"""
Конфигурация нормализатора в API.
"""
from pathlib import Path
import os
from typing import Dict, Any, Optional

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.normalizer.models import NormalizerConfig, ProviderConfig
from mindbank_poc.core.config.settings import settings, settings_logger
from mindbank_poc.core.common.types import ProviderType
from mindbank_poc.core.services.provider_service import get_provider_service

logger = get_logger(__name__)


def load_config(config_path: Optional[Path] = None) -> NormalizerConfig:
    """
    Загружает конфигурацию нормализатора из настроек.
    
    Конфигурация берется из настроек окружения (.env файл).
    
    Args:
        config_path: Путь к конфигурационному файлу (игнорируется, оставлен для совместимости)
        
    Returns:
        Конфигурация нормализатора
    """    
    # Используем настройки из .env
    logger.info("Using normalizer config from environment variables")
    settings_logger.info(f"[load_config] Initial settings.normalizer.offline_mode: {settings.normalizer.offline_mode} (type: {type(settings.normalizer.offline_mode)})" )
    
    # Принудительная проверка для отладки
    # Проверяем переменную среды напрямую
    env_offline_mode = os.getenv("NORMALIZER_OFFLINE_MODE", "").lower()
    is_offline = env_offline_mode in ("true", "1", "yes", "y", "on") or settings.normalizer.offline_mode is True
    
    if is_offline:
        logger.info("Offline mode is enabled, using fallback providers regardless of provider settings")
        transcript_provider = "fallback"
        caption_provider = "fallback"
        embed_provider = "fallback"
        classifier_provider = "fallback"
    else:
        logger.info(f"Using configured providers: "
                  f"transcript={settings.normalizer.transcript_provider}, "
                  f"caption={settings.normalizer.caption_provider}, "
                  f"embed={settings.normalizer.embed_provider}, "
                  f"classifier={settings.normalizer.classifier_provider}")
        transcript_provider = settings.normalizer.transcript_provider
        caption_provider = settings.normalizer.caption_provider
        embed_provider = settings.normalizer.embed_provider
        classifier_provider = settings.normalizer.classifier_provider

    # Clear the cache to ensure we get fresh data from the repository
    get_provider_service.cache_clear()
    logger.debug("Provider service cache cleared before loading normalizer config")
    
    # Get provider service
    provider_service = get_provider_service()
    
    # Get providers by type
    transcript_providers = provider_service.get_providers_by_type(ProviderType.TRANSCRIPTION)
    caption_providers = provider_service.get_providers_by_type(ProviderType.CAPTION)
    embed_providers = provider_service.get_providers_by_type(ProviderType.EMBEDDING)
    classifier_providers = provider_service.get_providers_by_type(ProviderType.CLASSIFICATION)
    

    print(f"transcript_providers: {transcript_providers}")
    print(f"caption_providers: {caption_providers}")
    print(f"embed_providers: {embed_providers}")
    print(f"classifier_providers: {classifier_providers}")
    # Создаем конфигурацию нормализатора на основе провайдеров из сервиса
    normalizer_config = NormalizerConfig(
        transcript=ProviderConfig(
            name=transcript_providers[0].name if transcript_providers else "fallback",
            enabled=settings.normalizer.enable_transcript,
            params=transcript_providers[0].current_config if transcript_providers else {}
        ),
        caption=ProviderConfig(
            name=caption_providers[0].name if caption_providers else "fallback",
            enabled=settings.normalizer.enable_caption,
            params=caption_providers[0].current_config if caption_providers else {}
        ),
        embed=ProviderConfig(
            name=embed_providers[0].name if embed_providers else "fallback",
            enabled=settings.normalizer.enable_embed,
            params=embed_providers[0].current_config if embed_providers else {}
        ),
        classifier=ProviderConfig(
            name=classifier_providers[0].name if classifier_providers else "fallback",
            enabled=settings.normalizer.enable_classifier,
            params=classifier_providers[0].current_config if classifier_providers else {}
        )
    )
    
    settings_logger.info(f"[load_config] Created NormalizerConfig from provider service: {normalizer_config.model_dump_json(indent=2)}")
    return normalizer_config