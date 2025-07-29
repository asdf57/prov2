from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.state import STATE_VALIDATOR, StateModel
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/state", tags=["state"])

@router.get("/{host_name}")
def get_state(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get the state of a host.
    """
    inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)

    if "state" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No flags found for {host_name}"}
        )

    return hostvars["state"]

@router.post("/{host_name}")
def post_state(host_name: str, state: StateModel, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Post the state
    """
    entry = inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)
    host_type = entry.get_type()

    if "state" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No state found for {host_name}"}
        )
    
    state_data = state.model_dump()
    flags = STATE_VALIDATOR[host_type].model_validate(state_data)
    hostvars["state"] = flags
    hostvars_manager.set_from_dict(entry, hostvars)
    return {"info": "State updated successfully!"}
