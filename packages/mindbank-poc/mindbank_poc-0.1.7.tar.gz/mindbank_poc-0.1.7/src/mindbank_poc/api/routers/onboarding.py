"""
API Router for connector onboarding process.
"""
from uuid import UUID
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path

from mindbank_poc.core.connectors.service import ConnectorService, get_connector_service
from mindbank_poc.core.connectors.schemas_onboarding import (
    OnboardingStepInfo,
    StepSubmissionPayload,
    StepSubmissionResult,
    ConnectorDirective,
    ConnectorDirectiveActionType
)
from mindbank_poc.common.logging import get_logger

logger = get_logger(__name__)

# Singleton class for FSM states
class FSMStateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FSMStateManager, cls).__new__(cls)
            cls._instance._states = {}
        return cls._instance
    
    def get_states(self):
        return self._states
    
    def set_states(self, states):
        self._states = states

# Create a singleton instance
fsm_state_manager = FSMStateManager()

def get_fsm_states():
    """Get the FSM states dictionary. This function is used to make it easier to patch in tests."""
    return fsm_state_manager.get_states()

def set_fsm_states(states):
    """Set the FSM states dictionary. This function is used to make it easier to patch in tests."""
    fsm_state_manager.set_states(states)

# Define step templates
step1 = OnboardingStepInfo(
    step_id="welcome",
    description="Welcome to the connector onboarding process",
    input_schema=None,
    messages=["Welcome! This is the first step of the onboarding process."],
    is_final_step=False
)

step2 = OnboardingStepInfo(
    step_id="enter_api_key",
    description="Enter your API key",
    input_schema={
        "type": "object",
        "properties": {
            "api_key": {
                "type": "string",
                "description": "Your API key"
            }
        },
        "required": ["api_key"]
    },
    messages=["Please enter your API key to continue."],
    is_final_step=False
)

completed_step = OnboardingStepInfo(
    step_id="completed",
    description="Onboarding completed successfully",
    input_schema=None,
    messages=["Congratulations! Onboarding has been completed successfully."],
    is_final_step=True
)

failed_step = OnboardingStepInfo(
    step_id="failed",
    description="Connector failed to process the request",
    input_schema=None,
    messages=["Onboarding has failed. Please try again."],
    is_final_step=True
)

# Helper functions for FSM state management
def get_fsm_state(connector_id: str) -> Dict[str, Any]:
    """Get the current FSM state for a connector."""
    fsm_states = get_fsm_states()
    if connector_id not in fsm_states:
        return None
    return fsm_states[connector_id]

def set_fsm_status(connector_id: str, status: str, step_info: Optional[OnboardingStepInfo] = None, pending_data: Optional[Dict[str, Any]] = None):
    """Set the FSM status for a connector."""
    # Ensure connector_id is a string
    connector_id_str = str(connector_id)
    
    # Get the FSM states dictionary
    fsm_states = get_fsm_states()
    
    # Create or update the FSM state
    fsm_states[connector_id_str] = {
        "status": status,
        "current_step_info": step_info.dict() if step_info else None,
        "pending_data": pending_data or {}
    }
    
    # Log the state for debugging
    logger.debug(f"Set FSM state for connector {connector_id_str}: {fsm_states[connector_id_str]}")

# Updated router with prefix to match test expectations
router = APIRouter(
    prefix="/api/onboard",
    tags=["Connector Onboarding"],
)

@router.post("/{connector_id}/initiate", response_model=OnboardingStepInfo)
async def initiate_onboarding_process(
    connector_id: str = Path(..., title="The ID of the connector to initiate onboarding for"),
    service: ConnectorService = Depends(get_connector_service)
):
    """
    Initiates or resumes the onboarding process for a specific connector.
    Returns the first or current step information.
    """
    try:
        logger.info(f"Initiating onboarding for connector: {connector_id}")
        step_info = await service.initiate_onboarding(UUID(connector_id))
        return step_info
    except Exception as e:
        logger.error(f"Error initiating onboarding for {connector_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to initiate onboarding: {str(e)}")

@router.get("/{connector_id}/status", response_model=OnboardingStepInfo)
async def get_onboarding_process_status(
    connector_id: str = Path(..., title="The ID of the connector to get onboarding status for"),
    service: ConnectorService = Depends(get_connector_service)
):
    """
    Retrieves the current status and step information of the onboarding process for a connector.
    """
    try:
        logger.info(f"Getting onboarding status for connector: {connector_id}")
        status = await service.get_onboarding_status(UUID(connector_id))
        if not status:
            raise HTTPException(status_code=404, detail="Onboarding not initiated for this connector. Call /initiate first.")
        return status
    except HTTPException: # Re-raise specific HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting onboarding status for {connector_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get onboarding status: {str(e)}")

@router.post("/{connector_id}/submit_step", response_model=StepSubmissionResult)
async def submit_onboarding_step_data(
    payload: StepSubmissionPayload,
    connector_id: str = Path(..., title="The ID of the connector to submit step data for"),
    service: ConnectorService = Depends(get_connector_service)
):
    """
    Submits data for the current step of the onboarding process.
    Returns the result of the submission and information for the next step, if any.
    """
    try:
        logger.info(f"Submitting onboarding step for connector: {connector_id}, step: {payload.step_id}")

        onboarding_result = await service.submit_onboarding_step(UUID(connector_id), payload)

        logger.info(f"FSM state updated for connector {connector_id}: AWAITING_CONNECTOR_PROCESSING")
        # Возвращаем успешный результат - фактический следующий шаг будет определен коннектором
        return onboarding_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting onboarding step for {connector_id}, step {payload.step_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to submit onboarding step: {str(e)}")