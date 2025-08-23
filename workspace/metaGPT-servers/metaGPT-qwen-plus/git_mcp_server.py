import sys
import asyncio
from mcp.server.fastmcp import FastMCP
from git import Repo, GitCommandError

# Initialize FastMCP server
mcp = FastMCP("git_repository_manager")

# Utility functions
def validate_repo_path(path: str) -> bool:
    """Validate repository path to prevent directory traversal attacks."""
    # Implement proper path validation
    return True  # Simplified for example

async def get_repo(path: str) -> Repo:
    """Get repository object from path."""
    try:
        return Repo(path)
    except Exception as e:
        raise ValueError(f"Invalid repository path: {path}") from e

# Git Operations

@mcp.tool()
async def git_init(path: str) -> str:
    """Initialize a new Git repository.

    Args:
        path: The directory path where to create the repository.

    Returns:
        A string containing the result message.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    try:
        Repo.init(path)
        return f"Repository initialized at {path}"
    except Exception as e:
        raise GitCommandError(['git', 'init'], 1, f"Failed to initialize repository: {str(e)}") from e

@mcp.tool()
async def git_status(path: str) -> str:
    """Get the status of a Git repository.

    Args:
        path: Path to the repository.

    Returns:
        A string containing the status output.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    return repo.git.status()

@mcp.tool()
async def git_add(path: str, file_pattern: str = ".") -> str:
    """Add files to the staging area.

    Args:
        path: Path to the repository.
        file_pattern: Pattern of files to add (default is all files).

    Returns:
        A string containing the result message.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    repo.git.add(file_pattern)
    return f"Added '{file_pattern}' to staging area in {path}"

@mcp.tool()
async def git_diff_unstaged(path: str) -> str:
    """Show differences in unstaged changes.

    Args:
        path: Path to the repository.

    Returns:
        A string containing the diff output.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    return repo.git.diff()

@mcp.tool()
async def git_diff_staged(path: str) -> str:
    """Show differences in staged changes.

    Args:
        path: Path to the repository.

    Returns:
        A string containing the diff output.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    return repo.git.diff('--cached')

@mcp.tool()
async def git_diff(path: str, commit_range: str) -> str:
    """Compare two commits or branches.

    Args:
        path: Path to the repository.
        commit_range: Range of commits to compare (e.g., 'HEAD~2..HEAD').

    Returns:
        A string containing the diff output.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    return repo.git.diff(commit_range)

@mcp.tool()
async def git_commit(path: str, message: str, author: str = None) -> str:
    """Commit changes in the repository.

    Args:
        path: Path to the repository.
        message: Commit message.
        author: Optional author name and email (format: 'Name <email>').

    Returns:
        A string containing the commit hash.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    if author:
        repo.git.commit(m=message, author=author)
    else:
        repo.git.commit(m=message)
    return f"Committed to {path} with message: {message}"

@mcp.tool()
async def git_reset(path: str, file_path: str = None) -> str:
    """Unstage changes in the repository.

    Args:
        path: Path to the repository.
        file_path: Optional specific file to unstage. If None, unstages all.

    Returns:
        A string containing the result message.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    if file_path:
        repo.git.reset(file_path)
        return f"Unstaged changes for {file_path} in {path}"
    else:
        repo.git.reset()
        return f"Unstaged all changes in {path}"

@mcp.tool()
async def git_log(path: str, max_count: int = 10) -> str:
    """View commit history.

    Args:
        path: Path to the repository.
        max_count: Maximum number of commits to show (default: 10).

    Returns:
        A string containing the commit history.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    return repo.git.log('-n', str(max_count))

@mcp.tool()
async def git_create_branch(path: str, branch_name: str) -> str:
    """Create a new branch.

    Args:
        path: Path to the repository.
        branch_name: Name of the new branch.

    Returns:
        A string containing the result message.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    repo.git.branch(branch_name)
    return f"Created branch '{branch_name}' in {path}"

@mcp.tool()
async def git_checkout(path: str, branch_name: str) -> str:
    """Switch to a different branch.

    Args:
        path: Path to the repository.
        branch_name: Name of the branch to switch to.

    Returns:
        A string containing the result message.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    repo.git.checkout(branch_name)
    return f"Switched to branch '{branch_name}' in {path}"

@mcp.tool()
async def git_show(path: str, commit_hash: str) -> str:
    """Display details of a specific commit.

    Args:
        path: Path to the repository.
        commit_hash: Hash of the commit to show.

    Returns:
        A string containing the commit details.

    Raises:
        ValueError: If the path is invalid.
        GitCommandError: If the git command fails.
    """
    repo = await get_repo(path)
    return repo.git.show(commit_hash)

# Run the server
if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        mcp.run()
    except Exception as e:
        print(f"Error running server: {str(e)}")
        sys.exit(1)