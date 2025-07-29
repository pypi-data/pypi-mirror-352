"""
Сервис для выбора провайдера на основе контекста.
"""
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, cast

from mindbank_poc.common.logging import get_logger

# Создаем типизированный параметр для провайдеров
T = TypeVar('T')

logger = get_logger(__name__)

class ProviderSelector(Generic[T]):
    """
    Сервис для выбора провайдера на основе контекста.
    Позволяет выбрать наиболее подходящий провайдер из списка доступных
    на основе архетипа, источника и метаданных.
    """
    
    @staticmethod
    def _check_metadata_condition(metadata: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """
        Проверяет соответствие метаданных условию.
        
        Args:
            metadata: Метаданные для проверки
            condition: Условие для проверки (key, operator, value)
            
        Returns:
            True, если метаданные соответствуют условию, иначе False
        """
        key = condition.get("key")
        operator = condition.get("operator", "eq")
        value = condition.get("value")
        
        # Если ключ отсутствует в метаданных, условие не выполняется
        if key not in metadata:
            return False
            
        metadata_value = metadata[key]
        
        # Проверяем условие в зависимости от оператора
        if operator == "eq":  # равно
            return metadata_value == value
        elif operator == "neq":  # не равно
            return metadata_value != value
        elif operator == "contains":  # содержит
            # Для строк проверяем вхождение подстроки
            if isinstance(metadata_value, str) and isinstance(value, str):
                return value in metadata_value
            # Для списков проверяем наличие элемента
            elif isinstance(metadata_value, list):
                return value in metadata_value
            return False
        elif operator == "gt":  # больше
            return metadata_value > value
        elif operator == "lt":  # меньше
            return metadata_value < value
        elif operator == "gte":  # больше или равно
            return metadata_value >= value
        elif operator == "lte":  # меньше или равно
            return metadata_value <= value
        elif operator == "in":  # в списке
            # Проверяем, что значение метаданных содержится в списке значений условия
            if isinstance(value, list):
                return metadata_value in value
            return False
        else:
            logger.warning(f"Неизвестный оператор: {operator}")
            return False
    
    @staticmethod
    def _check_filter_match(
        provider_filter: Dict[str, Any],
        archetype: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Проверяет, соответствует ли фильтр провайдера заданным параметрам.
        
        Args:
            provider_filter: Фильтр провайдера
            archetype: Архетип контента
            source: Источник контента
            metadata: Метаданные контента
            
        Returns:
            True, если фильтр соответствует параметрам, иначе False
        """
        # Проверяем архетип
        filter_archetypes = provider_filter.get("archetypes")
        if filter_archetypes and archetype:
            if archetype not in filter_archetypes:
                return False
                
        # Проверяем источник
        filter_sources = provider_filter.get("sources")
        if filter_sources and source:
            if source not in filter_sources:
                return False
                
        # Проверяем условия по метаданным
        filter_metadata_conditions = provider_filter.get("metadata_conditions")
        if filter_metadata_conditions and metadata:
            for condition in filter_metadata_conditions:
                if not ProviderSelector._check_metadata_condition(metadata, condition):
                    return False
                    
        # Если все проверки пройдены, фильтр соответствует параметрам
        return True
    
    @staticmethod
    def select_provider(
        providers: List[Dict[str, Any]],
        provider_type: str,
        archetype: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Выбирает наиболее подходящий провайдер на основе контекста.
        
        Args:
            providers: Список доступных провайдеров
            provider_type: Тип провайдера (embedding, classification и т.д.)
            archetype: Архетип контента
            source: Источник контента
            metadata: Метаданные контента
            
        Returns:
            Наиболее подходящий провайдер или None, если не найден
        """
        # Фильтруем провайдеры по типу
        filtered_providers = [p for p in providers if p.get("provider_type") == provider_type]
        
        if not filtered_providers:
            logger.warning(f"Не найдены провайдеры типа {provider_type}")
            return None
            
        # Для каждого провайдера проверяем его фильтры
        matching_filters = []
        
        for provider in filtered_providers:
            # Проверяем, есть ли у провайдера фильтры
            provider_filters = provider.get("filters", [])
            
            # Если у провайдера нет фильтров, проверяем поле supported_archetypes
            if not provider_filters:
                # Если архетип указан и провайдер поддерживает архетипы
                if archetype and "supported_archetypes" in provider:
                    supported_archetypes = provider.get("supported_archetypes", [])
                    if supported_archetypes and archetype not in supported_archetypes:
                        # Пропускаем провайдер, если он не поддерживает указанный архетип
                        continue
                
                # Добавляем провайдер с приоритетом 0 (базовый приоритет)
                matching_filters.append({
                    "provider": provider,
                    "priority": 0,
                    "config_override": None
                })
                continue
                
            # Проверяем каждый фильтр провайдера
            for provider_filter in provider_filters:
                if ProviderSelector._check_filter_match(provider_filter, archetype, source, metadata):
                    # Если фильтр соответствует параметрам, добавляем его в список
                    matching_filters.append({
                        "provider": provider,
                        "priority": provider_filter.get("priority", 0),
                        "config_override": provider_filter.get("config_override")
                    })
        
        # Если нет подходящих фильтров, возвращаем первый провайдер нужного типа
        if not matching_filters:
            logger.info(f"Не найдены подходящие фильтры для типа {provider_type}, архетипа {archetype}, источника {source}")
            return filtered_providers[0]
            
        # Сортируем фильтры по приоритету (по убыванию)
        matching_filters.sort(key=lambda x: x["priority"], reverse=True)
        
        # Берем фильтр с наивысшим приоритетом
        best_match = matching_filters[0]
        selected_provider = best_match["provider"]
        config_override = best_match["config_override"]
        
        # Если есть переопределение конфигурации, применяем его
        if config_override:
            # Создаем копию провайдера, чтобы не изменять оригинал
            provider_copy = selected_provider.copy()
            # Создаем копию текущей конфигурации
            current_config = provider_copy.get("current_config", {}).copy()
            # Применяем переопределение
            current_config.update(config_override)
            # Обновляем конфигурацию в копии провайдера
            provider_copy["current_config"] = current_config
            
            logger.info(f"Выбран провайдер {selected_provider['id']} с переопределением конфигурации")
            return provider_copy
        
        logger.info(f"Выбран провайдер {selected_provider['id']}")
        return selected_provider
    
    @staticmethod
    def select_provider_instance(
        providers: List[T],
        provider_type: str,
        provider_info_getter: callable,
        archetype: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[T]:
        """
        Выбирает наиболее подходящий экземпляр провайдера на основе контекста.
        
        Args:
            providers: Список доступных экземпляров провайдеров
            provider_type: Тип провайдера (embedding, classification и т.д.)
            provider_info_getter: Функция для получения информации о провайдере из экземпляра
            archetype: Архетип контента
            source: Источник контента
            metadata: Метаданные контента
            
        Returns:
            Наиболее подходящий экземпляр провайдера или None, если не найден
        """
        # Преобразуем экземпляры провайдеров в словари с информацией
        provider_infos = []
        provider_map = {}
        
        for provider in providers:
            provider_info = provider_info_getter(provider)
            provider_infos.append(provider_info)
            provider_map[provider_info["id"]] = provider
            
        # Выбираем наиболее подходящий провайдер
        selected_info = ProviderSelector.select_provider(
            provider_infos,
            provider_type,
            archetype,
            source,
            metadata
        )
        
        if not selected_info:
            return None
            
        # Возвращаем соответствующий экземпляр провайдера
        return provider_map.get(selected_info["id"])
