# mcp_git_repository_manager

## Overview

The `mcp_git_repository_manager` is a Model Context Protocol (MCP) server that provides Git repository management capabilities. It allows LLMs and other clients to interact with Git repositories through a standardized interface, enabling operations such as initialization, file writing, staging, committing, branching, and more.

This server integrates with the `gitpython` library to provide robust Git functionality while ensuring clean error handling and informative responses.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
GitPython
```

## Running the Server

To start the server using the standard input/output transport protocol, run:

```bash
python mcp_git_repository_manager.py
```

Alternatively, specify a different transport protocol if needed:

```bash
python mcp_git_repository_manager.py --transport sse
```

## Available Tools

Below is a list of available MCP tools provided by this server:

### Repository Management

- **`git_init(directory: str)`**  
  Initializes a new Git repository in the specified directory.

- **`git_status(directory: str)`**  
  Displays the current status of the Git repository (e.g., modified files, untracked files).

- **`git_log(directory: str)`**  
  Shows the commit history of the repository.

- **`git_show(directory: str, commit_hash: str)`**  
  Displays detailed information about a specific commit.

- **`git_create_branch(directory: str, branch_name: str)`**  
  Creates a new branch with the given name.

- **`git_checkout(directory: str, target: str)`**  
  Switches to the specified branch or commit.

### File Operations

- **`text_write(file_path: str, content: str)`**  
  Writes the given content to the specified file, creating or overwriting it.

### Staging & Committing Changes

- **`git_add(directory: str, files: List[str])`**  
  Adds the specified files to the Git staging area.

- **`git_reset(directory: str, files: List[str])`**  
  Unstages the specified files from the staging area.

- **`git_commit(directory: str, message: str)`**  
  Commits the staged changes with the provided commit message.

### Diff Inspection

- **`git_diff_unstaged(directory: str)`**  
  Shows differences between the working directory and the last commit (unstaged changes).

- **`git_diff_staged(directory: str)`**  
  Shows differences between the staging area and the last commit (staged changes).

- **`git_diff(directory: str, source: str, target: str)`**  
  Compares differences between branches, commits, or files.