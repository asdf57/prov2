
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from app.resources import get_inventory_manager, get_hostvars_manager

router = APIRouter(prefix="/ipxe", tags=["ipxe"])

@router.get("/{mac}")
async def get_ipxe_script(mac: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Returns a plaintext response of the os to iPXE boot to
    """
    host = inventory_manager.get_host_by_mac(mac)
    if not host:
        return PlainTextResponse(content="Host not found", status_code=404)

    hostvars = hostvars_manager.get(host.name)
    if not hostvars:
        return PlainTextResponse(content="Hostvars not found", status_code=404)

    if hostvars['type'] != "server":
        return PlainTextResponse(content="Only the 'server' type is supported for this operation!", status_code=400)

    return PlainTextResponse(content=str(hostvars['system']['os']), status_code=200)
