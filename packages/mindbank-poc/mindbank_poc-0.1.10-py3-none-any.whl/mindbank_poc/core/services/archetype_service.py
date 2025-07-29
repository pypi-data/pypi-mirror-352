"""
Сервис для управления архетипами в системе.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from mindbank_poc.core.config.settings import get_settings

class ArchetypeInfo(BaseModel):
    """Информация об архетипе"""
    name: str = Field(description="Название архетипа")
    description: str = Field(description="Описание архетипа")
    is_system: bool = Field(description="Является ли архетип системным")
    usage_count: int = Field(default=0, description="Количество использований")
    last_used: Optional[datetime] = Field(default=None, description="Последнее использование")

class ArchetypeService:
    """Сервис для управления архетипами в системе."""
    
    # Предопределенные архетипы
    _PREDEFINED_ARCHETYPES = {
        "document": "Документ (статья, отчет, и т.д.)",
        "note": "Заметка или короткая запись",
        "meeting_notes": "Заметки с совещания или встречи",
        "meeting_transcript": "Транскрипция встречи",
        "transcription": "Транскрипция аудио или видео",
        "code_snippet": "Фрагмент кода",
        "chat": "Чат или диалог",
        "email": "Электронное письмо",
        "task": "Задача или поручение",
        "generic": "Общий тип контента"
    }
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Инициализация сервиса архетипов.
        
        Args:
            storage_path: Путь к файлу для хранения обнаруженных архетипов. 
                          Если None, используется только хранение в памяти.
        """
        self._storage_path = storage_path
        # Системные архетипы
        self._predefined_archetypes: Dict[str, ArchetypeInfo] = {
            name: ArchetypeInfo(
                name=name,
                description=desc,
                is_system=True,
                usage_count=0
            ) for name, desc in self._PREDEFINED_ARCHETYPES.items()
        }
        # Обнаруженные пользовательские архетипы
        self._discovered_archetypes: Dict[str, ArchetypeInfo] = {}
        
        # Загружаем сохраненные архетипы, если есть файл
        self._load_archetypes()
    
    def _load_archetypes(self) -> None:
        """Загружает обнаруженные архетипы из файла, если он существует."""
        if not self._storage_path or not os.path.exists(self._storage_path):
            return
            
        try:
            with open(self._storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                # Преобразуем last_used из строки в datetime, если оно есть
                if "last_used" in item and item["last_used"]:
                    item["last_used"] = datetime.fromisoformat(item["last_used"])
                
                # Создаем объект ArchetypeInfo и добавляем в словарь
                archetype = ArchetypeInfo(**item)
                self._discovered_archetypes[archetype.name] = archetype
        except Exception as e:
            # Если файл поврежден или другая ошибка, игнорируем
            print(f"Error loading archetypes from {self._storage_path}: {e}")
    
    def _save_archetypes(self) -> None:
        """Сохраняет обнаруженные архетипы в файл, если указан путь."""
        if not self._storage_path:
            return
            
        # Создаем папку, если ее нет
        os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
        
        try:
            # Сериализуем словарь в список и сохраняем
            data = [archetype.dict() for archetype in self._discovered_archetypes.values()]
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving archetypes to {self._storage_path}: {e}")
    
    def register_usage(self, archetype_name: str, description: Optional[str] = None) -> None:
        """
        Регистрирует использование архетипа в системе.
        
        Args:
            archetype_name: Имя архетипа
            description: Опциональное описание для нового архетипа
        """
        now = datetime.now()
        
        # Если это предопределенный архетип, только обновляем статистику
        if archetype_name in self._predefined_archetypes:
            self._predefined_archetypes[archetype_name].usage_count += 1
            self._predefined_archetypes[archetype_name].last_used = now
            return
            
        # Если это новый архетип, добавляем в словарь обнаруженных
        if archetype_name not in self._discovered_archetypes:
            self._discovered_archetypes[archetype_name] = ArchetypeInfo(
                name=archetype_name,
                description=description or f"Пользовательский архетип '{archetype_name}'",
                is_system=False,
                usage_count=1,
                last_used=now
            )
        else:
            # Если уже существует, обновляем статистику
            self._discovered_archetypes[archetype_name].usage_count += 1
            self._discovered_archetypes[archetype_name].last_used = now
            
            # Если предоставлено описание и текущее - автогенерированное, обновляем
            current_desc = self._discovered_archetypes[archetype_name].description
            if description and current_desc.startswith("Пользовательский архетип"):
                self._discovered_archetypes[archetype_name].description = description
        
        # Сохраняем изменения
        self._save_archetypes()
    
    def get_all_archetypes(self) -> List[ArchetypeInfo]:
        """
        Возвращает все доступные архетипы (предопределенные + обнаруженные).
        
        Returns:
            Список объектов ArchetypeInfo
        """
        # Объединяем словари и конвертируем в список
        return list(self._predefined_archetypes.values()) + list(self._discovered_archetypes.values())
    
    def get_archetype_info(self, name: str) -> Optional[ArchetypeInfo]:
        """
        Получает информацию о конкретном архетипе.
        
        Args:
            name: Имя архетипа
            
        Returns:
            Объект ArchetypeInfo или None, если архетип не найден
        """
        if name in self._predefined_archetypes:
            return self._predefined_archetypes[name]
        return self._discovered_archetypes.get(name)

# Синглтон для доступа к сервису в приложении
_instance = None

def get_archetype_service() -> ArchetypeService:
    """
    Фабричная функция для получения экземпляра ArchetypeService.
    Реализует паттерн Singleton.
    
    Returns:
        Экземпляр ArchetypeService
    """
    global _instance
    if _instance is None:
        # Получаем путь к файлу архетипов из настроек приложения
        settings = get_settings()
        storage_path = os.path.join(settings.storage.data_dir, "archetypes.json")
        _instance = ArchetypeService(storage_path)
    return _instance 