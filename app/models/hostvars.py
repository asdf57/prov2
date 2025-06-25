from git import Union
from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Annotated, Literal, Optional

from app.models.state import StateModel

class HostvarsModel(BaseModel):
    """Base model for general host variables."""
    state: StateModel = Field(default_factory=StateModel)

class ServerHostvarsModel(HostvarsModel):
    type: Literal["server"] = "server"
    pass
    # system: SystemModel
    # storage: StorageModel

class DropletHostvarsModel(HostvarsModel):
    type: Literal["droplet"] = "droplet"
    pass
