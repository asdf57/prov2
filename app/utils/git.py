import logging
from pathlib import Path
from git import InvalidGitRepositoryError, Repo

from app.exceptions import GitGetOrCloneException, GitInitException, GitPullException, GitPushException


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepoHandler:
    def __init__(self, repo_url: str, repo_path: Path):
        self.repo_url = repo_url
        self.repo_path = repo_path
        try:
            self.repo = self._get_or_clone_repo()
        except Exception as e:
            logger.error(f"Failed to initialize repository: {e}")
            raise GitGetOrCloneException(f"Failed to initialize repository at {repo_path} from {repo_url}") from e

    def _get_or_clone_repo(self) -> Repo:
        if not self.repo_path.exists():
            logger.info(f"Repository path {self.repo_path} does not exist. Cloning from {self.repo_url} to {self.repo_path}")
            try:
                return Repo.clone_from(self.repo_url, self.repo_path)
            except Exception as e:
                logger.error(f"Failed to clone repository: {e}")
                raise GitGetOrCloneException(f"Failed to clone repository from {self.repo_url} to {self.repo_path}") from e

        try:
            return Repo(self.repo_path)
        except InvalidGitRepositoryError as e:
            logger.error(f"Path {self.repo_path} exists but is not a git repository. Initializing new git repo: {e}")
            try:
                repo = Repo.init(self.repo_path)
                if 'origin' not in repo.remotes:
                    repo.create_remote('origin', self.repo_url)

                return repo
            except Exception as e:
                logger.error(f"Failed to initialize git repo: {e}")
                raise GitInitException(f"Failed to initialize git repository at {self.repo_path}") from e

    def pull(self, branch: str = "main"):
        """
        Pull the latest changes from the remote repository.
        """
        try:
            self.repo.remotes.origin.pull(branch)
            logger.info(f"Successfully pulled changes from {branch} branch.")
        except Exception as e:
            logger.error(f"Failed to pull changes: {e}")
            raise GitPullException(f"Failed to pull changes from {branch} branch") from e

    def commit_all(self, commit_message: str):
        """
        Commit all changes in the repository with the given commit message.
        """
        self.repo.git.add(A=True)
        self.repo.index.commit(commit_message)

    def commit_and_push(self, commit_msg: str, branch: str = "main"):
        try:
            if branch not in self.repo.heads:
                logger.info(f"Branch '{branch}' not found. Creating it.")
                if not self.repo.head.is_valid():
                    self.repo.git.commit('--allow-empty', '-m', 'Initial commit')
                self.repo.git.checkout('-b', branch)
            else:
                self.repo.git.checkout(branch)

            self.repo.git.add(".")
            if self.repo.is_dirty(untracked_files=True):
                logger.info(f"Detected changes, committing to {branch} branch.")
                self.repo.index.commit(commit_msg)
            else:
                logger.info("No changes to commit")

            try:
                self.repo.git.push("origin", branch)
            except Exception:
                self.repo.git.push("--set-upstream", "origin", branch)
        except Exception as e:
            logger.error(f"Failed to commit and push: {e}")
            raise GitPushException(f"Failed to push changes to {branch} branch") from e