# mcp_git_repo_manager

## Overview
`mcp_git_repo_manager` is an MCP server that provides a set of tools for managing Git repositories. It allows you to initialize repositories, check status, stage and unstage files, commit changes, view logs, create and switch branches, and inspect commits — all via an MCP interface.

This server integrates Git functionality with the Model Context Protocol (MCP), enabling large language models to interact with Git repositories programmatically.

## Installation

To install dependencies:

1. Ensure Python 3.10+ is installed.
2. Install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

Make sure your `requirements.txt` includes:
```
mcp[cli]
gitpython
```

## Running the Server

To start the server, run the Python script from the command line:
```bash
python mcp_git_repo_manager.py
```

By default, the server will communicate over standard input/output (`stdio`).

## Available Tools

The following tools are available for interacting with Git repositories:

### `git_init`
Initializes a new Git repository in the specified directory.

**Args:**
- `directory`: Path to the directory where the Git repo should be initialized.

---

### `git_status`
Shows the working tree status, including modified, staged, and untracked files.

**Args:**
- `repository_path`: Path to the Git repository.

---

### `git_add`
Adds one or more files to the staging area.

**Args:**
- `repository_path`: Path to the Git repository.
- `files`: List of file paths (absolute or relative) to add.

---

### `git_diff_unstaged`
Displays differences between the working directory and the index (unstaged changes).

**Args:**
- `repository_path`: Path to the Git repository.

---

### `git_diff_staged`
Displays differences between the index and the last commit (staged changes).

**Args:**
- `repository_path`: Path to the Git repository.

---

### `git_diff`
Compares two commits or references and displays the differences.

**Args:**
- `repository_path`: Path to the Git repository.
- `reference1`: First commit or branch (e.g., `HEAD`).
- `reference2`: Second commit or branch (e.g., `HEAD~1`).

---

### `git_commit`
Commits the staged changes with a provided message.

**Args:**
- `repository_path`: Path to the Git repository.
- `message`: Commit message describing the changes.

---

### `git_reset`
Removes one or more files from the staging area.

**Args:**
- `repository_path`: Path to the Git repository.
- `files`: List of file paths (absolute or relative) to unstage.

---

### `git_log`
Displays the commit history of the repository.

**Args:**
- `repository_path`: Path to the Git repository.

---

### `git_create_branch`
Creates a new branch in the repository.

**Args:**
- `repository_path`: Path to the Git repository.
- `branch_name`: Name of the new branch.

---

### `git_checkout`
Switches to a different branch.

**Args:**
- `repository_path`: Path to the Git repository.
- `branch_name`: Name of the branch to switch to.

---

### `git_show`
Displays detailed information about a specific commit.

**Args:**
- `repository_path`: Path to the Git repository.
- `commit_hash`: Hash of the commit to display. If not provided, shows info for the latest commit (`HEAD`).