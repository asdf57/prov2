from typing import Union
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.flag import FLAGS_VALIDATOR, ServerFlagModel
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/flags", tags=["flags"])

@router.get("/{host_name}")
def get_flags(host_name: str, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Get flags
    """
    inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)

    if "flags" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No flags found for {host_name}"}
        )

    return hostvars["flags"]

@router.post("/{host_name}")
def post_flags(
    host_name: str,
    flags: Union[ServerFlagModel],
    hostvars_manager=Depends(get_hostvars_manager),
    inventory_manager=Depends(get_inventory_manager)
):
    """
    Post the flags
    """
    entry = inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)
    host_type = entry.get_type()

    if "flags" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No flags found for {host_name}"}
        )
    
    flags_data = flags.model_dump()
    flags = FLAGS_VALIDATOR[host_type].model_validate(flags_data)
    hostvars["flags"] = flags
    hostvars_manager.set_from_dict(entry, hostvars)
    return {"info": "Flags updated successfully!"}
