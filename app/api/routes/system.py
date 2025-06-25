from fastapi import APIRouter


route = APIRouter(prefix="/storage", tags=["storage"])

@route.post("/storage/{host}")
async def post_storage(host: str, payload: StorageModel):
    return await update_hostvars(host, payload.model_dump(), HostvarType.STORAGE, ReplacementType.OVERRIDE)

@route.put("/storage/{host}")
async def put_storage(host: str, payload: PartialStorageModel):
    return await update_hostvars(host, payload.model_dump(exclude_none=True), HostvarType.STORAGE, ReplacementType.IN_PLACE)

@route.get("/storage/{host}")
async def get_storage(host: str):
    storage_data = hostvars_manager.get_section_by_host(host, HostvarType.STORAGE)
    return JSONResponse(content={"status": "success", "data": storage_data}, status_code=200)

@route.get("/storage")
async def get_storage():
    storage_data = hostvars_manager.get_all_by_section(HostvarType.STORAGE)
    return JSONResponse(content={"status": "success", "data": storage_data}, status_code=200)
