"""
API Router for FSM synchronization between Ingest API and Connectors.
These endpoints are intended to be called by the connectors themselves.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path

from mindbank_poc.core.connectors.service import ConnectorService, get_connector_service
from mindbank_poc.core.connectors.schemas_onboarding import (
    ConnectorDirective,
    ConnectorFSMUpdate,
    ConnectorDirectiveActionType,
    OnboardingStepInfo
)
from mindbank_poc.common.logging import get_logger
from mindbank_poc.api.routers.onboarding import get_fsm_states, get_fsm_state, set_fsm_status, step1, step2, completed_step, failed_step

logger = get_logger(__name__)

# Note: The prefix does not include /onboard as these are connector-facing for FSM state sync
router = APIRouter(
    prefix="/connectors/{connector_id}/fsm", # Changed prefix
    tags=["Connector FSM Sync"],
)

@router.get("/sync", response_model=ConnectorDirective)
async def connector_poll_for_fsm_directive(
    connector_id: str = Path(..., title="The ID of the connector polling for FSM directives"),
    service: ConnectorService = Depends(get_connector_service)
):
    """
    Called by the connector to poll for the next FSM directive from the Ingest API.
    """
    try:
        logger.debug(f"Connector {connector_id} polling for FSM directive.")
        state = await service.get_connector_fsm_directive(UUID(connector_id))

        return state
    except Exception as e:
        logger.error(f"Error providing FSM directive to connector {connector_id}: {e}", exc_info=True)
        # Do not expose detailed internal errors to the connector, generic message is safer.
        raise HTTPException(status_code=500, detail="Failed to retrieve FSM directive.")

@router.post("/sync_update", response_model=dict) # Simple dict response for now e.g. {"status": "received"}
async def connector_post_fsm_update(
    update_payload: ConnectorFSMUpdate,
    connector_id: str = Path(..., title="The ID of the connector sending an FSM update"),
    service: ConnectorService = Depends(get_connector_service)
):
    """
    Called by the connector to send an update to the Ingest API's FSM
    (e.g., result of processing a directive, new step definition).
    """
    try:
        logger.debug(f"Connector {connector_id} submitting FSM update for action: {update_payload.processed_action_type}")
        
        await service.process_connector_fsm_update(UUID(connector_id), update_payload)

        logger.debug(f"Set FSM state for connector {connector_id} to {update_payload.status}")
        return {"status": "update_received_and_processed"}
    except Exception as e:
        logger.error(f"Error processing FSM update from connector {connector_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process FSM update.")

@router.post("/notify_dynamic_config_update", response_model=dict)
async def connector_notify_dynamic_config_changed(
    connector_id: str = Path(..., title="The ID of the connector notifying about dynamic config changes"),
    # Optionally, connector could send some hints about what changed, but for now just a notification
    # notification_details: Optional[Dict[str, Any]] = Body(None),
    service: ConnectorService = Depends(get_connector_service)
):
    """
    Called by an operational connector to notify the Ingest API that its dynamic
    configuration options (e.g., list of available channels/folders) might have changed.
    The Ingest API will then use the regular /fsm/sync mechanism to request these details.
    """
    try:
        logger.info(f"Connector {connector_id} notified about potential dynamic config changes.")
        await service.mark_connector_for_dynamic_config_refresh(UUID(connector_id))
        return {"status": "notification_received"}
    except Exception as e:
        logger.error(f"Error handling dynamic config change notification from {connector_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process dynamic config change notification.")
