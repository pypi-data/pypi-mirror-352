"""
Асинхронная очередь для обработки агрегатов.
"""
import asyncio
from typing import Any, Callable, Coroutine, Dict, List, Optional, TypeVar

T = TypeVar('T')  # Тип элемента в очереди

class AsyncProcessingQueue:
    """
    Асинхронная очередь для обработки элементов с поддержкой подписок на обработчики.
    """
    def __init__(self, maxsize: int = 0):
        """
        Инициализация очереди.
        
        Args:
            maxsize: Максимальный размер очереди (0 - без ограничений)
        """
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.processors: List[Callable[[T], Coroutine[Any, Any, Any]]] = []
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
    def add_processor(self, processor: Callable[[T], Coroutine[Any, Any, Any]]):
        """
        Добавляет обработчик в очередь.
        
        Args:
            processor: Асинхронная функция, обрабатывающая элементы очереди
        """
        self.processors.append(processor)
        
    async def put(self, item: T):
        """
        Добавляет элемент в очередь.
        
        Args:
            item: Элемент для обработки
        """
        await self.queue.put(item)
        
    async def _process_queue(self):
        """Обрабатывает элементы из очереди."""
        while self._running:
            try:
                item = await self.queue.get()
                
                # Пропускаем элемент через все обработчики
                for processor in self.processors:
                    try:
                        await processor(item)
                    except Exception as e:
                        # В реальной системе здесь должна быть более детальная обработка ошибок и логирование
                        print(f"Error in processor: {e}")
                
                # Помечаем задачу как выполненную
                self.queue.task_done()
            except asyncio.CancelledError:
                # Обработка отмены задачи
                break
            except Exception as e:
                # Обработка других ошибок
                print(f"Error processing queue: {e}")
                
    async def start(self):
        """Запускает обработку очереди."""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._process_queue())
        
    async def stop(self):
        """Останавливает обработку очереди."""
        if not self._running:
            return
            
        self._running = False
        
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
            self._task = None
    
    async def join(self):
        """Ожидает обработки всех элементов в очереди."""
        await self.queue.join()
    
    @property
    def is_running(self) -> bool:
        """Возвращает статус работы очереди."""
        return self._running
        
    def qsize(self) -> int:
        """Возвращает текущий размер очереди."""
        return self.queue.qsize() 