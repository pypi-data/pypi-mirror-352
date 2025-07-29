"""
Defines the interface for storing and retrieving connector onboarding state.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict
from uuid import UUID

from mindbank_poc.common.logging import get_logger
from mindbank_poc.core.connectors.schemas_onboarding import ConnectorOnboardingState

class OnboardingStateRepository(ABC):
    """
    Abstract base class for an onboarding state repository.

    This interface defines how the state of a connector's onboarding process
    is persisted and retrieved. Concrete implementations will handle the
    actual storage mechanism (e.g., in-memory, file-based, database).
    """

    @abstractmethod
    async def get_state(self, connector_id: UUID) -> Optional[ConnectorOnboardingState]:
        """
        Retrieves the onboarding state for a given connector.

        Args:
            connector_id: The UUID of the connector.

        Returns:
            The ConnectorOnboardingState if found, otherwise None.
        """
        pass

    @abstractmethod
    async def save_state(self, state: ConnectorOnboardingState) -> None:
        """
        Saves or updates the onboarding state for a connector.

        Args:
            state: The ConnectorOnboardingState to save.
        """
        pass

    @abstractmethod
    async def delete_state(self, connector_id: UUID) -> None:
        """
        Deletes the onboarding state for a given connector.

        Args:
            connector_id: The UUID of the connector whose state is to be deleted.
        """
        pass

# Added InMemoryOnboardingStateRepository implementation
class InMemoryOnboardingStateRepository(OnboardingStateRepository):
    """
    In-memory implementation of the OnboardingStateRepository.
    Suitable for testing or single-instance deployments where persistence is not required.
    """
    def __init__(self):
        self._states: Dict[UUID, ConnectorOnboardingState] = {}

    async def get_state(self, connector_id: UUID) -> Optional[ConnectorOnboardingState]:
        """Retrieves the onboarding state for a given connector."""
        return self._states.get(connector_id)

    async def save_state(self, state: ConnectorOnboardingState) -> None:
        """Saves or updates the onboarding state for a connector."""
        self._states[state.connector_id] = state

    async def delete_state(self, connector_id: UUID) -> None:
        """Deletes the onboarding state for a given connector."""
        if connector_id in self._states:
            del self._states[connector_id]
# End of InMemoryOnboardingStateRepository implementation

import json
import os
from pathlib import Path
import aiofiles
from datetime import datetime

class FileOnboardingStateRepository(OnboardingStateRepository):
    """
    File-based implementation of the OnboardingStateRepository.
    Stores each connector's onboarding state in a separate JSON file.
    """
    def __init__(self, storage_path: str):
        """
        Initialize the repository with a path for storing state files.
        
        Args:
            storage_path: Directory where state files will be stored
        """
        self._storage_path = Path(storage_path)
        # Create directory if it doesn't exist
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
    def _get_file_path(self, connector_id: UUID) -> Path:
        """Get the file path for a specific connector's state."""
        return self._storage_path / f"{connector_id}.json"
        
    async def get_state(self, connector_id: UUID) -> Optional[ConnectorOnboardingState]:
        """
        Retrieves the onboarding state for a given connector from its file.
        
        Args:
            connector_id: The UUID of the connector
            
        Returns:
            The ConnectorOnboardingState if found, otherwise None
        """
        file_path = self._get_file_path(connector_id)
        if not file_path.exists():
            return None
            
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                state_dict = json.loads(content)
                # Convert string connector_id back to UUID if needed
                if 'connector_id' in state_dict and isinstance(state_dict['connector_id'], str):
                    state_dict['connector_id'] = UUID(state_dict['connector_id'])
                return ConnectorOnboardingState(**state_dict)
        except (json.JSONDecodeError, IOError) as e:
            # Log error but don't raise to maintain interface contract
            logger = get_logger(__name__)
            logger.error(f"Error reading onboarding state for {connector_id}: {e}")
            return None
            
    async def save_state(self, state: ConnectorOnboardingState) -> None:
        """
        Saves or updates the onboarding state for a connector to its file.
        
        Args:
            state: The ConnectorOnboardingState to save
        """
        file_path = self._get_file_path(state.connector_id)
        
        try:
            # Add a timestamp for debugging/auditing
            serializable_state = state.model_dump()
            serializable_state['_last_saved'] = datetime.now().isoformat()
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(serializable_state, default=str, indent=2, ensure_ascii=False))
        except IOError as e:
            # Log error but don't raise to maintain interface contract
            logger = get_logger(__name__)
            logger.error(f"Error saving onboarding state for {state.connector_id}: {e}")
            
    async def delete_state(self, connector_id: UUID) -> None:
        """
        Deletes the onboarding state file for a given connector.
        
        Args:
            connector_id: The UUID of the connector whose state is to be deleted
        """
        file_path = self._get_file_path(connector_id)
        
        if file_path.exists():
            try:
                os.remove(file_path)
            except IOError as e:
                # Log error but don't raise to maintain interface contract
                logger = get_logger(__name__)
                logger.error(f"Error deleting onboarding state for {connector_id}: {e}") 