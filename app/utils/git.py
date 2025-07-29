import logging
from pathlib import Path
from git import InvalidGitRepositoryError, Repo

from app.exceptions import GitGetOrCloneException, GitPullException, GitCommitException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepoHandler:
    def __init__(self, repo_url: str, repo_path: Path):
        self.repo_url = repo_url
        self.repo_path = repo_path
        self.repo = self._get_or_clone_repo()

    def _get_or_clone_repo(self):
        """
        Get the repository if it exists, otherwise clone it.
        """
        try:
            if not self.repo_path.exists():
                logger.info(f"Cloning repository from {self.repo_url} to {self.repo_path}")
                return Repo.clone_from(self.repo_url, self.repo_path, branch="main")
            else:
                logger.info(f"Repository already exists at {self.repo_path}")
                return Repo(self.repo_path)
        except InvalidGitRepositoryError as e:
            logger.error(f"Invalid Git repository: {e}")
            raise GitGetOrCloneException("Failed to get or clone the repository.") from e
        except Exception as e:
            logger.error(f"An error occurred while getting or cloning the repository: {e}")
            raise GitGetOrCloneException("Failed to get or clone the repository.") from e

    def fetch(self):
        """
        Fetch the latest changes from the remote repository.
        """
        try:
            self.repo.remotes.origin.fetch()
            logger.info("Fetched latest changes from remote repository.")
        except Exception as e:
            logger.error(f"Failed to fetch changes: {e}")
            raise GitPullException("Failed to fetch changes from the remote repository.") from e

    def checkout_and_pull(self, branch: str = "main"):
        """
        Pull the latest changes from the remote repository.
        """
        try:
            self.repo.git.checkout(branch)
            self.repo.remotes.origin.pull(branch)
            logger.info(f"Checked out and pulled branch {branch}.")
        except Exception as e:
            logger.error(f"Failed to checkout and pull branch {branch}: {e}")
            raise GitPullException(f"Failed to checkout and pull branch {branch}.") from e

    def commit_all(self, commit_msg: str):
        """
        Commit all changes in the repository with the given commit message.
        """
        try:
            self.repo.git.add(A=True)
            self.repo.index.commit(commit_msg)
            logger.info(f"Committed all changes with message: {commit_msg}")
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            raise GitCommitException("Failed to commit changes to the repository.") from e

    def get_local_branches(self, excluded_branches: list = []):
        """
        Get a list of local branches in the repository.
        """
        return [branch.name for branch in self.repo.branches if branch.name not in excluded_branches]

    def commit_and_push(self, commit_msg: str, branch: str = "main"):
        try:
            self.repo.git.add(A=True)
            self.repo.index.commit(commit_msg)
            self.repo.remotes.origin.push(branch)
            logger.info(f"Committed and pushed changes to branch {branch} with message: {commit_msg}")
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            raise GitCommitException("Failed to commit changes to the repository.") from e
    
    def delete_branch_entirely(self, branch: str = "main"):
        self.checkout_and_pull(branch="main")

        logger.info(f"Deleting local branch {branch}")
        if branch in [b.name for b in self.repo.repo.heads]:
            self.repo.delete_head(branch, force=True)

        try:
            logger.info(f"Deleting remote branch {branch}")
            self.repo.git.push("origin", "--delete", branch)
        except Exception as e:
            logger.error(f"Failed to delete remote branch {branch}: {e}")