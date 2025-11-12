from fastapi import APIRouter, Depends, Body
from app.resources import get_inventory_manager, get_commands_manager

router = APIRouter(prefix="/actions", tags=["actions"])


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
