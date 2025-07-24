

from abc import ABC, abstractmethod
from typing import Type
from app.models.hostvars import DropletHostvarsModel, HostvarsModel, ServerHostvarsModel
from app.models.inventory import DropletInventoryEntry, InventoryEntry, ServerInventoryEntry

from ansible.inventory.host import Host

from app.utils.sanitize import sanitize_data


class HostTypeRegistryEntry(ABC):
    def __init__(self, inventory_model: Type[InventoryEntry], hostvars_model: Type[HostvarsModel]):
        self.inventory_model = inventory_model
        self.hostvars_model = hostvars_model

    @abstractmethod
    def get_inventory_entry(self, host: Host) -> InventoryEntry:
        ...

    @abstractmethod
    def get_hostvars_entry(self, data: dict) -> HostvarsModel:
        ...

    def get_default_hostvars(self) -> HostvarsModel:
        ...

class ServerRegistryEntry(HostTypeRegistryEntry):
    def __init__(self, inventory_model: Type[InventoryEntry], hostvars_model: Type[HostvarsModel]):
        super().__init__(inventory_model, hostvars_model)

    def get_inventory_entry(self, host: Host) -> InventoryEntry:
        vars = sanitize_data(host.vars)
        return self.inventory_model(
            type="server",
            name=host.name,
            ip=vars.get("ansible_host"),
            ansible_user=vars.get("ansible_user", "root"),
            ansible_port=vars.get("ansible_port", 22),
            groups=[g.name for g in host.groups],
            hostvars=vars
        )

    def get_hostvars_entry(self, data: dict) -> HostvarsModel:
        return self.hostvars_model.model_validate(data)

    def get_default_hostvars(self) -> HostvarsModel:
        return ServerHostvarsModel()


class DropletRegistryEntry(HostTypeRegistryEntry):
    def __init__(self, inventory_model: Type[InventoryEntry], hostvars_model: Type[HostvarsModel]):
        super().__init__(inventory_model, hostvars_model)


    def get_inventory_entry(self, host: Host) -> InventoryEntry:
        vars = sanitize_data(host.vars)
        return self.inventory_model(
            type="droplet",
            name=host.name,
            ip=vars.get("ansible_host"),
            ansible_user=vars.get("ansible_user", "root"),
            ansible_port=vars.get("ansible_port", 22),
            groups=[g.name for g in host.groups],
            hostvars=vars
        )

    def get_hostvars_entry(self, data: dict) -> HostvarsModel:
        return self.hostvars_model.model_validate(data)

    def get_default_hostvars(self) -> HostvarsModel:
        return DropletHostvarsModel()


HOST_TYPE_REGISTRY = {
    "server": ServerRegistryEntry(ServerInventoryEntry, ServerHostvarsModel),
    "droplet": DropletRegistryEntry(DropletInventoryEntry, DropletHostvarsModel),
}
