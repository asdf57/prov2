from typing import Union
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.system import SYSTEM_VALIDATOR, DropletSystemModel, ServerSystemModel
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/{host_name}")
def get_system(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get the system of a host.
    """
    inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)

    if "system" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No system data found for {host_name}"}
        )

    return hostvars["system"]

@router.post("/{host_name}")
def post_system(host_name: str, system: Union[ServerSystemModel, DropletSystemModel], hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Post the system
    """
    entry = inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)
    host_type = entry.get_type()

    if "system" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No system data found for {host_name}"}
        )
    
    system_data = system.model_dump()
    flags = SYSTEM_VALIDATOR[host_type].model_validate(system_data)
    hostvars["system"] = flags
    hostvars_manager.set_from_dict(entry, hostvars)
    return {"info": "System data updated successfully!"}
