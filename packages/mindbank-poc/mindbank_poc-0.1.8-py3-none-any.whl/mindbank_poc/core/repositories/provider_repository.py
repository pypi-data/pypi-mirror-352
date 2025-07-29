"""
Repository for processing providers.
"""
import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type

from mindbank_poc.core.common.types import ProviderType
from mindbank_poc.core.models.provider import ProviderModel, ProviderFilter

logger = logging.getLogger(__name__)

class ProviderRepository(ABC):
    """Abstract base class for provider repositories."""

    @abstractmethod
    def get_all_providers(self) -> Dict[str, ProviderModel]:
        """Get all registered providers."""
        pass

    @abstractmethod
    def get_provider(self, provider_id: str) -> Optional[ProviderModel]:
        """Get a provider by ID."""
        pass

    @abstractmethod
    def save_provider(self, provider: ProviderModel) -> ProviderModel:
        """Save or update a provider."""
        pass

    @abstractmethod
    def update_provider_config(self, provider_id: str, config: Dict[str, Any]) -> Optional[ProviderModel]:
        """Update a provider's configuration."""
        pass

    @abstractmethod
    def add_provider_filter(self, provider_id: str, filter_data: ProviderFilter) -> Optional[ProviderModel]:
        """Add a filter to a provider."""
        pass

    @abstractmethod
    def delete_provider_filter(self, provider_id: str, filter_index: int) -> Optional[ProviderModel]:
        """Delete a filter from a provider."""
        pass

    @abstractmethod
    def get_provider_filters(self, provider_id: str) -> List[ProviderFilter]:
        """Get all filters for a provider."""
        pass
    
    @abstractmethod
    def get_providers_by_type(self, provider_type: ProviderType) -> List[ProviderModel]:
        """Get all providers of a specific type."""
        pass


class FileProviderRepository(ProviderRepository):
    """File-based implementation of ProviderRepository."""

    def __init__(self, file_path: str):
        """Initialize the repository with a file path."""
        self.file_path = os.path.abspath(file_path)
        self._providers: Dict[str, ProviderModel] = {}
        self._load_providers()

    def _load_providers(self) -> None:
        """Load providers from file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._providers = {
                        k: ProviderModel.parse_obj(v) for k, v in data.items()
                    }
                logger.info(f"Loaded {len(self._providers)} providers from {self.file_path}")
            except Exception as e:
                logger.error(f"Failed to load providers from {self.file_path}: {e}")
                self._providers = self._create_default_providers()
        else:
            logger.info(f"Provider file {self.file_path} not found, creating defaults")
            self._providers = self._create_default_providers()
            self._save_providers()

    def _create_default_providers(self) -> Dict[str, ProviderModel]:
        """Create default providers if no file exists."""
        return {
            "openai-embedding": ProviderModel(
                id="openai-embedding",
                name="openai",
                description="Провайдер эмбеддингов на основе OpenAI API",
                provider_type=ProviderType.EMBEDDING,
                supported_archetypes=["document", "note", "meeting_notes", "transcription"],
                config_schema={
                    "api_key": {"type": "string", "description": "API ключ OpenAI"},
                    "model": {"type": "string", "description": "Модель для эмбеддингов", "default": "text-embedding-ada-002"}
                },
                current_config={
                    "api_key": "",
                    "model": "text-embedding-ada-002"
                },
                status="active",
                capabilities=["text_embedding", "semantic_search"],
                filters=[]
            ),
            "openai-classifier": ProviderModel(
                id="openai-classifier",
                name="openai",
                description="Классификатор на основе OpenAI API",
                provider_type=ProviderType.CLASSIFICATION,
                supported_archetypes=["document", "note", "meeting_notes", "transcription"],
                config_schema={
                    "api_key": {"type": "string", "description": "API ключ OpenAI"},
                    "model": {"type": "string", "description": "Модель для классификации", "default": "gpt-3.5-turbo"}
                },
                current_config={
                    "api_key": "",
                    "model": "gpt-3.5-turbo"
                },
                status="active",
                capabilities=["text_classification", "entity_extraction"],
                filters=[]
            ),
            "fallback-embedding": ProviderModel(
                id="fallback-embedding",
                name="Fallback Embeddings",
                description="Локальный провайдер эмбеддингов (fallback)",
                provider_type=ProviderType.EMBEDDING,
                supported_archetypes=["document", "note", "meeting_notes", "transcription"],
                config_schema={},
                current_config={},
                status="active",
                capabilities=["text_embedding"],
                filters=[]
            ),
            "fallback-classifier": ProviderModel(
                id="fallback-classifier",
                name="Fallback Classifier",
                description="Локальный классификатор (fallback)",
                provider_type=ProviderType.CLASSIFICATION,
                supported_archetypes=["document", "note", "meeting_notes", "transcription"],
                config_schema={},
                current_config={},
                status="active",
                capabilities=["text_classification"],
                filters=[]
            )
        }

    def _save_providers(self) -> None:
        """Save providers to file."""
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            logger.debug(f"Attempting to save providers to file: {self.file_path}")
            
            # Convert ProviderModel objects to dictionaries, handling 'instance' attribute
            serializable = {}
            for k, v in self._providers.items():
                try:
                    # Convert to dict excluding 'instance' as it's not serializable
                    provider_dict = v.dict(exclude={"instance"})
                    serializable[k] = provider_dict
                except Exception as e:
                    logger.error(f"Failed to convert provider {k} to dict: {e}")
                    # Try a simple conversion fallback
                    try:
                        provider_dict = v.dict()
                        if "instance" in provider_dict:
                            provider_dict.pop("instance")
                        serializable[k] = provider_dict
                    except Exception as e2:
                        logger.error(f"Fallback conversion also failed for {k}: {e2}")
            
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved {len(serializable)} providers to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save providers to {self.file_path}: {e}", exc_info=True)

    def get_all_providers(self) -> Dict[str, ProviderModel]:
        """Get all registered providers."""
        return dict(self._providers)

    def get_provider(self, provider_id: str) -> Optional[ProviderModel]:
        """Get a provider by ID."""
        return self._providers.get(provider_id)

    def save_provider(self, provider: ProviderModel) -> ProviderModel:
        """Save or update a provider."""
        self._providers[provider.id] = provider
        self._save_providers()
        return provider

    def update_provider_config(self, provider_id: str, config: Dict[str, Any]) -> Optional[ProviderModel]:
        """Update a provider's configuration."""
        provider = self.get_provider(provider_id)
        if provider:
            provider.current_config.update(config)
            self._save_providers()
            return provider
        return None

    def add_provider_filter(self, provider_id: str, filter_data: ProviderFilter) -> Optional[ProviderModel]:
        """Add a filter to a provider."""
        provider = self.get_provider(provider_id)
        if provider:
            provider.filters.append(filter_data)
            self._save_providers()
            return provider
        return None

    def delete_provider_filter(self, provider_id: str, filter_index: int) -> Optional[ProviderModel]:
        """Delete a filter from a provider."""
        provider = self.get_provider(provider_id)
        if provider and 0 <= filter_index < len(provider.filters):
            provider.filters.pop(filter_index)
            self._save_providers()
            return provider
        return None

    def get_provider_filters(self, provider_id: str) -> List[ProviderFilter]:
        """Get all filters for a provider."""
        provider = self.get_provider(provider_id)
        if provider:
            return provider.filters
        return []
    
    def get_providers_by_type(self, provider_type: ProviderType) -> List[ProviderModel]:
        """Get all providers of a specific type."""
        return [p for p in self._providers.values() if p.provider_type == provider_type] 