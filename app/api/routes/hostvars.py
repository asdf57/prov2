from typing import Union
from fastapi import APIRouter, Depends, Body
from app.models import *
from app.models.hostvars import HOSTVARS_VALIDATOR, ServerHostvarsModel, DropletHostvarsModel
from app.resources import get_hostvars_manager, get_inventory_manager
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/hostvars", tags=["hostvars"])

@router.get("/{host_name}")
def get_hostvars(host_name: str, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Get host variables.
    """
    inventory_manager.get_host(host_name)
    return hostvars_manager.get(host_name)

@router.post("/{host_name}")
def post_hostvars(
    host_name: str,
    hostvars: Union[ServerHostvarsModel, DropletHostvarsModel],
    hostvars_manager=Depends(get_hostvars_manager),
    inventory_manager=Depends(get_inventory_manager)
):
    """
    Save the host variables to the repository.
    """
    entry = inventory_manager.get_host(host_name)
    hostvars_data = hostvars.model_dump()
    host_type = entry.get_type()
    hostvars = HOSTVARS_VALIDATOR[host_type].model_validate(hostvars_data)
    hostvars_manager.set(entry, hostvars)
    return {"info": "Host variables updated successfully!"}
