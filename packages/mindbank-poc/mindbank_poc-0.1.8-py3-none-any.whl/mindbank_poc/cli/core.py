#!/usr/bin/env python
"""CLI команда для запуска API ядра Mindbank"""

import argparse
import sys
import os
import uvicorn

from mindbank_poc.core.config.settings import settings


def main():
    """Точка входа для команды run-core."""
    parser = argparse.ArgumentParser(description="Запуск API ядра Mindbank")
    parser.add_argument("--host", default=settings.api.host, help="Хост для запуска API (по умолчанию из настроек)")
    parser.add_argument("--port", type=int, default=settings.api.port, help="Порт для запуска API (по умолчанию из настроек)")
    parser.add_argument("--reload", action="store_true", default=settings.api.reload, help="Включить автоматическую перезагрузку при изменении кода")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error", "critical"], help="Уровень логирования")
    parser.add_argument("--offline-mode", action="store_true", default=settings.normalizer.offline_mode, help="Запуск в автономном режиме")
    parser.add_argument("--data-dir", help="Директория для хранения данных системы (файлы коннекторов, состояний, базы знаний)")
    parser.add_argument("--admin-key", help="Мастер-ключ администратора для доступа к защищенным API")
    
    args = parser.parse_args()
    
    # Переопределяем настройки
    settings.api.host = args.host
    settings.api.port = args.port
    settings.api.reload = args.reload
    settings.normalizer.offline_mode = args.offline_mode
    
    # Устанавливаем мастер-ключ, если он указан
    if args.admin_key:
        settings.auth.admin_api_key = args.admin_key
        print("Установлен мастер-ключ администратора")
    
    # Настройки директории данных
    if args.data_dir:
        # Проверяем и создаем директорию, если она не существует
        if not os.path.exists(args.data_dir):
            os.makedirs(args.data_dir)
            print(f"Создана директория для хранения данных: {args.data_dir}")
        
        # Создаем поддиректории, если их нет
        connector_dir = os.path.join(args.data_dir, "connectors")
        onboarding_dir = os.path.join(args.data_dir, "onboarding_states")
        knowledge_dir = os.path.join(args.data_dir, "knowledge_store")
        ingest_dir = os.path.join(args.data_dir, "ingest_jsonl")
        
        for directory in [connector_dir, onboarding_dir, knowledge_dir, ingest_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Создана поддиректория: {directory}")
        
        # Настраиваем пути в настройках
        settings.storage.data_dir = args.data_dir
        settings.storage.ingest_dir = ingest_dir
        settings.storage.knowledge_dir = knowledge_dir
        settings.connector.storage_path = os.path.join(connector_dir, "connectors.json")
        settings.connector.onboarding_states_path = onboarding_dir
        settings.connector.integration_keys_path = os.path.join(connector_dir, "integration_keys.json")
        settings.auth.fingerprint_tokens_path = os.path.join(connector_dir, "fingerprint_tokens.json")
        
        print(f"Данные будут храниться в директории: {args.data_dir}")
    
    print(f"Запуск API ядра Mindbank на {args.host}:{args.port}")
    print(f"Offline режим: {'включен' if args.offline_mode else 'выключен'}")
    
    try:
        uvicorn.run(
            "mindbank_poc.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("API ядро остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 