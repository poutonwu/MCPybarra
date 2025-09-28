# MCP Tools Plan

| Function Name | Description | Parameters | Return Value |
| :--- | :--- | :--- | :--- |
| `git_init` | 初始化一个新的Git仓库。 | - `repo_path` (str): 要初始化为Git仓库的本地目录路径。 | (str) 一条确认消息，例如 "Repository initialized at /path/to/repo"。 |
| `git_status` | 查看指定仓库的工作区和暂存区状态。 | - `repo_path` (str): Git仓库的本地路径。 | (str) Git仓库的当前状态文本。 |
| `git_add` | 将文件更改添加到暂存区。 | - `repo_path` (str): Git仓库的本地路径。<br>- `file_path` (str): 要添加到暂存区的文件路径。使用 `.` 来添加所有更改。 | (str) 一条确认消息，例如 "Added 'file.txt' to the staging area."。 |
| `git_diff_unstaged` | 查看工作区中尚未暂存的更改。 | - `repo_path` (str): Git仓库的本地路径。 | (str) 未暂存更改的差异文本。 |
| `git_diff_staged` | 查看已暂存但尚未提交的更改。 | - `repo_path` (str): Git仓库的本地路径。 | (str) 已暂存更改的差异文本。 |
| `git_diff` | 比较两个分支或提交之间的差异。 | - `repo_path` (str): Git仓库的本地路径。<br>- `base` (str): 比较的基础分支或提交哈希。<br>- `compare` (str, optional): 与基础进行比较的分支或提交哈希。如果未提供，则与工作区比较。 | (str) 两个引用之间的差异文本。 |
| `git_commit` | 提交暂存区的更改。 | - `repo_path` (str): Git仓库的本地路径。<br>- `message` (str): 本次提交的说明信息。 | (str) 新提交的哈希值。 |
| `git_reset` | 从暂存区取消暂存文件。 | - `repo_path` (str): Git仓库的本地路径。<br>- `file_path` (str, optional): 要从暂存区移除的特定文件路径。如果未提供，则取消暂存所有文件。 | (str) 一条确认消息，例如 "Unstaged 'file.txt'."。 |
| `git_log` | 查看仓库的提交历史。 | - `repo_path` (str): Git仓库的本地路径。<br>- `max_count` (int, optional): 要显示的最大日志条目数，默认为10。 | (str) 格式化的提交历史日志。 |
| `git_create_branch` | 在仓库中创建一个新分支。 | - `repo_path` (str): Git仓库的本地路径。<br>- `branch_name` (str): 要创建的新分支的名称。 | (str) 一条确认消息，例如 "Branch 'feature/new-branch' created."。 |
| `git_checkout` | 切换到指定的分支。 | - `repo_path` (str): Git仓库的本地路径。<br>- `branch_name` (str): 要切换到的分支的名称。 | (str) 一条确认消息，例如 "Switched to branch 'main'."。 |
| `git_show` | 显示特定提交的详细信息。 | - `repo_path` (str): Git仓库的本地路径。<br>- `commit_hash` (str): 要查看详情的提交哈希值。 | (str) 指定提交的详细信息，包括作者、日期和更改内容。 |

# Server Overview

该MCP服务器旨在提供一套用于自动化Git仓库管理的工具。它封装了核心的Git命令，允许用户通过MCP协议以编程方式执行Git操作，如初始化仓库、管理文件（添加、提交、查看差异）、浏览历史记录以及操作分支。所有操作都在服务器本地文件系统上执行。

# File to be Generated

mcp_git_server.py

# Dependencies

- `mcp`
- `GitPython`