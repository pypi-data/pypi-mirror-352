#!/usr/bin/env python
"""
Скрипт для инициализации пустых хранилищ данных.

Этот скрипт создает необходимые директории и файлы для работы 
с хранилищами JSONL и ChromaDB, если они отсутствуют.

Использование:
    python -m mindbank_poc.cli.init_storages

Аргументы:
    --store-type: Тип хранилища данных, "jsonl" или "chroma" (по умолчанию "chroma")
"""

import asyncio
import argparse
from pathlib import Path

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.config.settings import settings

logger = get_logger(__name__)

async def init_jsonl_storage() -> bool:
    """
    Инициализирует хранилище JSONL.
    
    Returns:
        True в случае успеха, иначе False
    """
    try:
        # Создаем директорию для хранения данных
        knowledge_dir = Path(settings.storage.knowledge_dir)
        knowledge_dir.mkdir(exist_ok=True, parents=True)
        
        # Создаем пустой JSONL файл, если он не существует
        jsonl_file = knowledge_dir / settings.storage.normalized_units_file
        if not jsonl_file.exists():
            jsonl_file.touch()
            logger.info(f"Создан пустой JSONL файл: {jsonl_file}")
        else:
            logger.info(f"JSONL файл уже существует: {jsonl_file}")
            
        # Создаем директорию для резервных копий
        backup_dir = knowledge_dir / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"Хранилище JSONL инициализировано: {knowledge_dir}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при инициализации хранилища JSONL: {e}")
        return False

async def init_chroma_storage() -> bool:
    """
    Инициализирует хранилище ChromaDB.
    
    Returns:
        True в случае успеха, иначе False
    """
    try:
        # Создаем директорию для хранения данных
        knowledge_dir = Path(settings.storage.knowledge_dir)
        knowledge_dir.mkdir(exist_ok=True, parents=True)
        
        # Создаем директорию для ChromaDB
        chroma_dir = knowledge_dir / "chroma_db"
        chroma_dir.mkdir(exist_ok=True)
        
        # Создаем директорию для резервных копий
        backup_dir = knowledge_dir / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"Хранилище ChromaDB инициализировано: {chroma_dir}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при инициализации хранилища ChromaDB: {e}")
        return False

async def init_ingest_storage() -> bool:
    """
    Инициализирует хранилище входящих данных.
    
    Returns:
        True в случае успеха, иначе False
    """
    try:
        # Создаем директорию для хранения входящих данных
        ingest_dir = Path(settings.storage.ingest_dir)
        ingest_dir.mkdir(exist_ok=True, parents=True)
        
        # Создаем пустые JSONL файлы, если они не существуют
        raw_entries_file = ingest_dir / settings.storage.raw_entries_file
        if not raw_entries_file.exists():
            raw_entries_file.touch()
            logger.info(f"Создан пустой JSONL файл: {raw_entries_file}")
        else:
            logger.info(f"JSONL файл уже существует: {raw_entries_file}")
            
        aggregates_file = ingest_dir / settings.storage.aggregates_file
        if not aggregates_file.exists():
            aggregates_file.touch()
            logger.info(f"Создан пустой JSONL файл: {aggregates_file}")
        else:
            logger.info(f"JSONL файл уже существует: {aggregates_file}")
            
        # Создаем директорию для резервных копий
        backup_dir = Path("data/backup")
        backup_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Хранилище входящих данных инициализировано: {ingest_dir}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при инициализации хранилища входящих данных: {e}")
        return False

async def update_storage_settings(store_type: str) -> bool:
    """
    Обновляет настройки типа хранилища в settings.
    
    Args:
        store_type: Тип хранилища данных ("jsonl" или "chroma")
        
    Returns:
        True в случае успеха, иначе False
    """
    try:
        # Изменяем тип хранилища в настройках
        if store_type in ["jsonl", "chroma"]:
            settings.storage.store_type = store_type
            logger.info(f"Тип хранилища данных изменен на: {store_type}")
            return True
        else:
            logger.error(f"Неверный тип хранилища данных: {store_type}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при обновлении настроек хранилища: {e}")
        return False

async def main():
    """Основная функция скрипта."""
    parser = argparse.ArgumentParser(description="Инициализация хранилищ данных")
    parser.add_argument("--store-type", choices=["jsonl", "chroma"], default="chroma",
                        help="Тип хранилища данных (jsonl или chroma)")
    
    args = parser.parse_args()
    
    logger.info("Начало инициализации хранилищ данных")
    
    # Обновляем настройки типа хранилища
    await update_storage_settings(args.store_type)
    
    # Инициализируем хранилища
    jsonl_init_success = await init_jsonl_storage()
    chroma_init_success = await init_chroma_storage()
    ingest_init_success = await init_ingest_storage()
    
    if jsonl_init_success and chroma_init_success and ingest_init_success:
        logger.info("Инициализация хранилищ данных завершена успешно")
        print(f"Хранилища данных инициализированы успешно. Активный тип хранилища: {args.store_type}")
    else:
        logger.error("Инициализация хранилищ данных завершена с ошибками")
        print("Инициализация хранилищ данных завершена с ошибками. См. лог для деталей.")

if __name__ == "__main__":
    asyncio.run(main()) 