from fastapi import APIRouter, Depends, Body
from app.resources import get_inventory_manager, get_commands_manager

router = APIRouter(prefix="/actions", tags=["actions"])


# POST /actions/{node_name}/command
@router.post("/command/{node_name}")
def post_command(
    node_name: str,
    user: str = "root",
    command: str = Body(..., media_type="text/plain"),
    inventory_manager=Depends(get_inventory_manager),
    commands_manager=Depends(get_commands_manager)
):
    """
    Execute a command on a node
    """
    _ = inventory_manager.get_host(node_name)
    commands_manager.add_node_command(node_name, command, user)
    return {"info": f"Command was scheduled on node {node_name}!"}

@router.post("/command/script")
async def post_script(
    script: str = Body(..., media_type="text/plain"),
    commands_manager=Depends(get_commands_manager)
):
    """
    Execute a bash script (accepts multi-line text/plain)
    """
    commands_manager.add_command(script)
    return {"info": "Script was scheduled!"}
