"""
Модуль для работы с хранилищем знаний (Knowledge Store).
""" 

from typing import Dict, Any, Optional

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings
from .base import KnowledgeStore
from .jsonl_store import JSONLKnowledgeStore
from .chroma_store import ChromaKnowledgeStore

logger = get_logger(__name__)

# Переменная для хранения единственного экземпляра хранилища (singleton)
_knowledge_store_instance: Optional[KnowledgeStore] = None

def get_knowledge_store(config: Optional[Dict[str, Any]] = None) -> KnowledgeStore:
    """
    Фабрика для создания или получения хранилища знаний.
    
    Если хранилище уже было создано, возвращает существующий экземпляр (singleton).
    По умолчанию создает хранилище на основе ChromaDB.
    
    Args:
        config: Конфигурация хранилища, если нужны особые параметры
        
    Returns:
        Экземпляр хранилища знаний (KnowledgeStore)
    """
    global _knowledge_store_instance
    
    # Если уже есть экземпляр, возвращаем его
    if _knowledge_store_instance is not None:
        logger.debug("Returning existing knowledge store instance")
        return _knowledge_store_instance
    
    # Если нет, создаем новый
    config = config or {}
    
    # Определяем тип хранилища
    if "store_type" in config:
        store_type = config["store_type"]
    elif hasattr(settings.storage, "store_type"):
        store_type = settings.storage.store_type
    else:
        # По умолчанию используем ChromaDB
        store_type = "chroma"
    
    logger.info(f"Creating knowledge store of type: {store_type}")
    
    # Создаем хранилище в зависимости от типа
    if store_type == "jsonl":
        logger.info("Using JSONLKnowledgeStore (JSONL)")
        _knowledge_store_instance = JSONLKnowledgeStore(config)
    else:
        # По умолчанию используем ChromaDB
        logger.info("Using ChromaKnowledgeStore (ChromaDB)")
        _knowledge_store_instance = ChromaKnowledgeStore(config)
    
    return _knowledge_store_instance 