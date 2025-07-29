from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Annotated, List, Literal, Optional, Union
from abc import ABC, abstractmethod

from app.models.flag import ServerFlagModel
from app.models.hostvars import DropletHostvarsModel, ServerHostvarsModel
from app.models.inventory import DropletInventoryEntry, ServerInventoryEntry
from app.models.state import StateModel
from app.models.system import ServerSystemModel
from app.models.user import UserModel
from app.models.storage import StorageModel
from app.utils.droplet import DropletImage, DropletRegion, DropletSize

class EntryModel(BaseModel):
    """Base model for general host variables."""
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

class ServerEntryModel(EntryModel):
    type: Literal["server"] = "server"
    ip: IPvAnyAddress = Field(
        None, description="IP address of the host"
    )
    mac: str = Field(
        ..., description="Primary MAC address of the server"
    )
    system: ServerSystemModel
    storage: StorageModel
    flags: ServerFlagModel
    users: List[UserModel]

class DropletEntryModel(EntryModel):
    type: Literal["droplet"] = "droplet"
    image: DropletImage
    region: DropletRegion
    size: DropletSize
    users: List[UserModel]

class EntryBuilder(ABC):
    def __init__(self, entry: EntryModel):
        """Initialize the entry builder."""
        self.entry = entry

    @abstractmethod
    def build_inventory(self):
        """Build the inventory entry from a given model."""
        pass

    @abstractmethod
    def build_hostvars(self):
        """Build the hostvars entry for a server."""
        pass

class ServerEntryBuilder(EntryBuilder):
    def __init__(self, entry: ServerEntryModel):
        """Initialize the server entry builder."""
        super().__init__(entry)

    def build_inventory(self) -> ServerInventoryEntry:
        """Build the inventory entry from a server model."""
        return ServerInventoryEntry(
            type="server",
            name=self.entry.name,
            ip=self.entry.ip,
            mac=self.entry.mac,
            groups=["servers"] + self.entry.groups,
            ansible_port=self.entry.ansible_port,
            ansible_user=self.entry.ansible_user,
            hostvars=self.entry.hostvars,
        )

    def build_hostvars(self) -> ServerHostvarsModel:
        """Build the hostvars entry for a server."""
        return ServerHostvarsModel(
            state=StateModel(
                status="initializing",
            ),
            system=self.entry.system,
            storage=self.entry.storage,
            flags=self.entry.flags,
            users=self.entry.users,
        )

class DropletEntryBuilder(EntryBuilder):
    def __init__(self, entry: DropletEntryModel):
        """Initialize the droplet entry builder."""
        super().__init__(entry)

    def build_inventory(self) -> DropletInventoryEntry:
        """Build the inventory entry from a droplet model."""
        return DropletInventoryEntry(
            type="droplet",
            name=self.entry.name,
            ip=None,
            groups=["droplets"] + self.entry.groups,
            ansible_port=self.entry.ansible_port,
            ansible_user=self.entry.ansible_user,
            hostvars=self.entry.hostvars,
            image=self.entry.image,
            region=self.entry.region,
            size=self.entry.size,
        )

    def build_hostvars(self) -> DropletHostvarsModel:
        """Build the hostvars entry for a droplet."""
        return DropletHostvarsModel(
            state=StateModel(
                status="initializing",
            ),
            image=self.entry.image,
            region=self.entry.region,
            size=self.entry.size,
            users=self.entry.users,
        )

BUILDER_BY_TYPE = {
    "server": ServerEntryBuilder,
    "droplet": DropletEntryBuilder,
}

EntryUnion = Annotated[
    Union[ServerEntryModel, DropletEntryModel],
    Field(discriminator="type")
]
