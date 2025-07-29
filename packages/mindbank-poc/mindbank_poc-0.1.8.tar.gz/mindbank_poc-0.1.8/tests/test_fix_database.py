"""
Тест для проверки обхода записи в реальную БД
"""
import pytest
import pytest_asyncio
import os
import sys
import json
from pathlib import Path

# Проверяем, что модуль jsonl_backend доступен
try:
    from mindbank_poc.api.backends import jsonl_backend
except ImportError:
    print("Не удалось импортировать jsonl_backend")
    raise

# Путь к реальной БД
REAL_DB_PATH = Path("/home/vlad/tech/job/involve/mindbank-poc/data/ingest_jsonl/raw_entries.jsonl")

def test_set_testing_dir():
    """
    Проверяет работу функции set_testing_dir для перенаправления записи в тестовую БД
    """
    # Сохраняем оригинальные пути
    original_data_dir = jsonl_backend.DATA_DIR
    original_raw_entries = jsonl_backend.RAW_ENTRIES_FILE
    original_aggregates = jsonl_backend.AGGREGATES_FILE
    
    # Проверяем, что работает в тестовом режиме
    assert jsonl_backend.IS_TESTING, "jsonl_backend.IS_TESTING должен быть True в тестовом окружении"
    
    # Проверяем наличие реальной БД
    real_db_exists = REAL_DB_PATH.exists()
    real_db_size_before = REAL_DB_PATH.stat().st_size if real_db_exists else 0
    
    # Создаем временную директорию для тестов
    import tempfile
    temp_dir = Path(tempfile.mkdtemp(prefix="test_jsonl_backend_"))
    print(f"Создана временная директория: {temp_dir}")
    
    # Устанавливаем тестовую директорию
    jsonl_backend.set_testing_dir(temp_dir)
    
    # Проверяем, что пути изменились
    assert jsonl_backend.DATA_DIR == temp_dir, f"DATA_DIR должен быть {temp_dir}, но получен {jsonl_backend.DATA_DIR}"
    assert jsonl_backend.RAW_ENTRIES_FILE == temp_dir / "raw_entries.jsonl", f"RAW_ENTRIES_FILE должен быть {temp_dir / 'raw_entries.jsonl'}, но получен {jsonl_backend.RAW_ENTRIES_FILE}"
    assert jsonl_backend.AGGREGATES_FILE == temp_dir / "aggregates.jsonl", f"AGGREGATES_FILE должен быть {temp_dir / 'aggregates.jsonl'}, но получен {jsonl_backend.AGGREGATES_FILE}"
    
    # Создаем тестовый объект для записи
    from mindbank_poc.api.schemas import RawEntryInput
    import datetime
    
    test_entry = RawEntryInput(
        collector_id="test-collector",
        group_id="test-group",
        entry_id="test-entry",
        type="text",
        payload={"content": "Test content"},
        metadata={"test": True},
        timestamp=datetime.datetime.now().isoformat()
    )
    
    # Записываем в БД
    import asyncio
    async def save_entry():
        await jsonl_backend.save_raw_entry(test_entry)
    
    # Запускаем асинхронную функцию
    asyncio.run(save_entry())
    
    # Проверяем, что файл создан во временной директории
    temp_db_path = temp_dir / "raw_entries.jsonl"
    assert temp_db_path.exists(), f"Файл {temp_db_path} должен быть создан"
    assert temp_db_path.stat().st_size > 0, f"Файл {temp_db_path} должен содержать данные"
    
    # Читаем содержимое файла
    with open(temp_db_path, "r") as f:
        content = f.read()
    print(f"Содержимое временного файла: {content}")
    assert "test-collector" in content, "Содержимое файла должно содержать test-collector"
    
    # Проверяем, что реальная БД не изменилась
    if real_db_exists:
        real_db_size_after = REAL_DB_PATH.stat().st_size
        assert real_db_size_before == real_db_size_after, f"Размер реальной БД изменился: было {real_db_size_before}, стало {real_db_size_after}"
    
    # Очищаем временную директорию
    import shutil
    shutil.rmtree(temp_dir)
    
    # Восстанавливаем оригинальные пути
    jsonl_backend.DATA_DIR = original_data_dir
    jsonl_backend.RAW_ENTRIES_FILE = original_raw_entries
    jsonl_backend.AGGREGATES_FILE = original_aggregates 