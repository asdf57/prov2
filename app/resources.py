from app.utils.inventory_manager import InventoryManager
from app.utils.hostvars_manager import HostvarsManager
from app.utils.concourse_manager import ConcourseManager
from app.utils.commands_manager import CommandsManager
from app.config import (
    CONCOURSE_URL,
    CONCOURSE_USER,
    CONCOURSE_PASSWORD,
    CONCOURSE_TEAM,
    CONCOURSE_COMMANDS_PIPELINE,
    CONCOURSE_COMMANDS_RESOURCE,
)
from app.utils.kauf_manager import KaufManager

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

concourse_manager = ConcourseManager(CONCOURSE_URL, CONCOURSE_USER, CONCOURSE_PASSWORD)
def get_concourse_manager() -> ConcourseManager:
    """
    Dependency to get the concourse manager.
    """
    return concourse_manager

commands_manager = CommandsManager(
    CONCOURSE_TEAM,
    CONCOURSE_COMMANDS_PIPELINE,
    CONCOURSE_COMMANDS_RESOURCE,
    "git@github.com:asdf57/commands_data.git",
    "/app/commands_data",
    concourse_manager
)
def get_commands_manager() -> CommandsManager:
    """
    Dependency to get the commands manager.
    """
    return commands_manager

def get_kauf_manager_factory():
    """
    Dependency to get the kauf manager factory.
    """

    def create_kauf_manager(node_name: str) -> KaufManager:
        return KaufManager(node_name)

    return create_kauf_manager
