
from enum import Enum
import os
import logging
from pathlib import Path
import yaml
from app.exceptions import HostvarsNotFoundException
from app.models.entities import HOST_TYPE_REGISTRY
from app.models.hostvars import HOSTVARS_VALIDATOR, DropletHostvarsModel, HostvarsModel, ServerHostvarsModel
from app.models.inventory import InventoryEntry, InventoryUnion
from app.utils.git import RepoHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Need this to avoid YAML dumping None as 'null'
yaml.SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
)

def str_enum_representer(dumper, data):
    if isinstance(data, Enum):
        return dumper.represent_scalar('tag:yaml.org,2002:str', str(data.value))
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))

yaml.SafeDumper.add_multi_representer(Enum, str_enum_representer)

class HostvarsManager:
    def __init__(self, repo_url: str, repo_path: Path):
        self.repo_url = repo_url
        self.repo_path = repo_path
        self.repo = RepoHandler(repo_url, Path(repo_path))
        self.hostvars_path = Path(repo_path) / "hostvars.yml"

    def init(self, host_name: str, hostvars: HostvarsModel):
        """
        Create the branch and file for the host if it does not exist.
        """
        branch_name = f"{host_name}"
        self.repo.checkout_and_pull(branch=host_name)
        if not self.hostvars_path.exists():
            with open(self.hostvars_path, "w") as f:
                yaml.safe_dump(hostvars.model_dump(), f, default_flow_style=False, allow_unicode=True)

        self.repo.commit_and_push(f"Initialize hostvars for {host_name}", branch=branch_name)

    def delete(self, host_name: str):
        """
        Delete the branch and file for the host.
        """
        self.repo.checkout_and_pull(branch=host_name)

        logger.info(f"Deleting hostvars for {host_name}...")

        # Remove the file
        os.remove(self.repo_path / "hostvars.yml")
        self.repo.commit_and_push(f"Deleting hostvars for {host_name}", branch=host_name)

        # Remove the host's branch in Git
        self.repo.delete_branch_entirely(branch=host_name)


    def delete_all(self):
        """
        Delete all hostvars branches other than main.
        """
        logger.info("Fetching remote branches...")
   
        self.repo.checkout_and_pull(branch="main")

        # For every non-main branch, check it out, delete the hostvars file, commit and push the change, then remove the branch
        local_branches = self.repo.get_local_branches(excluded_branches=["main"])

        for branch in local_branches:
            logger.info(f"Checking out branch {branch}...")
            self.repo.checkout_and_pull(branch=branch)

            if self.hostvars_path.exists():
                logger.info(f"Deleting hostvars file for branch {branch}...")
                os.remove(self.hostvars_path)
                self.repo.commit_and_push(f"Delete hostvars for {branch}", branch=branch)
            else:
                logger.warning(f"No hostvars file found for branch {branch}, skipping deletion.")

        # We cannot delete a branch while checked out to it, so we check out main first
        self.repo.checkout_and_pull(branch="main")

        logger.info("Deleting all hostvars branches...")
        for branch in local_branches:
            logger.info(f"Deleting local branch {branch}...")
            self.repo.repo.delete_head(branch, force=True)

            try:
                logger.info(f"Deleting remote branch {branch}...")
                self.repo.repo.remotes.origin.push(refspec=f":{branch}")
            except Exception as e:
                logger.error(f"Failed to delete remote branch {branch}: {e}")


    def get(self, host_name: str):
        self.repo.checkout_and_pull(branch=host_name)
        if not self.hostvars_path.exists():
            raise HostvarsNotFoundException

        hv_data = {}
        with open(self.hostvars_path, "r") as f:
            hv_data = yaml.safe_load(f) or {}

        return hv_data

    def set(self, host: InventoryEntry, hostvars: HostvarsModel):
        """Set hostvars for a host entry."""
        self.repo.checkout_and_pull(branch=host.name)

        hostvars_dict = hostvars.model_dump()

        logger.info(f"Setting hostvars for {host.name}: {hostvars_dict}")

        with open(self.hostvars_path, "w") as f:
            yaml.safe_dump(hostvars_dict, f, default_flow_style=False, allow_unicode=True)

        self.repo.commit_and_push("Update hostvars", branch=host.name)
    
    def set_from_dict(self, host: InventoryEntry, hostvars_dict: dict):
        host_type = host.get_type()
        hostvars_model = HOSTVARS_VALIDATOR[host_type].model_validate(hostvars_dict)
        self.set(host, hostvars_model)
