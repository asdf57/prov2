
from enum import Enum
import os
import logging
from pathlib import Path
import yaml
from app.models.entities import HOST_TYPE_REGISTRY
from app.models.hostvars import DropletHostvarsModel, HostvarsModel, ServerHostvarsModel
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
        os.makedirs(repo_path, exist_ok=True)
        self.repo = RepoHandler(repo_url, Path(repo_path))
        self.hostvars_path = Path(repo_path) / "hostvars.yml"
        self.repo.pull(branch="main")

    def init(self, host_name: str, hostvars: HostvarsModel):
        """
        Create the branch and file for the host if it does not exist.
        """
        branch_name = f"{host_name}"
        self.repo.pull(branch="main")
        if branch_name not in self.repo.repo.heads:
            self.repo.repo.create_head(branch_name)
            self.repo.repo.heads[branch_name].checkout()
            if not self.hostvars_path.exists():
                with open(self.hostvars_path, "w") as f:
                    yaml.safe_dump(hostvars.model_dump(), f, default_flow_style=False, allow_unicode=True)
            self.repo.commit_and_push(f"Initialize hostvars for {host_name}", branch=branch_name)
        else:
            self.repo.repo.heads[branch_name].checkout()

    def delete(self, host_name: str):
        """
        Delete the branch and file for the host.
        """
        self.repo.repo.git.checkout("main")
        self.repo.pull(branch="main")

        logger.info(f"Deleting hostvars for {host_name}...")

        if host_name in self.repo.repo.heads:
            self.repo.repo.delete_head(host_name, force=True)
            logger.info(f"Deleted branch {host_name} successfully.")

        try:
            logger.info(f"Deleting remote branch {host_name}...")
            self.repo.repo.git.push("origin", f"--delete", host_name)
            logger.info(f"Remote branch {host_name} deleted")
        except Exception as e:
            logger.error(f"Failed to delete remote branch: {e}")

    def delete_all(self):
        """
        Delete all hostvars branches other than main.
        """
        self.repo.repo.git.checkout("main")
        self.repo.pull(branch="main")

        logger.info("Fetching remote branches...")
        self.repo.repo.remotes.origin.fetch(prune=True)

        remote = self.repo.repo.remotes.origin
        remote_refs = remote.refs
        remote_branches = [ref.remote_head for ref in remote_refs 
                        if hasattr(ref, 'remote_head') and ref.remote_head not in ["main", "master", "HEAD"]]
        logger.info(f"Remote branches found: {remote_branches}")

        local_branches = [b.name for b in self.repo.repo.heads if b.name not in ["main", "master"]]

        logger.info("Deleting all hostvars branches...")
        for branch in local_branches:
            logger.info(f"Deleting local branch {branch}...")
            self.repo.repo.delete_head(branch, force=True)

        if remote_branches:
            logger.info(f"Deleting remote branches: {remote_branches}")
            try:
                self.repo.repo.git.push("origin", "--delete", *remote_branches)
                logger.info("Remote branches deleted")
            except Exception as e:
                logger.error(f"Failed to delete remote branches: {e}")
        else:
            logger.info("No remote branches to delete")

    def get(self, branch: str):
        self.repo.pull(branch=branch)
        if not self.hostvars_path.exists():
            return {}

        hv_data = {}
        with open(self.hostvars_path, "r") as f:
            hv_data = yaml.safe_load(f) or {}

        return hv_data

    def set(self, host: InventoryEntry, hostvars: HostvarsModel):
        """Set hostvars for a host entry."""
        hostvars_dict = hostvars.model_dump()

        logger.info(f"Setting hostvars for {host.name}: {hostvars_dict}")

        self.repo.pull(branch=host.name)
        with open(self.hostvars_path, "w") as f:
            yaml.safe_dump(hostvars_dict, f, default_flow_style=False, allow_unicode=True)

        self.repo.commit_and_push("Update hostvars", branch=host.name)