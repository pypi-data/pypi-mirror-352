"""
CLI-утилита для запуска и тестирования нормализатора.
"""
import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.normalizer.normalizer import Normalizer
from mindbank_poc.core.knowledge_store.jsonl_store import JSONLKnowledgeStore
from mindbank_poc.api.normalizers.config import load_config
from mindbank_poc.core.config.settings import settings


logger = get_logger(__name__)


async def load_aggregate_from_file(file_path: str) -> Dict[str, Any]:
    """
    Загружает агрегат из файла.
    
    Args:
        file_path: Путь к файлу с агрегатом
        
    Returns:
        Агрегат в виде словаря
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading aggregate from file {file_path}: {e}")
        sys.exit(1)
        

async def load_aggregate_from_jsonl(file_path: str, group_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Загружает агрегат из JSONL-файла.
    
    Args:
        file_path: Путь к JSONL-файлу с агрегатами
        group_id: ID группы для поиска конкретного агрегата
        
    Returns:
        Агрегат в виде словаря
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            
            # Если lines пустой, возвращаем ошибку
            if not lines:
                logger.error(f"No aggregates found in {file_path}")
                sys.exit(1)
                
            # Если указан group_id, ищем конкретный агрегат
            if group_id:
                for line in lines:
                    agg = json.loads(line)
                    if agg.get("group_id") == group_id:
                        return agg
                        
                logger.error(f"Aggregate with group_id {group_id} not found in {file_path}")
                sys.exit(1)
                
            # Иначе возвращаем последний агрегат
            return json.loads(lines[-1])
    except Exception as e:
        logger.error(f"Error loading aggregate from JSONL file {file_path}: {e}")
        sys.exit(1)
        
        
async def run_normalizer(config_path: Optional[str], aggregate: Dict[str, Any], output_file: Optional[str]):
    """
    Запускает нормализатор для обработки агрегата.
    
    Args:
        config_path: Путь к конфигурационному файлу
        aggregate: Агрегат для обработки
        output_file: Путь к файлу для сохранения результата
    """
    # Загружаем конфигурацию
    normalizer_config = load_config(config_path)
    
    # Инициализируем нормализатор
    normalizer = Normalizer(normalizer_config)
    
    # Обрабатываем агрегат
    logger.info(f"Processing aggregate {aggregate.get('group_id')} with {len(aggregate.get('entries', []))} entries")
    normalized_unit = await normalizer.process(aggregate)
    
    # Выводим результат
    logger.info(f"Normalized aggregate {aggregate.get('group_id')} into unit with text length {len(normalized_unit.text_repr)}")
    
    # Если указан output_file, сохраняем результат
    if output_file:
        # Инициализируем хранилище знаний
        knowledge_store = JSONLKnowledgeStore({
            "file_name": Path(output_file).name,
            "data_dir": Path(output_file).parent
        })
        
        # Сохраняем нормализованную единицу
        unit_id = await knowledge_store.store(normalized_unit)
        logger.info(f"Saved normalized unit with ID {unit_id} to {output_file}")
    else:
        # Иначе выводим результат в консоль
        unit_dict = normalized_unit.model_dump(mode="json")
        print(json.dumps(unit_dict, indent=2, ensure_ascii=False))
        

async def main_async(args):
    """
    Асинхронная точка входа для CLI-утилиты.
    
    Args:
        args: Аргументы командной строки
    """
    # Загружаем агрегат
    if args.aggregate_file:
        aggregate = await load_aggregate_from_file(args.aggregate_file)
    elif args.jsonl_file:
        aggregate = await load_aggregate_from_jsonl(args.jsonl_file, args.group_id)
    else:
        logger.error("Either --aggregate-file or --jsonl-file must be specified")
        sys.exit(1)
        
    # Запускаем нормализатор
    await run_normalizer(args.config, aggregate, args.output)


def main():
    """
    Точка входа для CLI-утилиты.
    """
    parser = argparse.ArgumentParser(description="Normalizer Runner for Mindbank")
    
    # Источник агрегата
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--aggregate-file", help="Path to a JSON file with an aggregate")
    source_group.add_argument("--jsonl-file", help="Path to a JSONL file with aggregates")
    
    # Дополнительные параметры
    parser.add_argument("--group-id", help="Group ID to find in JSONL file (if --jsonl-file is specified)")
    parser.add_argument("--config", help="Path to normalizer config file")
    parser.add_argument("--output", help="Path to output file for normalized unit")
    parser.add_argument("--offline", action="store_true", help="Run in offline mode (use fallback providers)")
    parser.add_argument("--openai", action="store_true", help="Use OpenAI providers (default from .env)")
    
    args = parser.parse_args()
    
    # Если указан --offline, устанавливаем переменную окружения
    if args.offline:
        import os
        os.environ["NORMALIZER_OFFLINE_MODE"] = "1"
        logger.info("Running in offline mode")
    
    # Если указан --openai, явно указываем использование OpenAI провайдеров
    if args.openai:
        import os
        os.environ["NORMALIZER_TRANSCRIPT_PROVIDER"] = "openai"
        os.environ["NORMALIZER_CAPTION_PROVIDER"] = "openai"
        os.environ["NORMALIZER_EMBED_PROVIDER"] = "openai"
        os.environ["NORMALIZER_CLASSIFIER_PROVIDER"] = "openai"
        os.environ["NORMALIZER_OFFLINE_MODE"] = "0"
        logger.info("Using OpenAI providers from environment settings")
    
    # Запускаем асинхронную функцию
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main() 