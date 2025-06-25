from fastapi import APIRouter, Depends
from app.models import *
from app.models.hostvars import HostvarsModel
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/hostvars", tags=["hostvars"])

@router.get("/{host_name}")
def get_hostvars(host_name: str, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Get host variables.
    """
    if not inventory_manager.get_host(host_name):
        return {"error": f"Host {host_name} not found in the inventory."}

    return hostvars_manager.get(host_name)

@router.post("/{host_name}")
def post_hostvars(host_name: str, hostvars: HostvarsModel, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Save the host variables to the repository.
    """
    entry = inventory_manager.get_host(host_name)
    hostvars_manager.set(entry, hostvars)
    return {"message": "Host variables updated successfully!"}
