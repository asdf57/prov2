import logging
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from pathlib import Path

from app.exceptions import HostAlreadyExistsException, HostNotFoundException, InvalidGroupException, NoGroupsException
from app.models.entities import HOST_TYPE_REGISTRY
from app.models.inventory import DropletInventoryEntry, InventoryEntry, ServerInventoryEntry
from app.utils.sanitize import sanitize_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Inventory():
    def __init__(self, inventory_path: Path):
        self.data_loader = DataLoader()
        self.inventory_path = inventory_path
        self.inventory = InventoryManager(loader=self.data_loader, sources=str(self.inventory_path))

    def get_host(self, host_name: str) -> InventoryEntry:
        self.inventory.refresh_inventory()

        host = self.inventory.get_host(host_name)
        if not host:
            raise HostNotFoundException(f"Host {host_name} not found")

        host_type = host.vars.get('type', None)

        entry_cls = HOST_TYPE_REGISTRY.get(host_type)
        if not entry_cls:
            raise ValueError(f"Unrecognized host type: {host_type}")

        return entry_cls.get_inventory_entry(host)

    def get_host_by_mac(self, mac: str) -> InventoryEntry | None:
        """
        Get a host entry from the inventory by its MAC address.
        """
        self.inventory.refresh_inventory()
        for host in self.inventory.get_hosts():
            if host.vars.get("primary_mac", None) == mac:
                return host

        return None

    def get_all_hosts(self) -> list[InventoryEntry]:
        """
        Get all hosts in the inventory.
        """
        self.inventory.refresh_inventory()
        hosts = self.inventory.get_hosts()

        if not hosts:
            logger.warning("No hosts found in the inventory.")
            return []

        all_hosts = []
        for host in hosts:
            all_hosts.append(self.get_host(host.name))

        return all_hosts

    def add_host(self, host: InventoryEntry) -> None:
        self.inventory.refresh_inventory()
        self.inventory.add_group("all")

        logger.info(f"Adding host {host.name} to the inventory...")

        if any(host.name == h.name for h in self.inventory.get_hosts()):
            raise HostAlreadyExistsException(f"Host {host.name} already exists in the inventory.")

        self.inventory.add_host(host.name, group="all", port=host.ansible_port)
        entry = self.inventory.get_host(host.name)

        for key, value in entry.get_hostvars().items():
            if value is not None:
                entry.set_variable(key, value)

        logger.info(f"Groups for host {host.name}: {host.groups}")

        for group in host.groups:
            logger.info(f"Adding host {host.name} to group {group}...")
            if group in ["all", "ungrouped", ""]:
                continue

            self.inventory.add_group(group)
            self.inventory.add_host(host.name, group=group)


        logger.info(f"Host {host.name} added to the inventory")

    def remove_host(self, host_name: str) -> None:
        self.inventory.refresh_inventory()

        host = self.inventory.get_host(host_name)
        if not host:
            logger.warning(f"Host {host_name} not found in the inventory.")
            raise HostNotFoundException(f"Host {host_name} not found in the inventory.")

        logger.info(f"Removing {host_name} from the inventory")
        self.inventory._inventory.remove_host(host)

        groups_list = list(self.inventory.groups)
        for group in groups_list:
            if group not in ["all", "ungrouped"] and not self.inventory.get_groups_dict()[group]:
                logger.info(f"Found empty group {group} after removing host. Removing the group as well.")
                self.inventory._inventory.remove_group(group)

    def clear_inventory(self) -> None:
        logger.info("Clearing the inventory...")
        self.inventory.refresh_inventory()

        for host in self.inventory.get_hosts():
            logger.info(f"Removing host {host.name} from the inventory")
            self.inventory._inventory.remove_host(host)

        groups = self.inventory.get_groups_dict()

        for group in groups:
            if group not in ["all", "ungrouped"]:
                logger.info(f"Removing group {group} from the inventory")
                self.inventory._inventory.remove_group(group)

    def to_dict(self, refresh_from_disk: bool = False) -> dict:
        # Only call self.inventory.refresh_inventory() when you want to refresh
        # the in-memory representation with what's on disk.
        if refresh_from_disk:
            self.inventory.refresh_inventory()

        inventory_dict = {"all": {"hosts": {}, "children": {}}}
        groups_dict = self.inventory.get_groups_dict()

        for host in groups_dict.get("all", []):
            entry = self.inventory.get_host(host)
            if not host:
                continue

            hostvars = entry.vars.copy()
            hostvars.pop("inventory_file", None)
            hostvars.pop("inventory_dir", None)
            inventory_dict["all"]["hosts"][str(host)] = hostvars

        for group, hosts in groups_dict.items():
            if group in ["all", "ungrouped"]:
                continue

            inventory_dict["all"]["children"][str(group)] = {"hosts": {}}
            for host in hosts:
                inventory_dict["all"]["children"][str(group)]["hosts"][str(host)] = None

        return inventory_dict
