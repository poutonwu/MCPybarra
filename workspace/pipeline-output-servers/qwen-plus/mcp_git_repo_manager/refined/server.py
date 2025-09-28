import sys
import os
import json
from typing import Dict, List, Any, Optional
from git import Repo, GitCommandError

# 初始化 FastMCP 服务器
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("git_repo_manager")

def validate_repo_path(repo_path: str) -> bool:
    """验证仓库路径是否有效"""
    if not repo_path or not isinstance(repo_path, str):
        return False
    if not os.path.exists(repo_path):
        return False
    return True

def create_error_response(message: str, error_type: str = "GitError") -> Dict[str, Any]:
    """创建标准化的错误响应"""
    return {
        "status": "error",
        "error_type": error_type,
        "message": message
    }

def create_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """创建标准化的成功响应"""
    response = {
        "status": "success",
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response

@mcp.tool()
def write_to_temp_file(file_path: str, content: str, skip_dependent_steps: bool = False) -> str:
    """
    将内容写入指定文件路径。

    Args:
        file_path: 要写入的文件路径 (必填)。
        content: 要写入的内容 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含操作结果的字典，包括成功或失败的状态及消息。

    Raises:
        ValueError: 如果提供的路径无效。
        IOError: 如果文件写入失败。
    """
    try:
        # 验证文件路径有效性
        if not file_path or not isinstance(file_path, str):
            raise ValueError("必须提供有效的文件路径")

        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # 写入文件
        with open(file_path, 'w') as f:
            f.write(content)

        return json.dumps(create_success_response({
            "file_path": file_path,
            "content_length": len(content)
        }, "文件写入成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except IOError as ioe:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ioe)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"文件写入失败: {str(ioe)}", "IOError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_init(repo_path: str) -> str:
    """
    初始化一个新的Git仓库。

    Args:
        repo_path: 新仓库的文件路径 (必填)。

    Returns:
        包含初始化状态的字典，包括仓库路径和初始化成功状态。

    Raises:
        ValueError: 如果提供的路径无效或已存在。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not repo_path or not isinstance(repo_path, str):
            raise ValueError("必须提供有效的仓库路径")

        if os.path.exists(repo_path):
            raise ValueError(f"路径已存在: {repo_path}")

        # 创建新仓库
        os.makedirs(repo_path)
        repo = Repo.init(repo_path)

        return json.dumps(create_success_response({
            "repo_path": repo_path,
            "initialized": True
        }, "仓库初始化成功"))

    except ValueError as ve:
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_status(repo_path: str, skip_dependent_steps: bool = False) -> str:
    """
    获取仓库当前状态。

    Args:
        repo_path: 仓库路径 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含仓库状态信息的字典，如当前分支、修改文件列表等。

    Raises:
        ValueError: 如果提供的路径无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 获取状态信息
        status_info = {
            "repo_path": repo_path,
            "is_dirty": repo.is_dirty(),
            "active_branch": str(repo.active_branch) if repo.active_branch else None,
            "untracked_files": repo.untracked_files,
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "staged_files": [item.a_path for item in repo.index.diff("HEAD")]
        }

        return json.dumps(create_success_response(status_info, "状态信息获取成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_add(repo_path: str, file_path: str, skip_dependent_steps: bool = False) -> str:
    """
    将文件添加到暂存区。

    Args:
        repo_path: 仓库路径 (必填)。
        file_path: 要添加的文件路径 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含操作结果的字典，包括成功或失败的状态及消息。

    Raises:
        ValueError: 如果提供的路径无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        full_file_path = os.path.join(repo_path, file_path)
        if not os.path.exists(full_file_path):
            raise ValueError(f"文件不存在: {file_path}")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 添加文件
        repo.index.add([file_path])

        return json.dumps(create_success_response({
            "repo_path": repo_path,
            "file_path": file_path,
            "added": True
        }, f"文件 {file_path} 添加到暂存区成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_diff_unstaged(repo_path: str, skip_dependent_steps: bool = False) -> str:
    """
    查看未暂存的差异。

    Args:
        repo_path: 仓库路径 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含未暂存差异内容的字符串。

    Raises:
        ValueError: 如果提供的路径无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 获取未暂存的差异
        modified_files = repo.index.diff(None)
        
        diff_output = "未暂存的更改:\n"
        for diff in modified_files:
            diff_output += f"- 修改文件: {diff.a_path}\n"
            
        untracked_files = repo.untracked_files
        if untracked_files:
            diff_output += "- 未跟踪文件:\n"
            for file in untracked_files:
                diff_output += f"  * {file}\n"

        return json.dumps(create_success_response(diff_output, "未暂存差异获取成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_diff_staged(repo_path: str, skip_dependent_steps: bool = False) -> str:
    """
    查看已暂存的差异。

    Args:
        repo_path: 仓库路径 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含已暂存差异内容的字符串。

    Raises:
        ValueError: 如果提供的路径无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 获取已暂存的差异
        staged_diffs = repo.index.diff("HEAD")
        
        diff_output = "已暂存的更改:\n"
        for diff in staged_diffs:
            diff_output += f"- 文件: {diff.a_path or diff.b_path}\n"
            diff_output += f"  变化类型: {diff.change_type}\n"
            
        if not staged_diffs:
            diff_output = "没有找到已暂存的更改。"

        return json.dumps(create_success_response(diff_output, "已暂存差异获取成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_diff(repo_path: str, commit1: str, commit2: str, skip_dependent_steps: bool = False) -> str:
    """
    比较分支或提交。

    Args:
        repo_path: 仓库路径 (必填)。
        commit1: 第一个比较的提交哈希或分支名 (必填)。
        commit2: 第二个比较的提交哈希或分支名 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含两个提交之间差异内容的字符串。

    Raises:
        ValueError: 如果提供的路径或提交信息无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        if not commit1 or not commit2:
            raise ValueError("必须提供两个有效的提交标识")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 获取提交对象
        try:
            commit_obj1 = repo.commit(commit1)
        except Exception:
            raise ValueError(f"无法解析第一个提交标识: {commit1}")

        try:
            commit_obj2 = repo.commit(commit2)
        except Exception:
            raise ValueError(f"无法解析第二个提交标识: {commit2}")

        # 获取差异
        diff_index = commit_obj1.diff(commit_obj2)
        
        diff_output = f"提交 {commit1[:7]} 和 {commit2[:7]} 之间的差异:\n\n"
        for diff in diff_index:
            diff_output += f"- 文件: {diff.a_path or diff.b_path}\n"
            diff_output += f"  变化类型: {diff.change_type}\n"
            
        if not diff_index:
            diff_output = "没有发现两个提交之间的差异。"

        return json.dumps(create_success_response(diff_output, "提交差异获取成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_commit(repo_path: str, message: str, skip_dependent_steps: bool = False) -> str:
    """
    提交更改。

    Args:
        repo_path: 仓库路径 (必填)。
        message: 提交信息 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含提交结果的字典，包括提交哈希和消息。

    Raises:
        ValueError: 如果提供的路径或提交信息无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        if not message or not isinstance(message, str):
            raise ValueError("必须提供有效的提交信息")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 确保有变化可以提交
        if not repo.is_dirty() and not repo.untracked_files:
            raise ValueError("没有需要提交的更改")

        # 提交更改
        new_commit = repo.index.commit(message)

        return json.dumps(create_success_response({
            "repo_path": repo_path,
            "commit_hash": new_commit.hexsha,
            "message": message
        }, "提交成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_reset(repo_path: str, file_path: str, skip_dependent_steps: bool = False) -> str:
    """
    取消暂存文件。

    Args:
        repo_path: 仓库路径 (必填)。
        file_path: 要取消暂存的文件路径 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含操作结果的字典，包括成功或失败的状态及消息。

    Raises:
        ValueError: 如果提供的路径或文件信息无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        if not file_path or not isinstance(file_path, str):
            raise ValueError("必须提供有效的文件路径")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 检查文件是否在暂存区
        staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        if file_path not in staged_files:
            raise ValueError(f"文件 {file_path} 不在暂存区")

        # 取消暂存文件
        repo.index.reset(paths=[file_path])

        return json.dumps(create_success_response({
            "repo_path": repo_path,
            "file_path": file_path,
            "reset": True
        }, f"文件 {file_path} 已从暂存区移除"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_log(repo_path: str, skip_dependent_steps: bool = False) -> str:
    """
    查看提交历史。

    Args:
        repo_path: 仓库路径 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含提交历史的列表，每个条目包含提交哈希、作者、日期和消息。

    Raises:
        ValueError: 如果提供的路径无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 获取提交历史
        commits = list(repo.iter_commits())
        
        commit_history = []
        for commit in commits:
            commit_history.append({
                "hash": commit.hexsha,
                "author": str(commit.author),
                "date": commit.committed_date,
                "message": commit.message.strip()
            })

        return json.dumps(create_success_response({
            "repo_path": repo_path,
            "commit_count": len(commit_history),
            "commits": commit_history
        }, "提交历史获取成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_create_branch(repo_path: str, branch_name: str, skip_dependent_steps: bool = False) -> str:
    """
    创建新分支。

    Args:
        repo_path: 仓库路径 (必填)。
        branch_name: 新分支名称 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含操作结果的字典，包括成功或失败的状态及消息。

    Raises:
        ValueError: 如果提供的路径或分支名称无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        if not branch_name or not isinstance(branch_name, str):
            raise ValueError("必须提供有效的分支名称")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 检查分支是否已经存在
        existing_branches = [str(head) for head in repo.heads]
        if branch_name in existing_branches:
            raise ValueError(f"分支 {branch_name} 已经存在")

        # 创建新分支
        new_branch = repo.create_head(branch_name)

        return json.dumps(create_success_response({
            "repo_path": repo_path,
            "branch_name": branch_name,
            "created": True
        }, f"分支 {branch_name} 创建成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_checkout(repo_path: str, branch_name: str, skip_dependent_steps: bool = False) -> str:
    """
    切换分支。

    Args:
        repo_path: 仓库路径 (必填)。
        branch_name: 要切换到的分支名称 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含操作结果的字典，包括成功或失败的状态及消息。

    Raises:
        ValueError: 如果提供的路径或分支名称无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        if not branch_name or not isinstance(branch_name, str):
            raise ValueError("必须提供有效的分支名称")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 检查目标分支是否存在
        existing_branches = [str(head) for head in repo.heads]
        if branch_name not in existing_branches:
            raise ValueError(f"分支 {branch_name} 不存在")

        # 切换分支
        repo.git.checkout(branch_name)

        return json.dumps(create_success_response({
            "repo_path": repo_path,
            "branch_name": branch_name,
            "checked_out": True
        }, f"成功切换到分支 {branch_name}"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

@mcp.tool()
def git_show(repo_path: str, commit_hash: str, skip_dependent_steps: bool = False) -> str:
    """
    显示提交的详细内容。

    Args:
        repo_path: 仓库路径 (必填)。
        commit_hash: 要显示的提交哈希 (必填)。
        skip_dependent_steps: 如果当前步骤失败，是否跳过依赖步骤 (可选，默认False)。

    Returns:
        包含提交详细信息的字符串，包括元数据和差异内容。

    Raises:
        ValueError: 如果提供的路径或提交哈希无效。
        GitCommandError: 如果Git命令执行失败。
    """
    try:
        # 验证路径有效性
        if not validate_repo_path(repo_path):
            raise ValueError(f"无效的仓库路径: {repo_path}")

        if not commit_hash or not isinstance(commit_hash, str):
            raise ValueError("必须提供有效的提交哈希")

        # 打开现有仓库
        repo = Repo(repo_path)

        # 获取提交对象
        try:
            commit = repo.commit(commit_hash)
        except Exception:
            raise ValueError(f"无法解析提交哈希: {commit_hash}")

        # 构建提交信息输出
        commit_info = f"提交详细信息 - {commit.hexsha}:\n\n"
        commit_info += f"作者: {commit.author}\n"
        commit_info += f"提交者: {commit.committer}\n"
        commit_info += f"提交日期: {commit.committed_datetime}\n"
        commit_info += f"提交信息: {commit.message.strip()}\n\n"
        
        commit_info += "文件更改:\n"
        if commit.parents:
            parent = commit.parents[0]
            for diff in commit.diff(parent):
                commit_info += f"- 文件: {diff.a_path or diff.b_path}\n"
                commit_info += f"  变化类型: {diff.change_type}\n"
        else:
            for diff in commit.diff(None):
                commit_info += f"- 文件: {diff.a_path or diff.b_path}\n"
                commit_info += f"  变化类型: {diff.change_type}\n"
            
        return json.dumps(create_success_response(commit_info, "提交详细信息获取成功"))

    except ValueError as ve:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(ve)}", "DependencySkipped"))
        return json.dumps(create_error_response(str(ve), "ValueError"))
    except GitCommandError as gce:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(gce)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"Git命令执行失败: {str(gce)}", "GitCommandError"))
    except Exception as e:
        if skip_dependent_steps:
            return json.dumps(create_error_response(f"跳过依赖步骤: {str(e)}", "DependencySkipped"))
        return json.dumps(create_error_response(f"未知错误: {str(e)}", "UnexpectedError"))

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()