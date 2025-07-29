"""
Отладочный коннектор для генерации тестовых данных
"""
import asyncio
import argparse
import json
import random
import uuid
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

# Импортируем ContentType из core
from mindbank_poc.core.common.types import ContentType 

# Настройки по умолчанию
DEFAULT_API_URL = "http://localhost:8000/ingest/entry"
DEFAULT_BATCH_SIZE = 10
DEFAULT_TOTAL_ENTRIES = 100
DEFAULT_SLEEP = 0.5  # секунды между отправками


class DebugConnectorClient:
    """
    Клиент отладочного коннектора, генерирующий тестовые данные
    и отправляющий их в Ingest API.
    """
    
    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        batch_size: int = DEFAULT_BATCH_SIZE,
        total_entries: int = DEFAULT_TOTAL_ENTRIES,
        sleep_duration: float = DEFAULT_SLEEP,
        collector_id: str = "debug-connector"
    ):
        """
        Инициализация клиента Debug коннектора.
        
        Args:
            api_url: URL API для отправки данных
            batch_size: Размер пакета данных
            total_entries: Общее количество записей для отправки
            sleep_duration: Пауза между отправками в секундах
            collector_id: Идентификатор коллектора
        """
        self.api_url = api_url
        self.batch_size = batch_size
        self.total_entries = total_entries
        self.sleep_duration = sleep_duration
        self.collector_id = collector_id
        
        # Используем UUID в качестве идентификатора группы по умолчанию
        self.group_id = str(uuid.uuid4())
        
        print(f"Debug коннектор инициализирован:")
        print(f"  API URL: {self.api_url}")
        print(f"  Batch size: {self.batch_size}")
        print(f"  Total entries: {self.total_entries}")
        print(f"  Sleep duration: {self.sleep_duration}s")
        print(f"  Collector ID: {self.collector_id}")
        print(f"  Group ID: {self.group_id}")

    def _generate_entry(self, index: int) -> Dict[str, Any]:
        """
        Генерирует тестовую запись.
        
        Args:
            index: Индекс записи
            
        Returns:
            Словарь с данными записи
        """
        # Определяем возможные типы записей
        entry_types: List[ContentType] = ["text", "image", "link", "code", "audio", "video", "file"]
        entry_type: ContentType = random.choice(entry_types)
        
        entry_id = f"debug-{self.group_id}-{index}"
        filename = f"debug_file_{index}.{entry_type if entry_type != 'link' else 'html'}"
        
        # Создаем разные типы данных в зависимости от типа записи
        payload = {}
        
        if entry_type == "text":
            payload = {
                "content": f"Это тестовый текст #{index} от Debug коннектора.",
            }
        elif entry_type == "code":
            language = random.choice(["python", "javascript", "rust"])
            payload = {
                "language": language,
                "content": f"# Code snippet #{index} in {language}\ndef func_{index}(): return {index}",
                "filename": f"snippet_{index}.{language}"
            }
        elif entry_type == "link":
            payload = {
                "url": f"https://example.com/debug/page_{index}",
                "title": f"Тестовая ссылка #{index}"
            }
        elif entry_type in ["image", "audio", "video", "file"]:
            # Генерируем плейсхолдер base64
            placeholder_data = f"placeholder data for {entry_type} #{index}".encode('utf-8')
            content_base64 = base64.b64encode(placeholder_data).decode('utf-8')
            payload = {
                "content_base64": content_base64,
                "filename": filename,
                "size_bytes": len(placeholder_data)
            }
            if entry_type in ["audio", "video"]:
                payload["duration"] = random.randint(10, 300) # Пример длительности в секундах
            if entry_type == "file":
                 payload["text_preview"] = f"Preview text for file #{index}..."[:50]
        else: # unknown or other types
             payload = {"data": f"Unknown data type for entry #{index}"}
             
        # Добавляем метаданные
        metadata = {
            "source": self.collector_id,
            "generated_at": datetime.now().isoformat(),
            "is_test": True
        }
        
        # Для последней записи в группе добавляем флаг is_last
        is_last = (index == self.total_entries - 1)
        if is_last:
            metadata["is_last"] = True
            
        # Создаем запись
        entry = {
            "collector_id": self.collector_id,
            "group_id": self.group_id,
            "entry_id": entry_id,
            "type": entry_type,
            "payload": payload,
            "metadata": metadata
        }
        
        return entry
        
    async def _send_entries(self, entries: List[Dict[str, Any]]) -> bool:
        """
        Отправляет пакет записей в API.
        
        Args:
            entries: Список записей для отправки
            
        Returns:
            True если отправка успешна, иначе False
        """
        try:
            async with httpx.AsyncClient() as client:
                for entry in entries:
                    response = await client.post(
                        self.api_url,
                        json=entry,
                        timeout=10.0
                    )
                    
                    if response.status_code not in [200, 201, 202]:
                        print(f"Ошибка при отправке записи {entry['entry_id']}: "
                              f"HTTP {response.status_code} - {response.text}")
                        return False
                    
                    # Выводим информацию об успешной отправке
                    is_last = entry.get("metadata", {}).get("is_last", False)
                    last_marker = " (последняя в группе)" if is_last else ""
                    print(f"Запись {entry['entry_id']} типа {entry['type']} "
                          f"успешно отправлена{last_marker}")
                    
            return True
        except Exception as e:
            print(f"Ошибка при отправке записей: {e}")
            return False
            
    async def run(self) -> None:
        """
        Запускает процесс генерации и отправки данных.
        """
        print(f"Запуск Debug коннектора. Будет отправлено {self.total_entries} записей "
              f"пакетами по {self.batch_size}")
        
        current_batch = []
        
        for i in range(self.total_entries):
            # Генерируем запись
            entry = self._generate_entry(i)
            current_batch.append(entry)
            
            # Проверяем, не достигли ли мы размера пакета
            if len(current_batch) >= self.batch_size:
                # Отправляем текущий пакет
                print(f"Отправка пакета из {len(current_batch)} записей...")
                success = await self._send_entries(current_batch)
                
                if not success:
                    print("Прерывание работы из-за ошибки отправки")
                    return
                
                # Очищаем пакет
                current_batch = []
                
                # Делаем паузу перед следующей отправкой
                if i < self.total_entries - 1:  # Если это не последняя итерация
                    print(f"Пауза {self.sleep_duration} секунд перед следующей отправкой...")
                    await asyncio.sleep(self.sleep_duration)
        
        # Отправляем оставшийся пакет, если он не пустой
        if current_batch:
            print(f"Отправка последнего пакета из {len(current_batch)} записей...")
            await self._send_entries(current_batch)
            
        print(f"Debug коннектор завершил работу. Отправлено {self.total_entries} записей.")


async def main_async(args) -> None:
    """
    Асинхронная точка входа для запуска коннектора.
    """
    client = DebugConnectorClient(
        api_url=args.api_url,
        batch_size=args.batch_size,
        total_entries=args.total,
        sleep_duration=args.sleep,
        collector_id=args.collector_id
    )
    
    await client.run()


def main():
    """
    Точка входа для запуска из командной строки.
    """
    parser = argparse.ArgumentParser(description="Debug Connector для Mindbank")
    parser.add_argument("--api-url", default=DEFAULT_API_URL,
                      help=f"URL Ingest API (по умолчанию: {DEFAULT_API_URL})")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                      help=f"Размер пакета (по умолчанию: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--total", type=int, default=DEFAULT_TOTAL_ENTRIES,
                      help=f"Общее количество записей (по умолчанию: {DEFAULT_TOTAL_ENTRIES})")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP,
                      help=f"Пауза между отправками в секундах (по умолчанию: {DEFAULT_SLEEP})")
    parser.add_argument("--collector-id", default="debug-connector",
                      help="Идентификатор коллектора")
                      
    args = parser.parse_args()
    
    # Запускаем асинхронную функцию
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main() 