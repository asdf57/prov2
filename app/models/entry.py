from pydantic import BaseModel, Field, IPvAnyAddress
from typing import List, Literal, Optional
from abc import ABC, abstractmethod

from app.models.hostvars import DropletHostvarsModel, ServerHostvarsModel
from app.models.inventory import DropletInventoryEntry, ServerInventoryEntry
from app.models.system import ServerSystemModel
from app.models.storage import StorageModel
from app.utils.droplet import DropletImage, DropletRegion, DropletSize

class EntryModel(BaseModel):
    """Base model for general host variables."""
    type: str

class ServerEntryModel(EntryModel):
    type: Literal["server"] = "server"
    name: str = Field(description="Unique name/identifier for the host")
    ip: IPvAnyAddress = Field(
        None, description="IP address of the host"
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
    system: ServerSystemModel
    storage: StorageModel

class DropletEntryModel(EntryModel):
    type: Literal["droplet"] = "droplet"
    image: DropletImage
    region: DropletRegion
    size: DropletSize

class EntryBuilder(ABC):
    def __init__(self, entry: EntryModel):
        """Initialize the entry builder."""
        self.entry = entry

    @abstractmethod
    def build_inventory(self):
        """Build the inventory entry from a given model."""
        pass

    @abstractmethod
    def build_server_hostvars(self):
        """Build the hostvars entry for a server."""
        pass

class ServerEntryBuilder(EntryBuilder):
    def __init__(self, entry: ServerEntryModel):
        """Initialize the server entry builder."""
        super().__init__(entry)

    def build_inventory(self) -> ServerInventoryEntry:
        """Build the inventory entry from a server model."""
        return ServerInventoryEntry(
            name=self.entry.name,
            ip=self.entry.ip,
            groups=["servers"] + self.entry.groups,
            ansible_port=self.entry.ansible_port,
            ansible_user=self.entry.ansible_user,
            hostvars=self.entry.hostvars,
        )

    def build_server_hostvars(self) -> ServerHostvarsModel:
        """Build the hostvars entry for a server."""
        return ServerHostvarsModel(
            state="initializing",
            system=self.entry.system,
            storage=self.entry.storage
        )

class DropletEntryBuilder(EntryBuilder):
    def __init__(self, entry: DropletEntryModel):
        """Initialize the droplet entry builder."""
        super().__init__(entry)

    def build_inventory(self) -> DropletInventoryEntry:
        """Build the inventory entry from a droplet model."""
        return DropletInventoryEntry(
            name=self.entry.name,
            groups=["droplets"] + self.entry.groups,
            ansible_port=self.entry.ansible_port,
            ansible_user=self.entry.ansible_user,
            hostvars=self.entry.hostvars,
        )

    def build_server_hostvars(self) -> DropletHostvarsModel:
        """Build the hostvars entry for a droplet."""
        return DropletHostvarsModel(
            state="initializing",
            image=self.entry.image,
            region=self.entry.region,
            size=self.entry.size,
        )

BUILDER_BY_TYPE = {
    "server": ServerEntryBuilder,
    "droplet": DropletEntryBuilder,
}