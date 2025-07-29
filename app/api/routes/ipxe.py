import logging
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from app.exceptions import HostNotFoundException, HostvarsNotFoundException
from app.resources import get_inventory_manager, get_hostvars_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ipxe", tags=["ipxe"])

@router.get("/{mac}")
async def get_ipxe_script(mac: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Returns a plaintext response of the os for iPXE booting
    Manually handle exceptions to avoid the generic JSON exception system
    """
    try:
        host = inventory_manager.get_host_by_mac(mac)
        hostvars = hostvars_manager.get(host.name)
        if host.get_type() != "server":
            return PlainTextResponse(content="Only the 'server' type is supported for this operation!", status_code=400)
    except HostNotFoundException:
        return PlainTextResponse(content="Host not found", status_code=404)
    except HostvarsNotFoundException:
        return PlainTextResponse(content="Hostvars not found", status_code=404)
    except Exception as e:
        logger.error(f"Received an error in iPXE route: {e}")
        return PlainTextResponse(content="Generic exception occurred!", status_code=404)

    return PlainTextResponse(content=str(hostvars['system']['os']), status_code=200)
