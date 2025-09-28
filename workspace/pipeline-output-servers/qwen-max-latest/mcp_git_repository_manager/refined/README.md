# mcp_git_repository_manager

## Overview
The `mcp_git_repository_manager` is a Model Context Protocol (MCP) server that provides Git repository management capabilities. It allows LLMs to interact with Git repositories by initializing, inspecting, modifying, and committing changes through a set of well-defined tools.

This server enables seamless integration between large language models and Git operations, making it easier to perform version control tasks programmatically within AI-driven workflows.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
gitpython
```

## Running the Server

To start the MCP Git Repository Manager server, run the following command:

```bash
python mcp_git_repository_manager.py
```

Make sure to replace `mcp_git_repository_manager.py` with the actual filename containing your server implementation.

## Available Tools

### Git Operations

- **`git_init(repo_path: str)`**  
  Initializes a new Git repository in the specified directory.

- **`git_status(repo_path: str = None)`**  
  Checks the status of the working tree in the specified Git repository.

- **`git_add(repo_path: str = None, file_pattern: str = "*")`**  
  Adds files to the staging area of the specified Git repository.

- **`git_diff_unstaged(repo_path: str = None)`**  
  Shows changes in the working tree not yet staged for the next commit.

- **`git_diff_staged(repo_path: str = None)`**  
  Shows changes between the staging area and the latest commit.

- **`git_diff(repo_path: str = None, source_ref: str = "main", target_ref: str = "feature-branch")`**  
  Compares differences between two branches or commits.

- **`git_commit(repo_path: str = None, message: str = "Commit changes")`**  
  Records changes to the repository by creating a new commit.

- **`git_reset(repo_path: str = None, file_pattern: str = "*")`**  
  Removes files from the staging area without altering the working directory.

- **`git_log(repo_path: str = None)`**  
  Displays the commit history of the specified Git repository.

- **`git_create_branch(repo_path: str = None, branch_name: str = "new-feature")`**  
  Creates a new branch in the specified Git repository.

- **`git_checkout(repo_path: str = None, branch_name: str = "feature-branch")`**  
  Switches the current working branch to the specified branch.

- **`git_show(repo_path: str = None, commit_hash: str = "a1b2c3d4")`**  
  Displays detailed information about a specific commit.

### File Operations

- **`text_write_file(file_path: str, content: str)`**  
  Writes content to a specified file. If the file exists, it will be overwritten.

- **`text_append_to_file(file_path: str, content: str)`**  
  Appends content to a specified file. If the file does not exist, it will be created.

- **`text_extract_regex(text: str, pattern: str)`**  
  Extracts the first match of a regular expression pattern from the given text.