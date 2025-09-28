import sys
import os
import json
from mcp.server.fastmcp import FastMCP
import git
from git import Repo, GitCommandError, InvalidGitRepositoryError

# Initialize FastMCP server
mcp = FastMCP("mcp_git_repository_manager")

def _get_repo(repo_path: str) -> Repo:
    """
    Helper function to get a GitPython Repo object.

    Args:
        repo_path (str): The local directory path where the Git repository is located.

    Returns:
        Repo: A GitPython Repo object for the specified repository.

    Raises:
        FileNotFoundError: If the repository path does not exist or is not a directory.
        ValueError: If the path is not a valid Git repository.
        RuntimeError: For other unexpected errors during repository loading.
    """
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"Repository path not found: {repo_path}")
    try:
        return Repo(repo_path)
    except InvalidGitRepositoryError:
        raise ValueError(f"Invalid Git repository: {repo_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to load repository at {repo_path}: {e}")

@mcp.tool()
def git_init(repo_path: str) -> str:
    """
    Initializes a new Git repository at the specified path.

    This function creates an empty Git repository in the given directory. If the
    directory does not exist, it will be created. If a Git repository already
    exists at the path, an error will be returned.

    Args:
        repo_path (str): The local directory path to initialize as a Git repository.
                         Example: "/path/to/my-repo"

    Returns:
        str: A JSON string confirming the repository initialization or reporting an error.
             On success: '{"status": "success", "message": "Repository initialized at /path/to/my-repo"}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        if os.path.isdir(os.path.join(repo_path, '.git')):
            return json.dumps({"status": "error", "message": f"Repository already exists at {repo_path}"})
        repo = Repo.init(repo_path)
        return json.dumps({"status": "success", "message": f"Repository initialized at {repo.working_dir}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def git_status(repo_path: str) -> str:
    """
    Shows the working tree status of a Git repository.

    This function provides a summary of the current state of the repository,
    including untracked files, changes not staged for commit, and changes
    to be committed.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"

    Returns:
        str: A JSON string containing the Git repository's current status or an error message.
             On success: '{"status": "success", "data": "status output"}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        return json.dumps({"status": "success", "data": repo.git.status()})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_add(repo_path: str, file_path: str) -> str:
    """
    Adds file changes to the staging area (index).

    This function stages changes in a specific file or all changes in the
    working directory, preparing them for the next commit.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        file_path (str): The file path to add to the staging area. Use '.' to add all changes.
                         Example: "my_file.py" or "."

    Returns:
        str: A JSON string confirming the addition or reporting an error.
             On success: '{"status": "success", "message": "Added 'my_file.py' to the staging area."}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        repo.git.add(file_path)
        message = f"Added '{file_path}' to the staging area." if file_path != '.' else "Added all changes to the staging area."
        return json.dumps({"status": "success", "message": message})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except GitCommandError as e:
        return json.dumps({"status": "error", "message": f"Git command failed: {e}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_diff_unstaged(repo_path: str) -> str:
    """
    Shows changes in the working directory that are not yet staged.

    This function displays the differences between the files in the working
    directory and the staging area (index). It highlights modifications that
    have not been added for commit.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"

    Returns:
        str: A JSON string containing the diff of unstaged changes or an error message.
             On success: '{"status": "success", "data": "diff output"}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        diff_output = repo.git.diff()
        return json.dumps({"status": "success", "data": diff_output})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_diff_staged(repo_path: str) -> str:
    """
    Shows changes that are staged but not yet committed.

    This function displays the differences between the staging area (index) and
    the last commit (HEAD). It shows what will be included in the next commit.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"

    Returns:
        str: A JSON string containing the diff of staged changes or an error message.
             On success: '{"status": "success", "data": "diff output"}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        diff_output = repo.git.diff('--staged')
        return json.dumps({"status": "success", "data": diff_output})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_diff(repo_path: str, base: str, compare: str = None) -> str:
    """
    Compares differences between two branches, commits, or a branch and the working directory.

    This function provides a flexible way to see the changes between different
    points in the repository's history.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        base (str): The base branch or commit hash for comparison.
                    Example: "main"
        compare (str, optional): The branch or commit hash to compare with the base.
                                 If not provided, compares the base with the current
                                 working directory.
                                 Example: "develop"

    Returns:
        str: A JSON string containing the diff between the two references or an error message.
             On success: '{"status": "success", "data": "diff output"}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        diff_output = repo.git.diff(base, compare) if compare else repo.git.diff(base)
        return json.dumps({"status": "success", "data": diff_output})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except GitCommandError as e:
        return json.dumps({"status": "error", "message": f"Git command failed: {e}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_commit(repo_path: str, message: str) -> str:
    """
    Records staged changes to the repository.

    This function creates a new commit containing the content of the staging area
    (index) along with a descriptive commit message. An error is returned if
    there are no changes staged for commit.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        message (str): The commit message.
                       Example: "feat: Add new feature"

    Returns:
        str: A JSON string containing the new commit's hash or an error message.
             On success: '{"status": "success", "commit_hash": "a1b2c3d4..."}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        commit = repo.index.commit(message)
        return json.dumps({"status": "success", "commit_hash": commit.hexsha})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        # GitPython raises a generic Exception for an empty commit
        return json.dumps({"status": "error", "message": f"Commit failed: {e}. This may be due to an empty commit."})

@mcp.tool()
def git_reset(repo_path: str, file_path: str = None) -> str:
    """
    Unstages files from the staging area (index).

    This function removes files from the staging area, effectively undoing a
    'git add' command. It does not modify the working directory.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        file_path (str, optional): The specific file path to remove from the staging area.
                                   If not provided, all files are unstaged.
                                   Example: "my_file.py"

    Returns:
        str: A JSON string confirming the reset or reporting an error.
             On success: '{"status": "success", "message": "Unstaged 'my_file.py'."}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        if file_path:
            # GitPython's reset expects a list of paths
            repo.index.reset(paths=[file_path])
            message = f"Unstaged '{file_path}'."
        else:
            repo.index.reset()
            message = "Unstaged all files."
        return json.dumps({"status": "success", "message": message})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_log(repo_path: str, max_count: int = 10) -> str:
    """
    Shows the commit history of the current branch.

    This function retrieves a list of the most recent commits, providing details
    such as commit hash, author, date, and message for each.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        max_count (int, optional): The maximum number of log entries to show.
                                   Defaults to 10. Example: 5

    Returns:
        str: A JSON string containing the formatted commit history log or an error message.
             On success: '{"status": "success", "data": [{"hash": ..., "author": ..., "date": ..., "message": ...}]}'
             On failure: '{"status": "error", "message": "Error description"}'
    """
    try:
        repo = _get_repo(repo_path)
        log_entries = list(repo.iter_commits(max_count=max_count))
        log_data = [
            {
                "hash": c.hexsha,
                "author": f"{c.author.name} <{c.author.email}>",
                "date": c.authored_datetime.isoformat(),
                "message": c.message.strip(),
            }
            for c in log_entries
        ]
        return json.dumps({"status": "success", "data": log_data})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_create_branch(repo_path: str, branch_name: str) -> str:
    """
    Creates a new branch in the repository.

    The new branch is created pointing to the current HEAD commit. This function
    does not switch to the new branch.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        branch_name (str): The name of the new branch to create.
                           Example: "feature/new-branch"

    Returns:
        str: A JSON string confirming the branch creation or reporting an error.
             On success: '{"status": "success", "message": "Branch 'feature/new-branch' created."}'
             On failure: '{"status": "error", "message": "Branch 'feature/new-branch' already exists."}'
    """
    try:
        repo = _get_repo(repo_path)
        if branch_name in repo.heads:
             return json.dumps({"status": "error", "message": f"Branch '{branch_name}' already exists."})
        new_branch = repo.create_head(branch_name)
        return json.dumps({"status": "success", "message": f"Branch '{new_branch.name}' created."})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_checkout(repo_path: str, branch_name: str) -> str:
    """
    Switches to a specified branch, updating the working directory.

    This function changes the current active branch to the one specified. The
    files in the working directory will be updated to match the version in
    the new branch.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        branch_name (str): The name of the branch to switch to.
                           Example: "main"

    Returns:
        str: A JSON string confirming the branch switch or reporting an error.
             On success: '{"status": "success", "message": "Switched to branch 'main'."}'
             On failure: '{"status": "error", "message": "Branch 'main' not found."}'
    """
    try:
        repo = _get_repo(repo_path)
        if branch_name not in repo.heads:
             return json.dumps({"status": "error", "message": f"Branch '{branch_name}' not found."})
        repo.heads[branch_name].checkout()
        return json.dumps({"status": "success", "message": f"Switched to branch '{branch_name}'."})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

@mcp.tool()
def git_show(repo_path: str, commit_hash: str) -> str:
    """
    Shows details and changes of a specific commit.

    This function provides metadata (author, date, message) and the patch
    (diff) for a given commit hash.

    Args:
        repo_path (str): The local path of the Git repository.
                         Example: "/path/to/my-repo"
        commit_hash (str): The hash of the commit to view details for. Can be a short hash.
                           Example: "a1b2c3d4"

    Returns:
        str: A JSON string containing detailed information about the specified commit or an error message.
             On success: '{"status": "success", "data": {"hash": ..., "author": ..., "date": ..., "message": ..., "diff": ...}}'
             On failure: '{"status": "error", "message": "Commit with hash 'a1b2c3d4' not found."}'
    """
    try:
        repo = _get_repo(repo_path)
        commit = repo.commit(commit_hash)
        commit_details = {
            "hash": commit.hexsha,
            "author": f"{commit.author.name} <{commit.author.email}>",
            "date": commit.authored_datetime.isoformat(),
            "message": commit.message.strip(),
            "diff": repo.git.show(commit.hexsha)
        }
        return json.dumps({"status": "success", "data": commit_details})
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        return json.dumps({"status": "error", "message": str(e)})
    except GitCommandError:
        return json.dumps({"status": "error", "message": f"Commit with hash '{commit_hash}' not found."})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {e}"})

if __name__ == "__main__":
    if sys.platform == "win32":
        # Set console output encoding to UTF-8 on Windows
        os.system("chcp 65001 > nul")
    # Ensure stdout handles UTF-8 for cross-platform compatibility
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()