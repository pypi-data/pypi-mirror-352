from fastapi import FastAPI
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from mindbank_poc.common.logging import setup_logging, get_logger
from mindbank_poc.core.config.settings import settings, settings_logger

# Настройка логирования для API компонента
setup_logging("api")
logger = get_logger(__name__)

logger.info("Starting Mindbank Ingest API")

app = FastAPI(
    title="Mindbank Ingest API",
    description="""API для приема данных от коннекторов и передачи в основную систему.
    
## Система безопасности

Система использует двухуровневый подход к безопасности:

### Интеграционные ключи
- Долгоживущие токены для регистрации коннекторов
- Передаются в заголовке `Authorization: IntegrationKey <integration_key>`
- Управляются администратором через защищенное API

### Токены доступа
- Короткоживущие токены для коннекторов
- Получаются при регистрации и обновлении конфигурации
- Передаются в заголовке `Authorization: Bearer <access_token>`

### Административный доступ
- Базовая HTTP-аутентификация для административных эндпоинтов
- Защита эндпоинтов управления интеграционными ключами
- Защита эндпоинтов управления коннекторами
    """,
    version="0.1.0",
)

# Добавляю CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно указать конкретные адреса, если нужно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    """Check if the API is running."""
    logger.debug("Health check requested")
    return {"status": "ok"}

# Import routers
from mindbank_poc.api.routers import ingest
app.include_router(ingest.router)

# Импортируем и добавляем роутер коннекторов
from mindbank_poc.api.routers import connectors
app.include_router(connectors.router)

# Импортируем и добавляем роутер ключей интеграции
from mindbank_poc.api.routers import integration_keys
app.include_router(integration_keys.router)

# Импортируем и добавляем роутер поиска
from mindbank_poc.api.routers import retrieval
app.include_router(retrieval.router)

# Эти роутеры теперь доступны через v1 API
# Импортируем и добавляем роутер токенов доступа
from mindbank_poc.api.routers import access_tokens
app.include_router(access_tokens.router)

# Импортируем и добавляем роутер статуса системы
from mindbank_poc.api.routers import status
app.include_router(status.router)

# Импортируем и добавляем роутер архитипов
from mindbank_poc.api.routers import archetypes
app.include_router(archetypes.router)

# Импортируем и добавляем роутер провайдеров обработки
from mindbank_poc.api.routers import processing_providers
app.include_router(processing_providers.router)

# Импортируем и добавляем роутер пайплайна
from mindbank_poc.api.routers import pipeline
app.include_router(pipeline.router)

# Импортируем и добавляем роутер fingerprint-токенов
from mindbank_poc.api.routers import fingerprint_tokens
app.include_router(fingerprint_tokens.router)

# Added imports for onboarding
from mindbank_poc.api.routers import onboarding as onboarding_router
from mindbank_poc.core.connectors.onboarding_repository import InMemoryOnboardingStateRepository, FileOnboardingStateRepository
from mindbank_poc.core.connectors.service import initialize_connector_service
# End of added imports for onboarding

# Added import for FSM sync router
from mindbank_poc.api.routers import fsm_sync_router
from mindbank_poc.api.routers import agent_chat

# Log when application has fully loaded
@app.on_event("startup")
async def startup_event():
    """Инициализация приложения при запуске."""
    settings_logger.info(f"Starting API with settings: normalizer.offline_mode={settings.normalizer.offline_mode} (type: {type(settings.normalizer.offline_mode)})")
    settings_logger.info(f"Providers: transcript={settings.normalizer.transcript_provider}, "
                         f"caption={settings.normalizer.caption_provider}, "
                         f"embed={settings.normalizer.embed_provider}, "
                         f"classifier={settings.normalizer.classifier_provider}")
    
    # Инициализируем сервис ключей интеграции (должен быть первым, если сервисы зависят от него)
    from mindbank_poc.core.services.integration_key_service import get_integration_key_service
    get_integration_key_service() # Синхронная инициализация, если она есть

    # Инициализируем сервис коннекторов с репозиторием онбоардинга
    # Определяем, какое хранилище использовать для состояний онбоардинга
    # В производственном режиме используем FileOnboardingStateRepository
    # чтобы состояния сохранялись между перезапусками сервера
    if settings.debug:
        logger.info("Using InMemoryOnboardingStateRepository for onboarding states (debug mode)")
        onboarding_repo = InMemoryOnboardingStateRepository()
    else:
        logger.info(f"Using FileOnboardingStateRepository for onboarding states at: {settings.connector.onboarding_states_path}")
        onboarding_repo = FileOnboardingStateRepository(storage_path=settings.connector.onboarding_states_path)
        
    connector_service = initialize_connector_service(onboarding_repo=onboarding_repo)
    await connector_service.start()
    
    logger.info("Mindbank Ingest API started")

@app.on_event("shutdown")
async def shutdown_event():
    # Останавливаем сервис коннекторов
    from mindbank_poc.core.connectors.service import get_connector_service
    service = get_connector_service() # Получаем экземпляр синхронно
    await service.stop()              # Вызываем его async метод stop()
    
    logger.info("Mindbank Ingest API shutting down")

# Включение нового роутера онбоардинга
app.include_router(onboarding_router.router)

# Включение нового роутера для FSM синхронизации с коннекторами
app.include_router(fsm_sync_router.router)

# Включение роутера для чатов агента
app.include_router(agent_chat.router)

# v1 API router removed - we don't use versioning in this project

# Этот код выполняется только если файл запускается напрямую, а не импортируется
if __name__ == "__main__":
    import uvicorn
    
    # Логирование настроек при запуске сервера
    offline_mode = settings.normalizer.offline_mode
    providers = {
        "transcript": settings.normalizer.transcript_provider,
        "caption": settings.normalizer.caption_provider,
        "embed": settings.normalizer.embed_provider,
        "classifier": settings.normalizer.classifier_provider
    }
    
    logger.info(f"Staring server with settings: offline_mode={offline_mode} (type: {type(offline_mode)})")
    logger.info(f"Providers: {providers}")
    
    # Запуск сервера
    uvicorn.run(
        "mindbank_poc.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload
    )
