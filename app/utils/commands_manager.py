import time
from pathlib import Path
from app.utils.concourse_manager import ConcourseManager
from app.utils.git import RepoHandler


class CommandsManager:
    def __init__(self, concourse_team: str, concourse_commands_pipeline: str, commands_resource: str, repo_url: str, repo_path: Path, concourse_manager: ConcourseManager):
        self.concourse_team = concourse_team
        self.concourse_commands_pipeline = concourse_commands_pipeline
        self.commands_resource = commands_resource
        self.repo_url = repo_url
        self.repo_path = Path(repo_path)
        self.repo = RepoHandler(repo_url, self.repo_path)
        self.concourse_manager = concourse_manager

    def add_command(self, command: str):
        """
        Add a new command to the commands repo and trigger a Concourse resource check.
        """
        self.repo.checkout_and_pull(branch="main")

        commands_file = self.repo_path / "commands"
        with open(commands_file, "w") as f:
            f.write(command)

        self.repo.commit_and_push(f"Update commands file", branch="main")

        self.concourse_manager.trigger_resource_check(
            self.concourse_team,
            self.concourse_commands_pipeline,
            self.commands_resource
        )

        time.sleep(1)

        self.concourse_manager.trigger_job(
            self.concourse_team,
            self.concourse_commands_pipeline,
            "commands",
        )

    def add_node_command(self, node: str, command: str, user: str = "root"):
        """
        Add a new command for a specific node to the commands repo and trigger a Concourse resource check.
        """
        self.repo.checkout_and_pull(branch=node, create_if_missing=True)

        commands_file = self.repo_path / "commands"

        yaml_content = f"user: {user}\ncommands: |\n"

        for line in command.splitlines():
            yaml_content += f"  {line}\n"
        
        with open(commands_file, "w") as f:
            f.write(yaml_content)

        self.repo.commit_and_push(f"Update commands file for {node}", branch=node)

        self.concourse_manager.trigger_resource_check(
            self.concourse_team,
            f"{node}-commands",
            self.commands_resource
        )

        time.sleep(1)

        self.concourse_manager.trigger_job(
            self.concourse_team,
            f"{node}-commands",
            "commands",
        )
