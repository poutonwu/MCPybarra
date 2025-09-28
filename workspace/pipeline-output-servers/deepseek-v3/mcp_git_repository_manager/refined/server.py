import sys
import os
import re
import json
from typing import List, Optional
from git import Repo, GitCommandError
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_git_repository_manager")

# --- Helper Functions ---

def ensure_directory_exists(directory: str) -> None:
    """Ensure the directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.isdir(directory):
        raise ValueError(f"Path is not a directory: {directory}")

def validate_directory(directory: str) -> None:
    """Validate the directory path exists and is a Git repository if required."""
    if not os.path.exists(directory):
        raise ValueError(f"Directory does not exist: {directory}")
    if not os.path.isdir(directory):
        raise ValueError(f"Path is not a directory: {directory}")

# --- Git Tools ---

@mcp.tool()
def git_init(directory: str) -> str:
    """
    Initialize a new Git repository in the specified directory.

    Args:
        directory: The path where the Git repository will be initialized.

    Returns:
        A string indicating the success or failure of the initialization.

    Raises:
        ValueError: If the directory is invalid.
        GitCommandError: If Git initialization fails.
    """
    try:
        ensure_directory_exists(directory)
        Repo.init(directory)
        return f"Git repository initialized successfully in {directory}"
    except (ValueError, GitCommandError) as e:
        return f"Error initializing Git repository: {str(e)}"

@mcp.tool()
def text_write(file_path: str, content: str) -> str:
    """
    Write content to a specified file.

    Args:
        file_path: The path to the file that should be created or overwritten.
        content: The content to write into the file.

    Returns:
        A confirmation message indicating success or an error message.

    Raises:
        ValueError: If the file path is invalid.
    """
    try:
        # Ensure the directory exists before writing the file
        directory = os.path.dirname(file_path)
        ensure_directory_exists(directory)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote content to {file_path}"
    except (ValueError, IOError) as e:
        return f"Error writing to file: {str(e)}"

@mcp.tool()
def git_status(directory: str) -> str:
    """
    Display the current state of the Git repository.

    Args:
        directory: The path to the Git repository.

    Returns:
        A string containing the status information.

    Raises:
        ValueError: If the directory is invalid.
        GitCommandError: If Git status fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        return repo.git.status()
    except (ValueError, GitCommandError) as e:
        return f"Error getting Git status: {str(e)}"

@mcp.tool()
def git_add(directory: str, files: List[str]) -> str:
    """
    Add specified files to the Git staging area.

    Args:
        directory: The path to the Git repository.
        files: A list of file paths to add to the staging area.

    Returns:
        A string confirming the files were added or an error message.

    Raises:
        ValueError: If the directory or files are invalid.
        GitCommandError: If Git add fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        repo.index.add(files)
        return f"Added files to staging area: {', '.join(files)}"
    except (ValueError, GitCommandError) as e:
        return f"Error adding files to Git: {str(e)}"

@mcp.tool()
def git_diff_unstaged(directory: str) -> str:
    """
    Show the differences between the working directory and the last commit (unstaged changes).

    Args:
        directory: The path to the Git repository.

    Returns:
        A string detailing the unstaged differences.

    Raises:
        ValueError: If the directory is invalid.
        GitCommandError: If Git diff fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        return repo.git.diff()
    except (ValueError, GitCommandError) as e:
        return f"Error getting unstaged differences: {str(e)}"

@mcp.tool()
def git_diff_staged(directory: str) -> str:
    """
    Show the differences between the staging area and the last commit (staged changes).

    Args:
        directory: The path to the Git repository.

    Returns:
        A string detailing the staged differences.

    Raises:
        ValueError: If the directory is invalid.
        GitCommandError: If Git diff fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        return repo.git.diff("--cached")
    except (ValueError, GitCommandError) as e:
        return f"Error getting staged differences: {str(e)}"

@mcp.tool()
def git_diff(directory: str, source: str, target: str) -> str:
    """
    Compare differences between branches, commits, or files.

    Args:
        directory: The path to the Git repository.
        source: The source branch, commit, or file.
        target: The target branch, commit, or file.

    Returns:
        A string detailing the differences.

    Raises:
        ValueError: If the directory, source, or target is invalid.
        GitCommandError: If Git diff fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        return repo.git.diff(source, target)
    except (ValueError, GitCommandError) as e:
        return f"Error comparing differences: {str(e)}"

@mcp.tool()
def git_commit(directory: str, message: str) -> str:
    """
    Commit the staged changes to the repository with a message.

    Args:
        directory: The path to the Git repository.
        message: The commit message.

    Returns:
        A string confirming the commit or an error message.

    Raises:
        ValueError: If the directory or message is invalid.
        GitCommandError: If Git commit fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        if not repo.index.diff("--cached"):
            return "No staged changes to commit"
        repo.index.commit(message)
        return f"Committed changes with message: {message}"
    except (ValueError, GitCommandError) as e:
        return f"Error committing changes: {str(e)}"

@mcp.tool()
def git_reset(directory: str, files: List[str]) -> str:
    """
    Unstage files from the staging area.

    Args:
        directory: The path to the Git repository.
        files: A list of file paths to unstage.

    Returns:
        A string confirming the reset or an error message.

    Raises:
        ValueError: If the directory or files are invalid.
        GitCommandError: If Git reset fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        repo.index.unstage(files)
        return f"Unstaged files: {', '.join(files)}"
    except (ValueError, GitCommandError) as e:
        return f"Error unstaging files: {str(e)}"

@mcp.tool()
def git_log(directory: str) -> str:
    """
    Display the commit history of the repository.

    Args:
        directory: The path to the Git repository.

    Returns:
        A string containing the commit history.

    Raises:
        ValueError: If the directory is invalid.
        GitCommandError: If Git log fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        return repo.git.log()
    except (ValueError, GitCommandError) as e:
        return f"Error getting commit history: {str(e)}"

@mcp.tool()
def git_create_branch(directory: str, branch_name: str) -> str:
    """
    Create a new branch in the repository.

    Args:
        directory: The path to the Git repository.
        branch_name: The name of the new branch.

    Returns:
        A string confirming the branch creation or an error message.

    Raises:
        ValueError: If the directory or branch name is invalid.
        GitCommandError: If Git branch creation fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        repo.create_head(branch_name)
        return f"Created new branch: {branch_name}"
    except (ValueError, GitCommandError) as e:
        return f"Error creating branch: {str(e)}"

@mcp.tool()
def git_checkout(directory: str, target: str) -> str:
    """
    Switch to a specified branch or commit.

    Args:
        directory: The path to the Git repository.
        target: The branch name or commit hash to switch to.

    Returns:
        A string confirming the checkout or an error message.

    Raises:
        ValueError: If the directory or target is invalid.
        GitCommandError: If Git checkout fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        repo.git.checkout(target)
        return f"Checked out to: {target}"
    except (ValueError, GitCommandError) as e:
        return f"Error checking out: {str(e)}"

@mcp.tool()
def git_show(directory: str, commit_hash: str) -> str:
    """
    Display detailed information about a specific commit.

    Args:
        directory: The path to the Git repository.
        commit_hash: The hash of the commit to display.

    Returns:
        A string containing the commit details.

    Raises:
        ValueError: If the directory or commit hash is invalid.
        GitCommandError: If Git show fails.
    """
    try:
        validate_directory(directory)
        repo = Repo(directory)
        return repo.git.show(commit_hash)
    except (ValueError, GitCommandError) as e:
        return f"Error showing commit details: {str(e)}"

# --- Main Execution ---

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()