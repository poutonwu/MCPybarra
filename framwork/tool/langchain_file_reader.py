import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type, Any, List, Union
from framwork.logger import logger

# Determine the project root relative to this file's location
# framwork/tool/langchain_file_reader.py -> framwork/ -> project_root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_TEST_FILES_DIR = PROJECT_ROOT / "testSystem" / "testFiles"

# 定义LangChain工具的输入schema
class LangchainFileReaderInput(BaseModel):
    list_files: bool = Field(default=True, description="设置为True时，列出允许的目录下的所有文件路径。只能为True。")

class LangchainFileReaderTool(BaseTool):
    name: str = "read_file_for_test"
    description: str = ""
    args_schema: Type[BaseModel] = LangchainFileReaderInput
    restricted_root: Path = DEFAULT_TEST_FILES_DIR

    def __init__(self, **data: Any):
        super().__init__(**data)
        # Load the restricted directory path from environment variables, with a sensible default
        restricted_path_str = os.getenv("TEST_FILES_DIR", str(DEFAULT_TEST_FILES_DIR))
        self.restricted_root = Path(restricted_path_str).resolve()
        # Ensure the directory exists
        if not self.restricted_root.exists() or not self.restricted_root.is_dir():
            logger.warning(f"The specified TEST_FILES_DIR '{self.restricted_root}' does not exist or is not a directory. The tool may fail.")
        # 动态更新描述
        self.description = (f"仅支持列出受限目录下的所有文件路径。此工具仅限于访问 '{self.restricted_root}' 目录。" )

    def _list_files(self) -> Union[List[str], str]:
        """列出受限目录下的所有文件的完整路径。"""
        try:
            file_paths = []
            for root, _, files in os.walk(self.restricted_root):
                for file in files:
                    file_path = Path(root) / file
                    file_paths.append(str(file_path))
            if not file_paths:
                return f"受限目录'{self.restricted_root}'中没有找到文件。"
            return file_paths
        except Exception as e:
            error_msg = f"列出文件时出错: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    def _run(self, list_files: bool = True, **kwargs: Any) -> Union[List[str], str]:
        """同步执行，仅支持列出文件操作。"""
        return self._list_files()

    async def _arun(self, list_files: bool = True, **kwargs: Any) -> Union[List[str], str]:
        """异步执行，仅支持列出文件操作。"""
        return self._list_files()