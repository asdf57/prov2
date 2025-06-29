from git import Union
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Annotated, Literal, Optional

from app.models.state import StateModel
from app.models.system import ServerSystemModel
from app.models.storage import StorageModel
from app.utils.droplet import DropletImage, DropletRegion, DropletSize

class HostvarsModel(BaseModel):
    """Base model for general host variables."""
    state: StateModel = Field(default_factory=StateModel)

class ServerHostvarsModel(HostvarsModel):
    # type: Literal["server"] = "server"
    system: ServerSystemModel
    storage: StorageModel

class DropletHostvarsModel(HostvarsModel):
    # type: Literal["droplet"] = "droplet"
    image: DropletImage
    region: DropletRegion
    size: DropletSize
