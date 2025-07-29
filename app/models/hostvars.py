from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Annotated, Literal, Optional, List

from app.models.flag import DropletFlagModel, ServerFlagModel
from app.models.state import StateModel
from app.models.system import ServerSystemModel
from app.models.storage import StorageModel
from app.models.user import UserModel
from app.utils.droplet import DropletImage, DropletRegion, DropletSize

class HostvarsModel(BaseModel):
    """Base model for general host variables."""
    state: StateModel = Field(default_factory=StateModel)

class ServerHostvarsModel(HostvarsModel):
    system: ServerSystemModel
    storage: StorageModel
    flags: ServerFlagModel
    users: List[UserModel]

class DropletHostvarsModel(HostvarsModel):
    image: DropletImage
    region: DropletRegion
    size: DropletSize
    users: List[UserModel]

HOSTVARS_VALIDATOR = {
    "server": ServerHostvarsModel,
    "droplet": DropletHostvarsModel
}