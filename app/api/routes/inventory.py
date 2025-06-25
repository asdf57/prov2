from fastapi import APIRouter, Depends
from app.models import *
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/")
def get_inventory(manager=Depends(get_inventory_manager)):
    """
    Get host variables.
    """
    return manager.get_inventory()

@router.delete("/")
def delete_inventory(inventory_manager=Depends(get_inventory_manager)):
    """
    Delete all servers from the inventory
    """
    inventory_manager.clear_inventory()
    inventory_manager.save()
    return {"message": "Inventory deleted"}

@router.delete("/all")
def delete_site(hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Delete everything
    """
    hostvars_manager.delete_all()
    inventory_manager.clear_inventory()
    inventory_manager.save()
    return {"message": "Site deleted"}