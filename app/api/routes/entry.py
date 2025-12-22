from fastapi import APIRouter, Depends
from app.exceptions import InvalidTypeException
from app.models.entry import BUILDER_BY_TYPE, EntryUnion
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/entry", tags=["entry"])

@router.get("/{host_name}")
def get_entry(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get an entry
    """
    host = inventory_manager.get_host(host_name)
    host = host.model_dump()
    hostvars = hostvars_manager.get(host_name)
    host['hostvars'].update(**hostvars)
    return host

@router.get("/")
def get_entry(inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get all entries
    """
    return inventory_manager.get_all_hosts()

@router.post("/")
def post_entry(entry: EntryUnion, hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Create an entry
    """
    if not BUILDER_BY_TYPE.get(entry.type):
        raise InvalidTypeException

    creator = BUILDER_BY_TYPE[entry.type](entry)
    inventory = creator.build_inventory()
    hostvars = creator.build_hostvars()
    inventory_manager.add_host(inventory)
    hostvars_manager.init(entry.name, hostvars)
    return {"info": f"{entry.name} of type {entry.type} was created successfully!"}

@router.delete("/{host_name}")
def delete_entry(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Delete an entry
    """
    inventory_manager.remove_host(host_name)
    hostvars_manager.delete(host_name)
    return {"info": "Entry deleted successfully!"}
