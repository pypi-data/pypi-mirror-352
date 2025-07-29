import time
import asyncio
from typing import Dict, List, Optional, Callable, Any, Set, Awaitable
from dataclasses import dataclass, field
import datetime

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.common.types import RawEntry, Aggregate

# Получаем логгер для этого модуля
logger = get_logger(__name__)

@dataclass
class BufferConfig:
    """Configuration for the InMemoryBuffer."""
    # Buffer will flush entries if they've been in buffer longer than this (seconds)
    timeout_seconds: float = 60.0
    # Max number of entries to keep per group before flushing
    max_entries_per_group: int = 100
    # How often to check for timeouts (seconds)
    check_interval_seconds: float = 5.0

class InMemoryBuffer:
    """
    A buffer that stores RawEntry objects in memory and outputs Aggregate objects.
    
    It will output an Aggregate when:
    1. The timeout for a group is reached
    2. An entry with is_last=True is received
    3. The max entries per group is reached
    """
    
    def __init__(self, 
                 config: BufferConfig = None,
                 on_aggregate_callback: Optional[Callable[[Aggregate], Awaitable[None]]] = None):
        """
        Initialize the buffer.
        
        Args:
            config: Configuration for the buffer
            on_aggregate_callback: Async callback to call when an aggregate is formed
        """
        self.config = config or BufferConfig()
        self.on_aggregate_callback = on_aggregate_callback
        
        # Store entries by group_id
        self._buffer: Dict[str, List[RawEntry]] = {}
        # Keep track of when each group was last updated
        self._last_update: Dict[str, float] = {}
        # Keep track of groups marked for flushing (is_last received)
        self._flush_marked: Set[str] = set()
        
        # Flag to control the background task
        self._running = False
        # Task that checks for timeouts
        self._timeout_task = None
        
        logger.info(f"InMemoryBuffer initialized with config: {self.config}")
        
    async def start(self):
        """Start the background timeout checking task."""
        if self._running:
            return
        
        self._running = True
        self._timeout_task = asyncio.create_task(self._check_timeouts())
        logger.info("InMemoryBuffer timeout checking task started")
        
    async def stop(self):
        """Stop the background timeout checking task and flush all remaining groups."""
        if not self._running:
            return
        
        self._running = False
        if self._timeout_task:
            self._timeout_task.cancel()
            try:
                await self._timeout_task
            except asyncio.CancelledError:
                pass
            
        # Flush all remaining groups
        group_ids = list(self._buffer.keys())
        for group_id in group_ids:
            await self._flush_group(group_id)
            
        logger.info("InMemoryBuffer stopped and all groups flushed")
        
    async def add_entry(self, entry: RawEntry):
        """Adds an entry to the buffer."""
        group_id = entry.group_id
        now = time.monotonic()

        if group_id not in self._buffer:
            self._buffer[group_id] = []
            # Устанавливаем время обновления/создания группы только если ее не было
            # или если group_timeout_seconds не переопределяет логику старта таймера
            self._last_update[group_id] = now 
            logger.debug(f"New group {group_id} created in buffer.")

        self._buffer[group_id].append(entry)
        
        # Обновляем время последнего апдейта группы, если только не пришел is_last
        # или если group_timeout_seconds не диктует иную логику (но сам по себе он не меняет last_update)
        if not entry.metadata.get("is_last", False):
            self._last_update[group_id] = now 
        
        logger.debug(f"Entry {entry.entry_id} added to group {group_id}. Group size: {len(self._buffer[group_id])}")

        # Check for flush conditions immediately after adding
        # Это немного изменит логику, т.к. flush_marked используется в _check_timeouts
        # Если is_last, то сразу помечаем и пытаемся сбросить.
        if entry.metadata.get("is_last", False):
            logger.info(f"Group {group_id} marked for flushing due to 'is_last' flag on entry {entry.entry_id}.")
            self._flush_marked.add(group_id)
            await self._flush_group_if_marked(group_id) # Попытка сбросить сразу
        
        # Проверка на максимальное количество записей
        elif len(self._buffer[group_id]) >= self.config.max_entries_per_group:
            logger.info(f"Group {group_id} reached max entries ({self.config.max_entries_per_group}). Flushing.")
            await self._flush_group(group_id, reason="max_entries_reached")

    async def _flush_group_if_marked(self, group_id: str):
        if group_id in self._flush_marked:
            await self._flush_group(group_id, reason="is_last_received")

    async def _check_timeouts(self):
        """Periodically checks for timed out groups and flushes them."""
        while self._running:
            await asyncio.sleep(self.config.check_interval_seconds)
            now = time.monotonic()
            # Копируем ключи, так как словарь может измениться во время итерации
            for group_id in list(self._buffer.keys()):
                if group_id not in self._buffer: # Группа могла быть уже сброшена
                    continue

                # Получаем специфичный таймаут для группы, если он есть в метаданных ПОСЛЕДНЕЙ записи
                # Это упрощение - предполагаем, что таймаут для группы консистентен или берется из последней записи
                # Для более сложной логики нужно хранить group_timeout_seconds на уровне группы.
                group_specific_timeout = self.config.timeout_seconds # По умолчанию глобальный
                if self._buffer[group_id]:
                    # Попробуем найти таймаут в метаданных любой из записей группы.
                    # Возьмем первый валидный найденный или последний, если их несколько.
                    # Для простоты пока можно ожидать, что он если есть, то в одной из записей.
                    # Наиболее логично, если он есть в первой записи группы или консистентен.
                    # В данном варианте ищем в последней добавленной записи.
                    timeout_from_meta = self._buffer[group_id][-1].metadata.get("group_timeout_seconds")
                    if isinstance(timeout_from_meta, (int, float)) and timeout_from_meta > 0:
                        # Можно добавить проверку на максимальный/минимальный допустимый таймаут из конфига, если нужно
                        group_specific_timeout = float(timeout_from_meta)
                        logger.debug(f"Using group specific timeout {group_specific_timeout}s for group {group_id}")
                
                last_update_time = self._last_update.get(group_id, now)
                if (now - last_update_time) > group_specific_timeout:
                    logger.info(f"Group {group_id} timed out after {now - last_update_time:.2f}s (limit: {group_specific_timeout}s). Flushing.")
                    await self._flush_group(group_id, reason="timeout")
                elif group_id in self._flush_marked: # Проверяем снова, если is_last пришел между проверками таймаута
                    await self._flush_group(group_id, reason="is_last_marked_during_check")

    async def _flush_group(self, group_id: str, reason: str):
        """
        Flush a group: create an Aggregate and call the callback.
        """
        if group_id not in self._buffer:
            return
            
        entries = self._buffer.pop(group_id)
        self._last_update.pop(group_id, None)
        if group_id in self._flush_marked:
            self._flush_marked.remove(group_id)
            
        if not entries:
            return
            
        # Create an Aggregate
        aggregate = Aggregate(
            group_id=group_id,
            entries=entries,
            aggregated_at=datetime.datetime.now(datetime.UTC),
            metadata={"source": "buffer", "count": len(entries)}
        )
        
        logger.info(f"Flushing group {group_id} with {len(entries)} entries. Reason: {reason}")
        
        # Call the callback if provided
        if self.on_aggregate_callback:
            try:
                await self.on_aggregate_callback(aggregate)
            except Exception as e:
                logger.error(f"Error in on_aggregate_callback: {e}")
                
        return aggregate 