# mcp_git_repo_manager

## Overview
`mcp_git_repo_manager` 是一个 MCP (Model Context Protocol) 服务器，提供与 Git 仓库交互的工具。它允许大语言模型 (LLM) 执行常见的 Git 操作，如初始化仓库、查看状态、暂存文件、提交更改、创建和切换分支等。

## Installation
1. 确保你已安装 Python 3.10 或更高版本。
2. 安装 MCP SDK:
   ```bash
   pip install mcp[cli]
   ```
3. 安装 GitPython:
   ```bash
   pip install gitpython
   ```
4. 安装项目依赖（假设你有一个 `requirements.txt` 文件）:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server
要启动服务器，请运行以下命令：
```bash
python mcp_git_repo_manager.py
```
确保将 `mcp_git_repo_manager.py` 替换为实际保存服务器代码的文件名。

## Available Tools
以下是此 MCP 服务器支持的工具及其功能：

### 1. `write_to_temp_file`
将内容写入指定路径的文件中。可用于创建或更新任意文件。

### 2. `git_init`
在指定路径上初始化一个新的 Git 仓库。

### 3. `git_status`
获取仓库的当前状态，包括活动分支、修改文件、未跟踪文件等信息。

### 4. `git_add`
将指定文件添加到 Git 的暂存区。

### 5. `git_diff_unstaged`
显示未暂存的更改，包括修改的文件和未跟踪的文件。

### 6. `git_diff_staged`
显示已暂存的更改，包括即将提交的文件及其变化类型。

### 7. `git_diff`
比较两个提交或分支之间的差异，并列出发生变化的文件。

### 8. `git_commit`
提交暂存的更改，并附带提交信息。

### 9. `git_reset`
从暂存区移除指定的文件。

### 10. `git_log`
查看仓库的提交历史，包括每次提交的哈希值、作者、日期和消息。

### 11. `git_create_branch`
在仓库中创建一个新的分支。

### 12. `git_checkout`
切换到指定的 Git 分支。

### 13. `git_show`
显示特定提交的详细信息，包括作者、提交者、提交时间、提交信息和文件更改内容。