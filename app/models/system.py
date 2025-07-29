from pydantic import BaseModel
from typing import Literal

from app.utils.droplet import DropletImage, DropletRegion, DropletSize

class SystemModel(BaseModel):
    pass

class ServerSystemModel(SystemModel):
    os: Literal["arch", "debian"]
    node_type: Literal["coord", "infra", "worker"]

class DropletSystemModel(SystemModel):
    image: DropletImage
    region: DropletRegion
    size: DropletSize

SYSTEM_VALIDATOR = {
    "server": ServerSystemModel,
    "droplet": DropletSystemModel,
}