from typing import Union, List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.user import USER_VALIDATOR, UserModel
from app.resources import get_hostvars_manager, get_inventory_manager

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/{host_name}")
def get_user(host_name: str, inventory_manager=Depends(get_inventory_manager), hostvars_manager=Depends(get_hostvars_manager)):
    """
    Get the users of a host.
    """
    inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)

    if "users" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No user data found for {host_name}"}
        )

    return hostvars["user"]

@router.post("/{host_name}")
def post_user(host_name: str, users: List[UserModel], hostvars_manager=Depends(get_hostvars_manager), inventory_manager=Depends(get_inventory_manager)):
    """
    Post the user data
    """
    entry = inventory_manager.get_host(host_name)
    hostvars = hostvars_manager.get(host_name)
    host_type = entry.get_type()

    if "users" not in hostvars:
        return JSONResponse(
            status_code=200,
            content={"info": f"No user data found for {host_name}"}
        )

    # Technically this isn't needed for UserModel since all types use the SAME model,
    # but we keep it for consistency with other routes.
    for user in users:
        user_data = user.model_dump()
        user_model = USER_VALIDATOR[host_type].model_validate(user_data)

    hostvars["users"] = users
    hostvars_manager.set_from_dict(entry, hostvars)
    return {"info": "User data updated successfully!"}
