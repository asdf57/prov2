from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.resources import get_inventory_manager, get_commands_manager

router = APIRouter(prefix="/node", tags=["node"])

class NodeRequest(BaseModel):
    node: str

class ProvisionRequest(BaseModel):
    node: str
    wipe: bool = False

@router.post("/reboot/normal")
def post_entry(request: NodeRequest, inventory_manager=Depends(get_inventory_manager), commands_manager=Depends(get_commands_manager)):
    """
    Reboot a node
    """
    _ = inventory_manager.get_host(request.node)
    commands_manager.add_command(f"ansible-playbook -i inventory/inventory.yml ansible/plays/reboot.yml -l {request.node}")
    return {"info": f"Node {request.node} reboot initiated!"}

@router.post("/reboot/ipxe")
def post_entry(request: NodeRequest, inventory_manager=Depends(get_inventory_manager), commands_manager=Depends(get_commands_manager)):
    """
    Reboot a node into iPXE environment
    """
    _ = inventory_manager.get_host(request.node)
    commands_manager.add_command(f"ansible-playbook -i inventory/inventory.yml ansible/plays/reboot.yml -e reboot_to_ipxe=true -l {request.node}")
    return {"info": f"Node {request.node} reboot initiated!"}

@router.post("/reboot/hard")
def post_entry(request: NodeRequest, inventory_manager=Depends(get_inventory_manager), commands_manager=Depends(get_commands_manager)):
    """
    Reboot a node using sysrq
    """
    _ = inventory_manager.get_host(request.node)
    commands_manager.add_command(f"ansible-playbook -i inventory/inventory.yml ansible/plays/reboot.yml -e hard_reset=true -l {request.node}")
    return {"info": f"Node {request.node} reboot initiated!"}

@router.post("/provision")
def post_entry(request: ProvisionRequest, inventory_manager=Depends(get_inventory_manager), commands_manager=Depends(get_commands_manager)):
    """
    Provision a node
    """
    _ = inventory_manager.get_host(request.node)
    commands_manager.add_command(f"ansible-playbook -i inventory/inventory.yml ansible/plays/provision.yml -e should_wipe={request.wipe} -l {request.node}")
    return {"info": f"Node {request.node} provision initiated!"}
