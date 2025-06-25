from pydantic import BaseModel
from typing import Literal, Annotated
from functools import partial

from app.utils.droplet import DropletImage, DropletRegion, DropletSize

class GeneralSystemModel(BaseModel):
    pass

class ServerSystemModel(GeneralSystemModel):
    os: Literal["arch", "debian"]
    mac: str
    node_type: Literal["coord", "infra", "worker"]

class DropletSystemModel(GeneralSystemModel):
    image: DropletImage
    region: DropletRegion
    size: DropletSize
