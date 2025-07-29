"""
Pydantic models for connector onboarding process.
"""
from uuid import UUID
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

class ConnectorOnboardingState(BaseModel):
    """
    Represents the state of a connector's onboarding process.
    """
    connector_id: UUID
    current_step_id: Optional[str] = None
    onboarding_context: Dict[str, Any] = Field(default_factory=dict)
    last_error_message: Optional[str] = None
    is_completed: bool = False
    is_failed: bool = False # Indicates if the onboarding failed definitively

class OnboardingStepInfo(BaseModel):
    """
    Provides information about a specific onboarding step.
    This is typically returned by the connector (or an adapter)
    to inform the Ingest API about what data is needed.
    """
    step_id: str
    description: Optional[str] = None
    # JSON Schema describing the data expected for this step
    input_schema: Optional[Dict[str, Any]] = None
    # Optional: UI schema or hints for rendering the input_schema
    ui_schema: Optional[Dict[str, Any]] = None
    messages: List[str] = Field(default_factory=list)
    # Indicates if this step is the final one after successful completion
    is_final_step: bool = False

class StepSubmissionPayload(BaseModel):
    """
    Data submitted by the user for a specific onboarding step.
    """
    step_id: str
    data: Dict[str, Any]

class StepSubmissionResult(BaseModel):
    """
    Result of submitting data for an onboarding step.
    This is typically returned by the Ingest API to the client.
    """
    success: bool
    # Information about the next step, if any
    next_step_info: Optional[OnboardingStepInfo] = None
    is_onboarding_complete: bool = False
    error_message: Optional[str] = None
    messages: List[str] = Field(default_factory=list)

# --- Models for Ingest API <-> Connector FSM Synchronization ---

class ConnectorDirectiveActionType(str, Enum):
    """Defines the types of actions the Ingest API can request from a connector during FSM sync."""
    PROVIDE_STEP_DEFINITION = "PROVIDE_STEP_DEFINITION"
    PROCESS_STEP_DATA = "PROCESS_STEP_DATA"
    PROVIDE_DYNAMIC_CONFIG_OPTIONS = "PROVIDE_DYNAMIC_CONFIG_OPTIONS" # For post-onboarding updates
    AWAIT_ONBOARDING_START = "AWAIT_ONBOARDING_START" # Явное ожидание старта онбординга
    AWAIT_USER_INPUT = "AWAIT_USER_INPUT" # Connector should wait for user input
    NONE = "NONE" # No action needed

class ConnectorDirective(BaseModel):
    """
    Directive sent from Ingest API to Connector via the sync polling mechanism.
    Tells the connector what the Ingest API's FSM currently needs.
    """
    action_type: ConnectorDirectiveActionType
    # Context for the action, e.g., for which step_id to provide definition or process data
    action_context_step_id: Optional[str] = None 
    data_for_connector_processing: Optional[Dict[str, Any]] = None
    # Relevant parts of Ingest API's FSM context that might be useful for the connector
    current_fsm_context_snapshot: Optional[Dict[str, Any]] = None 

class ConnectorFSMUpdateStatus(str, Enum):
    """Status of the connector's processing of a directive."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

class ConnectorFSMUpdate(BaseModel):
    """
    Update sent from Connector to Ingest API after processing a directive.
    Contains results, new step definitions, or errors.
    """
    processed_action_type: ConnectorDirectiveActionType
    processed_action_context_step_id: Optional[str] = None # The step_id this update pertains to
    status: ConnectorFSMUpdateStatus
    error_message: Optional[str] = None
    
    # If PROVIDE_STEP_DEFINITION was processed successfully
    step_definition_provided: Optional[OnboardingStepInfo] = None 
    
    # If PROCESS_STEP_DATA was processed successfully, this is data to merge into Ingest API's FSM context
    processing_result_data_to_update_context: Optional[Dict[str, Any]] = None 
    
    # If PROVIDE_DYNAMIC_CONFIG_OPTIONS was processed (post-onboarding)
    dynamic_config_options_provided: Optional[Dict[str, Any]] = None 
    # Optional: If the connector wants to suggest a full new config_schema after dynamic update
    new_full_config_schema_provided: Optional[Dict[str, Any]] = None
