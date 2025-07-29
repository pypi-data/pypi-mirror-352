import json
import aiofiles
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os
import sys

from mindbank_poc.common.logging import get_logger
from mindbank_poc.api.schemas import RawEntryInput, AggregateInput

# Получаем логгер для этого модуля
logger = get_logger(__name__)

# Determine project root based on this file's location
# src/mindbank_poc/api/backends/jsonl_backend.py -> project_root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# Специальный флаг для тестов - проверяем, запущены ли тесты
IS_TESTING = 'pytest' in sys.modules
TESTING_DIR = None  # Будет установлено в фикстуре

# Директория для хранения данных по умолчанию
DEFAULT_DATA_DIR = PROJECT_ROOT / "data" / "ingest_jsonl"
DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Устанавливаем пути для реальной работы
DATA_DIR = DEFAULT_DATA_DIR
RAW_ENTRIES_FILE = DATA_DIR / "raw_entries.jsonl"
AGGREGATES_FILE = DATA_DIR / "aggregates.jsonl"

# Add some logging to see the path
logger.info(f"JSONL Backend initialized. Data directory: {DATA_DIR.resolve()}")

def set_testing_dir(directory: Path):
    """
    Устанавливает директорию для тестов.
    Вызывается из тестовых фикстур.
    """
    global TESTING_DIR, DATA_DIR, RAW_ENTRIES_FILE, AGGREGATES_FILE, IS_TESTING
    TESTING_DIR = directory
    if IS_TESTING and TESTING_DIR is not None:
        old_dir = DATA_DIR
        old_raw = RAW_ENTRIES_FILE
        old_agg = AGGREGATES_FILE
        
        DATA_DIR = TESTING_DIR
        RAW_ENTRIES_FILE = DATA_DIR / "raw_entries.jsonl"
        AGGREGATES_FILE = DATA_DIR / "aggregates.jsonl"
        
        logger.info(f"JSONL Backend switched to testing directory")
        logger.info(f" - Old DATA_DIR: {old_dir}")
        logger.info(f" - Old RAW_ENTRIES_FILE: {old_raw}")
        logger.info(f" - Old AGGREGATES_FILE: {old_agg}")
        logger.info(f" - New DATA_DIR: {DATA_DIR}")
        logger.info(f" - New RAW_ENTRIES_FILE: {RAW_ENTRIES_FILE}")
        logger.info(f" - New AGGREGATES_FILE: {AGGREGATES_FILE}")
        # Убедимся, что директория существует
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created testing directory: {DATA_DIR}")
            
        # Печатаем в stdout тоже для отладки
        print(f"[JSONL_BACKEND] Switched to testing directory: {DATA_DIR}")
        print(f"[JSONL_BACKEND] RAW_ENTRIES_FILE: {RAW_ENTRIES_FILE}")
        print(f"[JSONL_BACKEND] AGGREGATES_FILE: {AGGREGATES_FILE}")

async def save_raw_entry(entry: RawEntryInput):
    """Appends a raw entry to the JSONL file."""
    entry_dict = entry.model_dump(mode="json")
    
    # Выбираем правильный путь: тестовый или реальный
    target_file = RAW_ENTRIES_FILE
    
    # Добавляем детальное логирование
    logger.info(f"[save_raw_entry] DATA_DIR={DATA_DIR}, TESTING_DIR={TESTING_DIR}, IS_TESTING={IS_TESTING}")
    logger.info(f"[save_raw_entry] Saving raw entry to: {target_file}")
    logger.info(f"[save_raw_entry] Entry content preview: {str(entry_dict)[:100]}...")
    
    # Печатаем в stdout тоже для отладки
    print(f"[JSONL_BACKEND.save_raw_entry] Saving to {target_file}")
    print(f"[JSONL_BACKEND.save_raw_entry] Entry ID: {entry_dict.get('entry_id', 'N/A')}")  
        
    try:
        # Создаем родительскую директорию, если не существует
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(target_file, mode='a') as f:
            await f.write(json.dumps(entry_dict, ensure_ascii=False) + '\n')
        logger.debug("Raw entry saved successfully")
        print(f"[JSONL_BACKEND.save_raw_entry] Success writing to {target_file}")
    except Exception as e:
        logger.error(f"Error saving raw entry: {e}")
        print(f"[JSONL_BACKEND.save_raw_entry] ERROR: {e}")
        raise  # Re-raise to allow the API to handle the error

async def save_aggregate(aggregate: AggregateInput):
    """Appends an aggregate to the JSONL file."""
    aggregate_data = aggregate.model_dump(mode="json")
    output_dict = {
        "group_id": aggregate_data["group_id"],
        "entries": aggregate_data["entries"],
        "metadata": aggregate_data["metadata"],
        "aggregated_at": datetime.datetime.now(datetime.UTC).isoformat()
    }
    
    # Выбираем правильный путь: тестовый или реальный
    target_file = AGGREGATES_FILE
        
    logger.debug(f"Saving aggregate to: {target_file}")
    try:
        # Создаем родительскую директорию, если не существует
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(target_file, mode='a') as f:
            await f.write(json.dumps(output_dict, ensure_ascii=False) + '\n')
        logger.debug("Aggregate saved successfully")
    except Exception as e:
        logger.error(f"Error saving aggregate: {e}")
        raise  # Re-raise to allow the API to handle the error

async def load_aggregate_by_id(group_id: str) -> Optional[AggregateInput]:
    """Загружает агрегат по его group_id из файла JSONL."""
    target_file = AGGREGATES_FILE
    
    if not target_file.exists():
        logger.warning(f"Aggregates file {target_file} not found.")
        return None
    try:
        async with aiofiles.open(target_file, mode='r') as f:
            async for line in f:
                if line.strip():
                    data = json.loads(line)
                    if data.get("group_id") == group_id:
                        # Убедимся, что все поля для AggregateInput присутствуют
                        # schema AggregateInput: group_id, entries, metadata
                        # В файле сохраняется: group_id, entries, metadata, aggregated_at
                        return AggregateInput(
                            group_id=data["group_id"],
                            entries=[RawEntryInput(**entry_data) for entry_data in data.get("entries", [])],
                            metadata=data.get("metadata", {})
                        )
        logger.debug(f"Aggregate with group_id {group_id} not found in {target_file}.")
        return None
    except Exception as e:
        logger.error(f"Error loading aggregate {group_id}: {e}")
        return None # Или можно возбудить исключение
