from typing import Annotated, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.networks import IPvAnyAddress

from app.exceptions import InvalidTypeException

class InventoryEntry(BaseModel):
    """Base model for any Ansible inventory host entry."""
    type: str
    name: str = Field(description="Unique name/identifier for the host")
    ip: Optional[IPvAnyAddress] = Field(
        None, description="IP address of the host (optional for special connection types)"
    )
    groups: List[str] = Field(
        default_factory=list,
        description="Ansible inventory groups this host belongs to"
    )
    ansible_port: Optional[int] = Field(
        22, ge=1, le=65535,
        description="SSH port for connecting to this host"
    )
    ansible_user: Optional[str] = Field(
        "root", 
        description="Username for SSH connection"
    )
    hostvars: dict = Field(
        default_factory=dict,
        description="Additional Ansible host variables"
    )

    def get_hostvars(self) -> dict:
        d = {}
        if self.ip:
            d["ansible_host"] = self.ip.exploded
        if self.ansible_user:
            d["ansible_user"] = self.ansible_user
        if self.ansible_port:
            d["ansible_port"] = self.ansible_port
        if self.mac:
            d["mac"] = self.mac

        d.update(self.hostvars)

        # Must remove - a byproduct of using discriminated unions in Pydantic
        d.pop("type", None)
        return d
    
    def get_type(self) -> str:
        if "servers" in self.groups:
            return "server"
        elif "droplets" in self.groups:
            return "droplet"
        else:
            raise InvalidTypeException

    @staticmethod
    def get_type_from_group(groups) -> str:
        """Determine the type based on the groups."""
        found = None

        for group in groups:
            if str(group) == "servers":
                found = "server"
            elif str(group) == "droplets":
                found = "droplet"

        if not found:
            raise InvalidTypeException("Unrecognized group for inventory entry type.")

        return found

class ServerInventoryEntry(InventoryEntry):
    """Strict model for server entries that require direct IP connectivity."""
    type: Literal["server"]
    ip: IPvAnyAddress = Field(..., description="Required IP address for the server")
    mac: str = Field(
        ..., description="Primary MAC address of the server"
    )

    @field_validator("groups", mode="before")
    def ensure_servers_group(cls, v):
        """Ensure the server is part of the 'servers' group."""
        if not v:
            return ["servers"]
        if "servers" not in v:
            return ["servers"] + v
        return v

class DropletInventoryEntry(InventoryEntry):
    """Model for DigitalOcean Droplet entries."""
    type: Literal["droplet"]

    @model_validator(mode="after")
    def ensure_droplets_group(self) -> 'DropletInventoryEntry':
        if not self.groups:
            self.groups = ["droplets"]
        elif "droplets" not in self.groups:
            self.groups.append("droplets")
        return self

InventoryUnion = Annotated[
    Union[ServerInventoryEntry, DropletInventoryEntry],
    Field(discriminator="type")
]
