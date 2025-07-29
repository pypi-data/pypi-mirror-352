"""
Pydantic schemas for FSM-based Onboarding and Connector Synchronization.
Simplified for PoC.
"""
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# --- Schemas for UI/Hub facing API (/onboard) ---

class OnboardingStepInfo(BaseModel):
    """Information about the current or next onboarding step for the UI."""
    step_id: str = Field(..., description="Identifier for the current step.", examples=["initial_auth", "select_folders"])
    description: Optional[str] = Field(None, description="Description of the step for the user.")
    input_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for data required from the user, or null if no input needed.")
    # ui_schema: Optional[Dict[str, Any]] = Field(None, description="Optional JSON Schema for UI hints.") # Simplified for PoC
    messages: List[str] = Field(default_factory=list, description="Messages for the user.")
    is_final_step: bool = Field(False, description="Indicates if this is the final step (completion or failure).")

class StepSubmissionPayload(BaseModel):
    """Payload sent by the UI to submit data for a step."""
    step_id: str = Field(..., description="Identifier of the step being submitted.")
    data: Optional[Dict[str, Any]] = Field(None, description="User-provided data corresponding to input_schema.")

class StepSubmissionResult(BaseModel):
    """Result returned after submitting step data."""
    success: bool
    next_step_info: Optional[OnboardingStepInfo] = Field(None, description="Info for the next step if successful, null otherwise or if onboarding complete.")
    is_onboarding_complete: bool = Field(False, description="True if this step was the final successful step.")
    error_message: Optional[str] = Field(None, description="Error message if success is false.")
    messages: List[str] = Field(default_factory=list, description="Additional messages.")

# --- Schemas for Connector facing API (/fsm) ---

class ConnectorDirectiveActionType(str, Enum):
    """Action requested from the connector."""
    PROVIDE_STEP_DEFINITION = "PROVIDE_STEP_DEFINITION"
    PROCESS_STEP_DATA = "PROCESS_STEP_DATA"
    # PROVIDE_DYNAMIC_CONFIG_OPTIONS = "PROVIDE_DYNAMIC_CONFIG_OPTIONS" # Simplified for PoC
    NONE = "NONE" # No action needed currently

class ConnectorDirective(BaseModel):
    """Directive sent from Core API to the connector via /fsm/sync."""
    action_type: ConnectorDirectiveActionType
    action_context_step_id: Optional[str] = Field(None, description="Context for the action, e.g., the step_id to define or process.")
    data_for_connector_processing: Optional[Dict[str, Any]] = Field(None, description="Data submitted by the user for the connector to process.")
    # current_fsm_context_snapshot: Optional[Dict[str, Any]] = Field(None) # Simplified for PoC

class ConnectorFSMUpdateStatus(str, Enum):
    """Status of the connector's update."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class ConnectorFSMUpdate(BaseModel):
    """Update sent from the connector to Core API via /fsm/sync_update."""
    processed_action_type: ConnectorDirectiveActionType
    processed_action_context_step_id: Optional[str]
    status: ConnectorFSMUpdateStatus
    error_message: Optional[str] = Field(None)
    # For PROVIDE_STEP_DEFINITION action:
    step_definition_provided: Optional[OnboardingStepInfo] = Field(None, description="The definition of the step provided by the connector.")
    # For PROCESS_STEP_DATA action:
    # processing_result_data_to_update_context: Optional[Dict[str, Any]] = Field(None) # Simplified for PoC
    # dynamic_config_options_provided: Optional[Dict[str, Any]] = Field(None) # Simplified for PoC
    # new_full_config_schema_provided: Optional[Dict[str, Any]] = Field(None) # Simplified for PoC
