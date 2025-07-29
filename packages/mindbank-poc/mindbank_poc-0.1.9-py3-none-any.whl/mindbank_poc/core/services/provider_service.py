"""
Service for managing processing providers.
"""
from typing import Dict, List, Any, Optional, Type
import os
import logging
from functools import lru_cache
import pathlib

from mindbank_poc.core.common.types import ProviderType
from mindbank_poc.core.models.provider import ProviderModel, ProviderFilter
from mindbank_poc.core.repositories.provider_repository import ProviderRepository, FileProviderRepository
from mindbank_poc.core.config.settings import settings

logger = logging.getLogger(__name__)

# Get the absolute path to the project root directory
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent.parent.parent.absolute()

# Default path for provider data file using absolute path
DEFAULT_PROVIDERS_PATH = os.path.join(PROJECT_ROOT, "data", "providers.json")

class ProviderService:
    """Service for managing processing providers."""

    def __init__(self, repository: ProviderRepository):
        """Initialize with a repository instance."""
        self.repository = repository
        
    def get_all_providers(self) -> List[ProviderModel]:
        """Get all providers."""
        return list(self.repository.get_all_providers().values())
        
    def get_provider(self, provider_id: str) -> Optional[ProviderModel]:
        """Get a provider by ID."""
        return self.repository.get_provider(provider_id)
        
    def update_provider_config(self, provider_id: str, config: Dict[str, Any]) -> Optional[ProviderModel]:
        """Update a provider's configuration."""
        logger.debug(f"Updating provider config for {provider_id} with {config}")
        result = self.repository.update_provider_config(provider_id, config)
        if result:
            logger.debug(f"Provider config updated successfully for {provider_id}")
            # Invalidate the provider service cache
            get_provider_service.cache_clear()
            logger.debug("Provider service cache cleared")
        else:
            logger.debug(f"Failed to update provider config for {provider_id}")
        return result
        
    def add_provider_filter(self, provider_id: str, filter_data: ProviderFilter) -> Optional[ProviderModel]:
        """Add a filter to a provider."""
        result = self.repository.add_provider_filter(provider_id, filter_data)
        if result:
            # Invalidate the provider service cache
            get_provider_service.cache_clear()
        return result
        
    def delete_provider_filter(self, provider_id: str, filter_index: int) -> Optional[ProviderModel]:
        """Delete a filter from a provider."""
        result = self.repository.delete_provider_filter(provider_id, filter_index)
        if result:
            # Invalidate the provider service cache
            get_provider_service.cache_clear()
        return result
        
    def get_provider_filters(self, provider_id: str) -> List[ProviderFilter]:
        """Get all filters for a provider."""
        return self.repository.get_provider_filters(provider_id)
    
    def get_providers_by_type(self, provider_type: ProviderType) -> List[ProviderModel]:
        """Get all providers of a specific type."""
        return self.repository.get_providers_by_type(provider_type)
    
    def get_default_provider(self, provider_type: ProviderType) -> Optional[str]:
        """Get the default provider ID for a provider type."""
        # This could be stored in settings, database, or a separate file
        # For now, we use a simple dictionary mapping
        defaults = {
            ProviderType.EMBEDDING: "openai-embedding",
            ProviderType.CLASSIFICATION: "openai-classifier",
            ProviderType.TRANSCRIPTION: "openai-classifier",
            ProviderType.CAPTION: "openai-classifier",
            ProviderType.LLM_CHAT: "openai-llm-chat"
        }
        return defaults.get(provider_type)
    
    def set_default_provider(self, provider_type: ProviderType, provider_id: str) -> bool:
        """Set the default provider for a provider type."""
        # In a real implementation, this would update the defaults in a database or file
        # For now, we just validate that the provider exists
        provider = self.repository.get_provider(provider_id)
        if not provider:
            return False
        if provider.provider_type != provider_type:
            return False
            
        # In a real implementation, update the defaults configuration
        # For now just log the change
        logger.info(f"Setting default provider for {provider_type} to {provider_id}")
        # Invalidate the provider service cache
        get_provider_service.cache_clear()
        return True


@lru_cache()
def get_provider_service() -> ProviderService:
    """Get or create a singleton ProviderService instance."""
    # Use a fixed path for providers.json in the data directory 
    # instead of trying to get it from settings
    file_path = DEFAULT_PROVIDERS_PATH
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    logger.debug(f"Initializing provider repository with file path: {file_path}")
    repository = FileProviderRepository(file_path)
    logger.debug(f"Initialized provider service with {len(repository.get_all_providers())} providers")
    return ProviderService(repository) 