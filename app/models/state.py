

from typing import Literal
from pydantic import BaseModel

class StateModel(BaseModel):
    state: Literal[
        "initializing",
        "created",
        "provisioning",
        "provisioned",
    ] = "initializing"
