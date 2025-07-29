"""
Коннектор для обработки файлов из файловой системы

Этот коннектор сканирует указанную директорию и отправляет содержимое файлов в Ingest API.
"""
import asyncio
import argparse
import os
import json
import uuid
import base64 # Import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import httpx

# Импортируем ContentType из core и утилиты
from mindbank_poc.core.common.types import ContentType 
from mindbank_poc.core.common.utils import get_content_type_from_extension, get_language_from_extension

# Настройки по умолчанию
DEFAULT_API_URL = "http://localhost:8000/ingest/entry"
DEFAULT_BATCH_SIZE = 5
# Добавим расширения для изображений, аудио, видео
DEFAULT_EXTENSIONS = [".txt", ".md", ".json", ".py", ".js", ".html", ".css", ".jpg", ".jpeg", ".png", ".gif", ".mp3", ".wav", ".mp4", ".avi", ".mov", ".pdf"]
DEFAULT_SLEEP = 0.5  # секунды между отправками файлов
TEXT_PREVIEW_LENGTH = 200 # Длина превью для файлов

class FileSystemConnectorClient:
    """
    Клиент файлового коннектора, который сканирует файловую систему 
    и отправляет содержимое файлов в Ingest API.
    """
    
    def __init__(
        self,
        folder_path: str,
        api_url: str = DEFAULT_API_URL,
        batch_size: int = DEFAULT_BATCH_SIZE,
        collector_id: str = "filesystem-connector",
        file_extensions: List[str] = DEFAULT_EXTENSIONS,
        sleep_duration: float = DEFAULT_SLEEP
    ):
        """
        Инициализация клиента файлового коннектора.
        
        Args:
            folder_path: Путь к директории для сканирования
            api_url: URL API для отправки данных
            batch_size: Размер пакета данных
            collector_id: Идентификатор коллектора
            file_extensions: Список расширений файлов для обработки
            sleep_duration: Пауза между отправками в секундах
        """
        self.folder_path = Path(folder_path)
        self.api_url = api_url
        self.batch_size = batch_size
        self.collector_id = collector_id
        self.file_extensions = [ext.lower() for ext in file_extensions] # Приводим к нижнему регистру
        self.sleep_duration = sleep_duration
        
        # Используем UUID в качестве идентификатора группы
        self.group_id = str(uuid.uuid4())
        
        print(f"FileSystem коннектор инициализирован:")
        print(f"  Директория: {self.folder_path.resolve()}")
        print(f"  API URL: {self.api_url}")
        print(f"  Расширения файлов: {self.file_extensions}")
        print(f"  Batch size: {self.batch_size}")
        print(f"  Sleep duration: {self.sleep_duration}s")
        print(f"  Collector ID: {self.collector_id}")
        print(f"  Group ID: {self.group_id}")

    def scan_directory(self) -> List[Path]:
        """
        Сканирует директорию и возвращает список файлов с заданными расширениями.
        
        Returns:
            Список путей к файлам
        """
        if not self.folder_path.exists():
            print(f"Ошибка: директория {self.folder_path} не существует")
            return []
            
        if not self.folder_path.is_dir():
            print(f"Ошибка: {self.folder_path} не является директорией")
            return []
            
        files = []
        
        for file_path in self.folder_path.glob('**/*'):
            # Проверяем расширение в нижнем регистре
            if file_path.is_file() and file_path.suffix.lower() in self.file_extensions:
                files.append(file_path)
                
        print(f"Найдено {len(files)} файлов с расширениями {self.file_extensions}")
        return files
    
    async def process_file(self, file_path: Path, is_last: bool = False) -> bool:
        """
        Обрабатывает файл и отправляет его содержимое в API.
        
        Args:
            file_path: Путь к обрабатываемому файлу
            is_last: Флаг, указывающий, является ли файл последним в группе
        
        Returns:
            True в случае успеха, иначе False
        """
        try:
            # Определяем тип контента с помощью утилиты
            file_ext = file_path.suffix.lower()
            content_type = get_content_type_from_extension(file_ext)
            
            # Подготавливаем полезную нагрузку
            payload: Dict[str, Any] = {
                "filename": file_path.name,
                "path": str(file_path.relative_to(self.folder_path.parent)), # Путь относительно родителя папки
                "size_bytes": file_path.stat().st_size
            }
            text_content = None
            
            # Читаем содержимое файла
            if content_type in ["text", "code", "link"]: # Читаем как текст
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    payload["content"] = text_content
                    if content_type == "code":
                        # Используем утилиту для определения языка
                        payload["language"] = get_language_from_extension(file_ext)
                        
                except UnicodeDecodeError:
                    print(f"Предупреждение: Файл {file_path} не в UTF-8, читаем как бинарный.")
                    # Если не UTF-8, читаем как бинарный
                    content_type = "file"
                    with open(file_path, 'rb') as f:
                        file_bytes = f.read()
                    payload["content_base64"] = base64.b64encode(file_bytes).decode('utf-8')
                except Exception as e:
                     print(f"Ошибка чтения файла {file_path} как текста: {e}")
                     return False # Пропускаем файл, если ошибка чтения
            else: # Читаем как бинарный
                try:
                    with open(file_path, 'rb') as f:
                        file_bytes = f.read()
                    payload["content_base64"] = base64.b64encode(file_bytes).decode('utf-8')
                    
                    # Попытка извлечь текстовое превью для бинарных файлов
                    if content_type == "file":
                        try:
                            # Пытаемся декодировать начало файла как UTF-8
                            preview = file_bytes[:TEXT_PREVIEW_LENGTH * 2].decode('utf-8', errors='ignore')
                            payload["text_preview"] = preview[:TEXT_PREVIEW_LENGTH]
                        except Exception:
                            pass # Игнорируем ошибки декодирования превью
                except Exception as e:
                    print(f"Ошибка чтения файла {file_path} как бинарного: {e}")
                    return False # Пропускаем файл, если ошибка чтения

            # Создаем запись
            entry_id = f"file-{self.group_id}-{file_path.name}"
            
            # Метаданные
            metadata = {
                "source": self.collector_id,
                "processed_at": datetime.now().isoformat(),
                "file_stats": {
                    "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                }
            }
            
            # Для последнего файла устанавливаем флаг is_last
            if is_last:
                metadata["is_last"] = True
                
            # Создаем запись
            entry = {
                "collector_id": self.collector_id,
                "group_id": self.group_id,
                "entry_id": entry_id,
                "type": content_type,
                "payload": payload,
                "metadata": metadata
            }
            
            # Отправляем запись в API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=entry,
                    timeout=30.0
                )
                
                if response.status_code not in [200, 201, 202]:
                    print(f"Ошибка при отправке файла {file_path.name}: "
                          f"HTTP {response.status_code} - {response.text}")
                    return False
                
            # Выводим информацию об успешной отправке
            last_marker = " (последний в группе)" if is_last else ""
            print(f"Файл {file_path.name} (тип: {content_type}) успешно отправлен{last_marker}")
            return True
            
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")
            return False
    
    async def run(self) -> None:
        """
        Запускает процесс сканирования директории и отправки файлов.
        """
        # Сканируем директорию
        files = self.scan_directory()
        
        if not files:
            print("Нет файлов для обработки")
            return
            
        print(f"Начинаем обработку {len(files)} файлов...")
        
        # Счетчик успешно обработанных файлов
        processed_count = 0
        
        # Обрабатываем файлы пакетами
        for i in range(0, len(files), self.batch_size):
            batch = files[i:i+self.batch_size]
            
            print(f"Обработка пакета {i//self.batch_size + 1} из {(len(files)-1)//self.batch_size + 1} "
                  f"({len(batch)} файлов)...")
            
            tasks = []
            for j, file_path in enumerate(batch):
                # Определяем, является ли файл последним в группе
                is_last = (i + j == len(files) - 1)
                # Создаем задачу для обработки файла
                tasks.append(self.process_file(file_path, is_last))

            # Запускаем обработку пакета асинхронно
            results = await asyncio.gather(*tasks)
            processed_count += sum(1 for success in results if success)
                
            # Если это не последний пакет, делаем паузу перед следующим
            if i + self.batch_size < len(files):
                print(f"Пауза {self.sleep_duration} секунд перед следующим пакетом...")
                await asyncio.sleep(self.sleep_duration)
        
        print(f"Обработка завершена. Успешно обработано {processed_count} из {len(files)} файлов.")


