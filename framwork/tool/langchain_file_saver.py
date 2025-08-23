import os
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type, Any
import aiofiles

from framwork.logger import logger

# Define the input schema for the LangChain tool
class LangchainFileSaverInput(BaseModel):
    content: str = Field(description="(required) The content to save to the file.")
    file_path: str = Field(description=("(required) The path where the file should be saved relative to the project workspace, "
                                         "including filename and extension. Example: 'output-servers/my_server.py' or "
                                         "'server-test-report/report.json'"))
    mode: str = Field(default="w", description="(optional) The file opening mode. Default is 'w' for write. Use 'a' for append.")

class LangchainFileSaverTool(BaseTool):
    name: str = "save_content_to_file" # Distinct name for LangChain tool
    description: str = ("Save string content to a local file at a specified path relative to the project workspace ('workspace/'). "
                        "Use this tool ONLY when you need to save text, code, reports, or other generated string content to a file. "
                        "Provide the file path relative to the 'workspace' directory (e.g., 'output-servers/my_code.py' or 'server-test-report/report.json'). "
                        "Do NOT use absolute paths.")
    args_schema: Type[BaseModel] = LangchainFileSaverInput
    # Defines the root for relative paths used by this tool
    workspace_root: Path = Path("workspace") 

    def _validate_path(self, file_path_str: str) -> tuple[Path | None, str | None]:
        """Validates the path and returns the full path or an error message."""
        target_path = Path(file_path_str)
        
        # Basic security checks
        if target_path.is_absolute() or ".." in target_path.parts:
            error_msg = f"Error: Invalid file path '{file_path_str}'. Only relative paths within the '{self.workspace_root}' directory are allowed, and must not contain '..'."
            logger.error(error_msg)
            return None, error_msg
            
        full_path = self.workspace_root.resolve() / target_path
        
        # Optional: Check if it's truly within the intended workspace root after resolving
        try:
            full_path.relative_to(self.workspace_root.resolve())
        except ValueError:
            error_msg = f"Error: Path '{file_path_str}' resolves outside the workspace directory '{self.workspace_root.resolve()}'."
            logger.error(error_msg)
            return None, error_msg
            
        return full_path, None

    def _run(self, content: str, file_path: str, mode: str = "w", **kwargs: Any) -> str:
        """Synchronously save content to a file."""
        logger.info(f"Attempting to save file synchronously via tool: {file_path}")
        full_path, error = self._validate_path(file_path)
        if error:
            return error
            
        try:
            # Ensure the directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write directly to the file (synchronously)
            with open(full_path, mode, encoding="utf-8") as file:
                file.write(content)

            relative_path_str = str(self.workspace_root / Path(file_path).relative_to(Path(file_path).anchor))
            success_msg = f"Content successfully saved to {relative_path_str}"
            logger.info(success_msg)
            return success_msg
        except Exception as e:
            error_msg = f"Error saving file '{file_path}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    async def _arun(self, content: str, file_path: str, mode: str = "w", **kwargs: Any) -> str:
        """Asynchronously save content to a file."""
        logger.info(f"Attempting to save file asynchronously via tool: {file_path}")
        full_path, error = self._validate_path(file_path)
        if error:
            return error
            
        try:
            # Ensure the directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write asynchronously to the file
            async with aiofiles.open(full_path, mode, encoding="utf-8") as file:
                await file.write(content)

            relative_path_str = str(self.workspace_root / Path(file_path).relative_to(Path(file_path).anchor))
            success_msg = f"Content successfully saved to {relative_path_str}"
            logger.info(success_msg)
            return success_msg
        except Exception as e:
            error_msg = f"Error saving file '{file_path}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg 