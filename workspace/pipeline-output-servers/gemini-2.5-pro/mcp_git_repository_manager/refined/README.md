# mcp_git_repository_manager

## Overview

The `mcp_git_repository_manager` is a Model Context Protocol (MCP) server that provides Git repository management capabilities. It allows LLMs to interact with Git repositories through a set of standardized tools, enabling operations such as initializing repositories, checking status, committing changes, managing branches, and viewing commit history.

## Installation

To install the required dependencies:

1. Ensure you have Python 3.10 or higher installed.
2. Install the MCP SDK and GitPython:

```bash
pip install mcp[cli] gitpython
```

Make sure your environment supports UTF-8 encoding for proper operation.

## Running the Server

To run the server, execute the Python script from the command line:

```bash
python mcp_git_repository_manager.py
```

This will start the MCP server using standard input/output transport.

## Available Tools

Here is a list of available MCP tools provided by this server:

### Repository Initialization
- **`git_init(repo_path: str)`**  
  Initializes a new Git repository at the specified path.

### Status & Inspection
- **`git_status(repo_path: str)`**  
  Shows the working tree status including untracked files and changes not staged.
- **`git_diff_unstaged(repo_path: str)`**  
  Displays differences between the working directory and the staging area.
- **`git_diff_staged(repo_path: str)`**  
  Displays differences between the staging area and the last commit.
- **`git_diff(repo_path: str, base: str, compare: str = None)`**  
  Compares differences between two branches, commits, or a branch and the working directory.

### Changes Management
- **`git_add(repo_path: str, file_path: str)`**  
  Adds file changes to the staging area (index).
- **`git_reset(repo_path: str, file_path: str = None)`**  
  Unstages files from the staging area without modifying the working directory.
- **`git_commit(repo_path: str, message: str)`**  
  Records staged changes into the repository with a descriptive message.

### History & Logs
- **`git_log(repo_path: str, max_count: int = 10)`**  
  Shows the commit history of the current branch.
- **`git_show(repo_path: str, commit_hash: str)`**  
  Displays detailed information and changes of a specific commit.

### Branch Management
- **`git_create_branch(repo_path: str, branch_name: str)`**  
  Creates a new branch pointing to the current HEAD commit.
- **`git_checkout(repo_path: str, branch_name: str)`**  
  Switches to a specified branch, updating the working directory.