"""
Mindbank POC - инструмент для агрегации контента 
и интеграции с базой знаний.
"""

# Загружаем переменные окружения из .env в самом начале
import os
from pathlib import Path

# Пытаемся загрузить python-dotenv, если установлен
try:
    from dotenv import load_dotenv
    # Ищем .env файл в разных расположениях
    env_paths = [
        Path.cwd() / '.env',                         # текущая директория
        Path(__file__).parents[2] / '.env',          # корень проекта при src layout
        Path.home() / '.mindbank.env',               # домашняя директория пользователя
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            print(f"Loading environment from {env_path}")
            load_dotenv(dotenv_path=env_path, override=True)
            break
except ImportError:
    import warnings
    warnings.warn("python-dotenv not installed. Environment variables may not be loaded correctly.")

# Устанавливаем NORMALIZER_OFFLINE_MODE принудительно на основе значения в окружении
# Это необходимо для исправления проблемы с парсингом булевых значений
env_offline_mode = os.getenv("NORMALIZER_OFFLINE_MODE", "").lower()
if env_offline_mode in ("true", "1", "yes", "y", "on"):
    os.environ["NORMALIZER_OFFLINE_MODE"] = "1"
    print("NORMALIZER_OFFLINE_MODE set to True")
else:
    os.environ["NORMALIZER_OFFLINE_MODE"] = "0"
    print("NORMALIZER_OFFLINE_MODE set to False")
