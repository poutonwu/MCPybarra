import os
import sys
import git
from git import Repo
from mcp.server.fastmcp import FastMCP
import json

# Initialize MCP server
mcp = FastMCP("mcp_git_repo_manager")

@mcp.tool()
def git_init(directory: str) -> str:
    """
    Initializes a new Git repository in the specified directory.

    Args:
        directory (str): The path to the directory where the repository should be initialized. Example: '/path/to/new/repo'.

    Returns:
        str: Confirmation message indicating success or failure.

    Example:
        git_init(directory='/path/to/new/repo')
    """
    try:
        repo = Repo.init(directory)
        return json.dumps({"message": f"Initialized new Git repository at: {repo.working_dir}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_status(repository_path: str) -> dict:
    """
    Retrieves the status of the Git repository, showing changes in the working directory and staged files.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.

    Returns:
        dict: A dictionary containing the status of files (e.g., staged, unstaged, modified).

    Example:
        git_status(repository_path='/path/to/repo')
    """
    try:
        repo = Repo(repository_path)
        modified = [item.a_path for item in repo.index.diff(None)]
        staged = [item.a_path for item in repo.index.diff("HEAD")]
        untracked = repo.untracked_files

        return json.dumps({
            "modified": modified,
            "staged": staged,
            "untracked": untracked
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_add(repository_path: str, files: list) -> str:
    """
    Adds specified files to the staging area.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.
        files (list of str): List of file paths to add to the staging area. Example: ['file1.txt', 'file2.txt'].

    Returns:
        str: Confirmation message indicating the files added to the staging area.

    Example:
        git_add(repository_path='/path/to/repo', files=['file1.txt', 'file2.txt'])
    """
    try:
        repo = Repo(repository_path)
        repo.index.add(files)
        return json.dumps({"message": f"Added files to staging area: {files}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_diff_unstaged(repository_path: str) -> str:
    """
    Displays the differences in files that are not staged for commit.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.

    Returns:
        str: A string showing the diff of unstaged changes.

    Example:
        git_diff_unstaged(repository_path='/path/to/repo')
    """
    try:
        repo = Repo(repository_path)
        diffs = repo.index.diff(None)
        return json.dumps({"unstaged_diff": [str(diff) for diff in diffs]})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_diff_staged(repository_path: str) -> str:
    """
    Displays the differences in files that are staged for commit.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.

    Returns:
        str: A string showing the diff of staged changes.

    Example:
        git_diff_staged(repository_path='/path/to/repo')
    """
    try:
        repo = Repo(repository_path)
        diffs = repo.index.diff("HEAD")
        return json.dumps({"staged_diff": [str(diff) for diff in diffs]})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_diff(repository_path: str, reference1: str, reference2: str) -> str:
    """
    Compares two branches or commits and displays the differences.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.
        reference1 (str): The first branch or commit to compare. Example: 'HEAD'.
        reference2 (str): The second branch or commit to compare. Example: 'HEAD~1'.

    Returns:
        str: A string showing the diff between the two references.

    Example:
        git_diff(repository_path='/path/to/repo', reference1='HEAD', reference2='HEAD~1')
    """
    try:
        repo = Repo(repository_path)
        diffs = repo.commit(reference1).diff(reference2)
        return json.dumps({"diff": [str(diff) for diff in diffs]})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_commit(repository_path: str, message: str) -> str:
    """
    Commits staged changes to the repository.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.
        message (str): Commit message describing the changes. Example: 'Initial commit'.

    Returns:
        str: Confirmation message with the commit hash.

    Example:
        git_commit(repository_path='/path/to/repo', message='Initial commit')
    """
    try:
        repo = Repo(repository_path)
        new_commit = repo.index.commit(message)
        return json.dumps({"message": f"Created new commit: {new_commit.hexsha}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_reset(repository_path: str, files: list) -> str:
    """
    Removes files from the staging area.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.
        files (list of str): List of file paths to remove from the staging area. Example: ['file1.txt', 'file2.txt'].

    Returns:
        str: Confirmation message indicating the files reset.

    Example:
        git_reset(repository_path='/path/to/repo', files=['file1.txt', 'file2.txt'])
    """
    try:
        repo = Repo(repository_path)
        repo.index.reset(files)
        return json.dumps({"message": f"Removed files from staging area: {files}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_log(repository_path: str) -> list:
    """
    Displays the commit history of the repository.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.

    Returns:
        list: A list of dictionaries, each containing commit details (e.g., hash, author, date, message).

    Example:
        git_log(repository_path='/path/to/repo')
    """
    try:
        repo = Repo(repository_path)
        commits = repo.iter_commits()
        return json.dumps([{ "hash": commit.hexsha, "author": commit.author.name, "date": commit.committed_date, "message": commit.message } for commit in commits])
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_create_branch(repository_path: str, branch_name: str) -> str:
    """
    Creates a new branch in the repository.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.
        branch_name (str): Name of the new branch. Example: 'new-feature'.

    Returns:
        str: Confirmation message indicating success or failure.

    Example:
        git_create_branch(repository_path='/path/to/repo', branch_name='new-feature')
    """
    try:
        repo = Repo(repository_path)
        repo.create_head(branch_name)
        return json.dumps({"message": f"Created new branch: {branch_name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_checkout(repository_path: str, branch_name: str) -> str:
    """
    Switches the current branch in the repository.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.
        branch_name (str): Name of the branch to switch to. Example: 'main'.

    Returns:
        str: Confirmation message indicating the branch switched.

    Example:
        git_checkout(repository_path='/path/to/repo', branch_name='main')
    """
    try:
        repo = Repo(repository_path)
        repo.git.checkout(branch_name)
        return json.dumps({"message": f"Switched to branch: {branch_name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def git_show(repository_path: str, commit_hash: str) -> dict:
    """
    Displays detailed information about a specific commit.

    Args:
        repository_path (str): Path to the Git repository. Example: '/path/to/repo'.
        commit_hash (str): The hash of the commit to display. Example: 'abc123'.

    Returns:
        dict: A dictionary containing commit details (e.g., hash, author, date, message, changes).

    Example:
        git_show(repository_path='/path/to/repo', commit_hash='abc123')
    """
    try:
        repo = Repo(repository_path)
        commit = repo.commit(commit_hash)
        return json.dumps({
            "hash": commit.hexsha,
            "author": commit.author.name,
            "date": commit.committed_date,
            "message": commit.message,
            "stats": commit.stats.files
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()