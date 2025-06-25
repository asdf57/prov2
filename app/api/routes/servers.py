from fastapi import APIRouter, Depends
from app.models.inventory import InventoryUnion
from app.resources import get_hostvars_manager, get_inventory_manager
from app.utils.inventory_manager import InventoryManager

router = APIRouter(prefix="/servers", tags=["servers"])

@router.get("/{host_name}")
def get_server(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get host variables.
    """
    host = inventory_manager.get_host(host_name)
    host = host.model_dump()
    hostvars = hostvars_manager.get(host_name)
    host['hostvars'].update(**hostvars)
    return host

@router.post("/")
def post_server(entry: InventoryUnion, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Save the inventory to the repository.
    """
    inventory_manager.add_host(entry)

    # Init the hostvars
    hostvars_manager.init(entry)

    return {"message": "Server created successfully!"}

@router.delete("/")
def delete_server(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Delete all servers from the inventory
    """
    inventory_manager.remove_host(host_name)
    hostvars_manager.delete(host_name)
    return {"message": "Server deleted successfully!"}
