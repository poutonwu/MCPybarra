import os
import json
from mcp.server.fastmcp import FastMCP
from git import Repo, InvalidGitRepositoryError, NoSuchPathError, GitCommandError

class MCPGitServer:
    def __init__(self):
        self.mcp = FastMCP("mcp_git_repository_manager")

    def initialize_tools(self):
        @self.mcp.tool()
        def git_init(repo_path: str) -> str:
            """
            Initializes a new Git repository in the specified directory.

            Args:
                repo_path (str): The path where the new Git repository should be initialized.

            Returns:
                A string confirming the successful initialization of the Git repository.

            Example:
                git_init(repo_path="/path/to/new/repo")
            """
            try:
                # Validate input
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")

                # Initialize the repository
                repo = Repo.init(repo_path)
                return json.dumps({"status": "success", "message": f"Initialized Git repository at {repo.working_dir}"})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_status(repo_path: str) -> str:
            """
            Checks the status of the working tree in the specified Git repository.

            Args:
                repo_path (str): The path to the Git repository.

            Returns:
                A string containing the status information of the repository.

            Example:
                git_status(repo_path="/path/to/existing/repo")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")

                repo = Repo(repo_path)
                status = repo.git.status()
                return json.dumps({"status": "success", "message": status})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_add(repo_path: str, file_pattern: str) -> str:
            """
            Adds files to the staging area of the specified Git repository.

            Args:
                repo_path (str): The path to the Git repository.
                file_pattern (str): The pattern or specific file(s) to add to the staging area.

            Returns:
                A string confirming the successful addition of files to the staging area.

            Example:
                git_add(repo_path="/path/to/existing/repo", file_pattern="*.py")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")
                if not file_pattern or not isinstance(file_pattern, str):
                    raise ValueError("file_pattern must be a non-empty string.")

                repo = Repo(repo_path)
                repo.index.add([file_pattern])
                return json.dumps({"status": "success", "message": f"Added {file_pattern} to staging area."})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_diff_unstaged(repo_path: str) -> str:
            """
            Shows changes in the working tree not yet staged for the next commit.

            Args:
                repo_path (str): The path to the Git repository.

            Returns:
                A string containing the diff of unstaged changes.

            Example:
                git_diff_unstaged(repo_path="/path/to/existing/repo")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")

                repo = Repo(repo_path)
                diff = repo.git.diff(None)
                return json.dumps({"status": "success", "message": diff})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_diff_staged(repo_path: str) -> str:
            """
            Shows changes between the staging area and the latest commit.

            Args:
                repo_path (str): The path to the Git repository.

            Returns:
                A string containing the diff of staged changes.

            Example:
                git_diff_staged(repo_path="/path/to/existing/repo")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")

                repo = Repo(repo_path)
                diff = repo.git.diff('HEAD')
                return json.dumps({"status": "success", "message": diff})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_diff(repo_path: str, source_ref: str, target_ref: str) -> str:
            """
            Compares differences between two branches or commits.

            Args:
                repo_path (str): The path to the Git repository.
                source_ref (str): The source branch or commit hash.
                target_ref (str): The target branch or commit hash.

            Returns:
                A string containing the diff between the specified references.

            Example:
                git_diff(repo_path="/path/to/existing/repo", source_ref="main", target_ref="feature-branch")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")
                if not source_ref or not isinstance(source_ref, str):
                    raise ValueError("source_ref must be a non-empty string.")
                if not target_ref or not isinstance(target_ref, str):
                    raise ValueError("target_ref must be a non-empty string.")

                repo = Repo(repo_path)
                diff = repo.git.diff(f"{source_ref}..{target_ref}")
                return json.dumps({"status": "success", "message": diff})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_commit(repo_path: str, message: str) -> str:
            """
            Records changes to the repository by creating a new commit.

            Args:
                repo_path (str): The path to the Git repository.
                message (str): The commit message describing the changes.

            Returns:
                A string confirming the successful creation of a new commit.

            Example:
                git_commit(repo_path="/path/to/existing/repo", message="Add new feature")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")
                if not message or not isinstance(message, str):
                    raise ValueError("message must be a non-empty string.")

                repo = Repo(repo_path)
                commit = repo.index.commit(message)
                return json.dumps({"status": "success", "message": f"Created new commit: {commit.hexsha}"})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_reset(repo_path: str, file_pattern: str) -> str:
            """
            Removes files from the staging area without altering the working directory.

            Args:
                repo_path (str): The path to the Git repository.
                file_pattern (str): The pattern or specific file(s) to unstage.

            Returns:
                A string confirming the successful unstaging of files.

            Example:
                git_reset(repo_path="/path/to/existing/repo", file_pattern="*.py")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")
                if not file_pattern or not isinstance(file_pattern, str):
                    raise ValueError("file_pattern must be a non-empty string.")

                repo = Repo(repo_path)
                repo.git.reset('--', file_pattern)
                return json.dumps({"status": "success", "message": f"Unstaged {file_pattern}."})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_log(repo_path: str) -> str:
            """
            Displays the commit history of the specified Git repository.

            Args:
                repo_path (str): The path to the Git repository.

            Returns:
                A string containing the commit history.

            Example:
                git_log(repo_path="/path/to/existing/repo")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")

                repo = Repo(repo_path)
                log = repo.git.log()
                return json.dumps({"status": "success", "message": log})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_create_branch(repo_path: str, branch_name: str) -> str:
            """
            Creates a new branch in the specified Git repository.

            Args:
                repo_path (str): The path to the Git repository.
                branch_name (str): The name of the new branch to create.

            Returns:
                A string confirming the successful creation of the new branch.

            Example:
                git_create_branch(repo_path="/path/to/existing/repo", branch_name="new-feature")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")
                if not branch_name or not isinstance(branch_name, str):
                    raise ValueError("branch_name must be a non-empty string.")

                repo = Repo(repo_path)
                new_branch = repo.create_head(branch_name)
                return json.dumps({"status": "success", "message": f"Created new branch: {new_branch.name}"})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_checkout(repo_path: str, branch_name: str) -> str:
            """
            Switches the current working branch to the specified branch.

            Args:
                repo_path (str): The path to the Git repository.
                branch_name (str): The name of the branch to switch to.

            Returns:
                A string confirming the successful checkout of the specified branch.

            Example:
                git_checkout(repo_path="/path/to/existing/repo", branch_name="feature-branch")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")
                if not branch_name or not isinstance(branch_name, str):
                    raise ValueError("branch_name must be a non-empty string.")

                repo = Repo(repo_path)
                repo.git.checkout(branch_name)
                return json.dumps({"status": "success", "message": f"Checked out to branch: {branch_name}"})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

        @self.mcp.tool()
        def git_show(repo_path: str, commit_hash: str) -> str:
            """
            Displays detailed information about a specific commit.

            Args:
                repo_path (str): The path to the Git repository.
                commit_hash (str): The hash of the commit to display details for.

            Returns:
                A string containing the detailed information about the specified commit.

            Example:
                git_show(repo_path="/path/to/existing/repo", commit_hash="a1b2c3d4")
            """
            try:
                if not repo_path or not isinstance(repo_path, str):
                    raise ValueError("repo_path must be a non-empty string.")
                if not commit_hash or not isinstance(commit_hash, str):
                    raise ValueError("commit_hash must be a non-empty string.")

                repo = Repo(repo_path)
                show = repo.git.show(commit_hash)
                return json.dumps({"status": "success", "message": show})
            except (InvalidGitRepositoryError, NoSuchPathError, Exception) as e:
                return json.dumps({"status": "error", "message": str(e)})

    def run_server(self):
        self.initialize_tools()
        self.mcp.run()

if __name__ == "__main__":
    server = MCPGitServer()
    server.run_server()