from fastapi import APIRouter

from app.api.routes import (
    entry,
    hostvars,
    flags,
    inventory,
    state,
    storage,
    system,
    ipxe,
    user
)

api_router = APIRouter()
api_router.include_router(hostvars.router)
api_router.include_router(flags.router)
api_router.include_router(inventory.router)
api_router.include_router(state.router)
api_router.include_router(entry.router)
api_router.include_router(storage.router)
api_router.include_router(system.router)
api_router.include_router(ipxe.router)
api_router.include_router(user.router)
