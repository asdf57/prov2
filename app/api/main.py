from fastapi import APIRouter

from app.api.routes import (
    hostvars,
    servers,
    inventory,
    state,
    storage,
    system,
    ipxe,
)

api_router = APIRouter()
api_router.include_router(hostvars.router)
api_router.include_router(inventory.router)
api_router.include_router(state.router)
api_router.include_router(servers.router)
# api_router.include_router(storage.router)
# api_router.include_router(system.router)
api_router.include_router(ipxe.router)
