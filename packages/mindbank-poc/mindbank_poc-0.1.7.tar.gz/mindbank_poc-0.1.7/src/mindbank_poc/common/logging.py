"""
Централизованная настройка логирования для всех компонентов Mindbank.

Этот модуль предоставляет единую точку настройки логирования с помощью loguru.
Он поддерживает вывод логов в консоль и файлы, с возможностью
настройки уровня логирования для разных компонентов.
"""

import sys
import os
from pathlib import Path
from loguru import logger
from typing import Optional, Dict, Any

# Определяем базовую директорию для логов
DEFAULT_LOG_DIR = Path("logs")

# Словарь настроек по умолчанию
DEFAULT_SETTINGS = {
    "level": "INFO",  # Уровень логов по умолчанию для консоли
    "file_level": "DEBUG",  # Уровень логов по умолчанию для файла
    "rotation": "10 MB",  # Ротация при достижении 10MB
    "retention": "1 week",  # Хранение логов 1 неделю
    "compression": "zip",  # Сжатие ротированных логов
    "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
}

def setup_logging(
    component: str,
    log_dir: Optional[Path] = None,
    settings: Optional[Dict[str, Any]] = None,
    add_console_handler: bool = True,
    add_file_handler: bool = True,
    env_var_prefix: str = "MINDBANK_LOG"
) -> None:
    """
    Настраивает логирование для компонента.
    
    Args:
        component: Название компонента (например, "api", "core", "connector-telegram")
        log_dir: Директория для хранения логов (по умолчанию "logs")
        settings: Дополнительные настройки, которые переопределяют значения по умолчанию
        add_console_handler: Добавлять ли обработчик для вывода в консоль
        add_file_handler: Добавлять ли обработчик для вывода в файл
        env_var_prefix: Префикс переменных окружения для конфигурации
    """
    # Объединяем настройки по умолчанию с пользовательскими
    config = DEFAULT_SETTINGS.copy()
    if settings:
        config.update(settings)
    
    # Проверяем переменные окружения, которые могут переопределить настройки
    env_level = os.environ.get(f"{env_var_prefix}_LEVEL")
    env_file_level = os.environ.get(f"{env_var_prefix}_FILE_LEVEL")
    
    if env_level:
        config["level"] = env_level
    if env_file_level:
        config["file_level"] = env_file_level
    
    # Установка директории для логов
    log_dir = log_dir or DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Удаляем все существующие обработчики
    logger.remove()
    
    # Добавляем обработчик для вывода в консоль, если требуется
    if add_console_handler:
        logger.add(
            sys.stderr,
            format=config["format"],
            level=config["level"],
            filter=lambda record: record["extra"].get("component", component) == component
        )
    
    # Добавляем обработчик для вывода в файл, если требуется
    if add_file_handler:
        log_file = log_dir / f"{component}.log"
        logger.add(
            log_file,
            format=config["format"],
            level=config["file_level"],
            rotation=config["rotation"],
            retention=config["retention"],
            compression=config["compression"],
            filter=lambda record: record["extra"].get("component", component) == component
        )
    
    # Добавляем контекстную информацию о компоненте
    component_logger = logger.bind(component=component)
    
    # Логируем старт настройки
    component_logger.info(f"Настройка логирования для компонента {component} завершена")
    component_logger.debug(f"Уровень логирования консоли: {config['level']}")
    component_logger.debug(f"Уровень логирования файла: {config['file_level']}")
    if add_file_handler:
        component_logger.debug(f"Файл логов: {log_file}")

def get_logger(module_name: str):
    """
    Возвращает логгер для конкретного модуля.
    
    Args:
        module_name: Имя модуля (обычно __name__)
    
    Returns:
        Объект логгера с привязанным именем модуля
    """
    return logger.bind(name=module_name)
