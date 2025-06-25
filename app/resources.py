from app.utils.inventory_manager import InventoryManager
from app.utils.hostvars_manager import HostvarsManager

inventory_manager = InventoryManager("git@github.com:asdf57/inventory.git", "/app/inventory")
def get_inventory_manager() -> InventoryManager:
    """
    Dependency to get the inventory manager.
    """
    return inventory_manager

hostvars_manager = HostvarsManager("git@github.com:asdf57/hostvars.git", "/app/hostvars")
def get_hostvars_manager() -> HostvarsManager:
    """
    Dependency to get the hostvars manager.
    """
    return hostvars_manager
