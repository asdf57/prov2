from typing import Union
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.storage import STORAGE_VALIDATOR, StorageModel
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/storage", tags=["storage"])

@router.get("/{host_name}")
def get_storage(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get the storage of a host.
    """
    inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)

    if "storage" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No storage found for {host_name}"}
        )

    return hostvars["storage"]

@router.post("/{host_name}")
def post_storage(host_name: str, storage: Union[StorageModel], hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Post the storage
    """
    entry = inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)
    host_type = entry.get_type()

    if "storage" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No storage found for {host_name}"}
        )
    
    storage_data = storage.model_dump()
    flags = STORAGE_VALIDATOR[host_type].model_validate(storage_data)
    hostvars["storage"] = flags
    hostvars_manager.set_from_dict(entry, hostvars)
    return {"info": "Storage updated successfully!"}
