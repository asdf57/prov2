from fastapi import APIRouter, Depends
from app.models.inventory import InventoryUnion
from app.models.state import StateModel
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/state", tags=["state"])

@router.get("/{host_name}")
def get_state(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get the state of a host.
    """
    if not inventory_manager.get_host(host_name):
        return {"error": f"Host {host_name} not found in the inventory."}

    return hostvars_manager.get(host_name)['state']

@router.post("/{host_name}")
def post_state(host_name: str, state: StateModel, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Update the state of a host.
    """
    entry = inventory_manager.get_host(host_name)
    if not entry:
        return {"error": f"Host {host_name} not found in the inventory."}

    # Update the state in hostvars
    hostvars = hostvars_manager.get(host_name)
    hostvars['state'] = state

    # Save the updated hostvars
    hostvars_manager.set(entry, hostvars)

    return {"message": "State updated successfully!"}