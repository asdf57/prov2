import json
import os
import yaml
from pathlib import Path
from app.models.inventory import InventoryEntry
from app.utils.git import RepoHandler
from app.utils.inventory import Inventory
from app.utils.sanitize import sanitize_data

# Need this to avoid YAML dumping None as 'null'
yaml.SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
)

class InventoryManager:
    def __init__(self, repo_url: str, repo_path: Path):
        self.repo_url = repo_url
        self.repo_path = repo_path
        os.makedirs(repo_path, exist_ok=True)
        self.repo = RepoHandler(repo_url, Path(repo_path))
        self.inventory_path = Path(repo_path) / "inventory.yml"
        self.inventory = Inventory(self.inventory_path)
        self.repo.pull(branch="main")

    def save(self):
        """
        Save the current state of the inventory to the repository.
        """
        # Take the in-memory representation and write it to disk
        inventory = self.inventory.to_dict(refresh_from_disk=False)
        sanitized_inventory = sanitize_data(inventory)

        with open(self.inventory_path, "w") as f:
            yaml.safe_dump(sanitized_inventory, f, default_flow_style=False, allow_unicode=True)

        self.repo.commit_and_push("Update inventory", branch="main")

    def get_host(self, host_name: str) -> InventoryEntry:
        """
        Get a host entry from the inventory by its name.
        """
        self.repo.pull(branch="main")
        return self.inventory.get_host(host_name)

    def get_host_by_mac(self, mac: str) -> InventoryEntry | None:
        """
        Get a host entry from the inventory by its MAC address.
        """
        self.repo.pull(branch="main")
        return self.inventory.get_host_by_mac(mac)

    def get_all_hosts(self) -> list[InventoryEntry]:
        """
        Get all hosts in the inventory.
        """
        self.repo.pull(branch="main")
        return self.inventory.get_all_hosts()

    def get_inventory(self) -> dict:
        """
        Get the current inventory as a dictionary.
        """
        self.repo.pull(branch="main")
        return self.inventory.to_dict(refresh_from_disk=True)

    def add_host(self, entry: InventoryEntry):
        """
        Add a host to the inventory with its variables.
        """
        self.repo.pull(branch="main")
        self.inventory.add_host(entry)
        self.save()

    def remove_host(self, host_name: str):
        """
        Delete a host from the inventory.
        """
        self.repo.pull(branch="main")
        self.inventory.remove_host(host_name)
        self.save()

    def clear_inventory(self):
        """
        Clear the inventory by removing all hosts.
        """
        self.repo.pull(branch="main")
        self.inventory.clear_inventory()
        self.save()
