import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api.main import api_router
from app.exceptions import GitException, HostNotFoundException, InventoryException

app = FastAPI(
    title="Infrastructure Management API",
    description="API for managing infrastructure resources",
    version="1.0.0",
)

app.include_router(api_router)


@app.exception_handler(InventoryException)
async def inventory_exception_handler(request, exc: InventoryException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc)}
    )

@app.exception_handler(GitException)
async def git_exception_handler(request, exc: GitException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc)}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": f"An unexpected error occurred: {exc}"}
    )
