import time
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.resources import get_inventory_manager, get_commands_manager, get_kauf_manager_factory

router = APIRouter(prefix="/power", tags=["power"])

class PowerRequest(BaseModel):
    node: str

@router.post("/on")
def post_entry(request: PowerRequest, inventory_manager=Depends(get_inventory_manager), kauf_factory=Depends(get_kauf_manager_factory)):
    """
    Reboot a node
    """
    _ = inventory_manager.get_host(request.node)
    kauf_manager = kauf_factory(request.node)
    kauf_manager.turn_on()
    return {"info": f"Node {request.node} reboot initiated!"}

@router.post("/off")
def post_entry(request: PowerRequest, inventory_manager=Depends(get_inventory_manager), kauf_factory=Depends(get_kauf_manager_factory)):
    """
    Reboot a node
    """
    _ = inventory_manager.get_host(request.node)
    kauf_manager = kauf_factory(request.node)
    kauf_manager.turn_off()
    return {"info": f"Node {request.node} reboot initiated!"}

@router.post("/cycle")
def post_entry(request: PowerRequest, inventory_manager=Depends(get_inventory_manager), kauf_factory=Depends(get_kauf_manager_factory)):
    """
    Reboot a node
    """
    _ = inventory_manager.get_host(request.node)
    kauf_manager = kauf_factory(request.node)
    kauf_manager.turn_off()
    time.sleep(5)
    kauf_manager.turn_on()
    return {"info": f"Node {request.node} reboot initiated!"}