async def main_async(args) -> None:
    """
    Асинхронная точка входа для запуска коннектора.
    """
    extensions = args.extensions.split(",") if args.extensions else DEFAULT_EXTENSIONS
    
    client = FileSystemConnectorClient(
        folder_path=args.folder_path,
        api_url=args.api_url,
        batch_size=args.batch_size,
        collector_id=args.collector_id,
        file_extensions=extensions,
        sleep_duration=args.sleep
    )
    
    await client.run()


def main():
    """
    Точка входа для запуска из командной строки.
    """
    parser = argparse.ArgumentParser(description="FileSystem Connector для Mindbank")
    parser.add_argument("folder_path", help="Путь к директории для сканирования")
    parser.add_argument("--api-url", default=DEFAULT_API_URL,
                      help=f"URL Ingest API (по умолчанию: {DEFAULT_API_URL})")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                      help=f"Размер пакета (по умолчанию: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--extensions", 
                      help=f"Список расширений файлов через запятую (по умолчанию: {','.join(DEFAULT_EXTENSIONS)})")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP,
                      help=f"Пауза между отправками в секундах (по умолчанию: {DEFAULT_SLEEP})")
    parser.add_argument("--collector-id", default="filesystem-connector",
                      help="Идентификатор коллектора")
                      
    args = parser.parse_args()
    
    # Запускаем асинхронную функцию
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main() 