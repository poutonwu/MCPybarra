import sys
import os
import hashlib
import json
import logging
from typing import Dict, List, Optional, Union, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("text_file_processor")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------- Utility Functions -----------------------------
def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def validate_file_path(file_path: str) -> bool:
    """Validate file path to prevent path traversal attacks."""
    base_dir = os.path.abspath(os.getcwd())
    try:
        file_dir = os.path.abspath(file_path)
        return file_dir.startswith(base_dir)
    except Exception:
        return False

# ----------------------------- Tool Definitions -----------------------------
@mcp.tool()
def get_text_file_contents(file_paths: List[str], start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Read content from one or more text files, optionally limited to a range of lines.
    Returns both content and SHA-256 hashes for concurrency control.

    Args:
        file_paths: A list of file paths to read.
        start_line: Starting line index (inclusive, 0-based).
        end_line: Ending line index (inclusive, 0-based).

    Returns:
        JSON string containing:
        - "contents": Dictionary mapping file paths to their contents (list of lines).
        - "hashes": Dictionary mapping file paths to their SHA-256 hashes.

    Raises:
        ValueError: If invalid file paths or line ranges are provided.

    Example:
        get_text_file_contents(file_paths=["example.txt"], start_line=0, end_line=5)
    """
    try:
        result = {"contents": {}, "hashes": {}}

        if not isinstance(file_paths, list) or len(file_paths) == 0:
            raise ValueError("file_paths must be a non-empty list")
        if start_line is not None and end_line is not None and start_line > end_line:
            raise ValueError("start_line cannot be greater than end_line")

        for file_path in file_paths:
            if not validate_file_path(file_path):
                raise ValueError(f"Invalid file path: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                    actual_start = max(0, start_line) if start_line is not None else 0
                    actual_end = min(len(lines) - 1, end_line) if end_line is not None else len(lines) - 1

                    if actual_start > actual_end:
                        result["contents"][file_path] = []
                    else:
                        result["contents"][file_path] = lines[actual_start:actual_end + 1]

                    result["hashes"][file_path] = calculate_file_hash(file_path)
            except FileNotFoundError:
                raise ValueError(f"File not found: {file_path}")
            except Exception as e:
                raise ValueError(f"Error reading file {file_path}: {str(e)}")

        logging.info("Successfully retrieved file contents")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to retrieve file contents: {str(e)}")
        return json.dumps({"error": "get_text_file_contents failed", "message": str(e)}, ensure_ascii=False)

@mcp.tool()
def create_text_file(file_path: str, content: str) -> str:
    """
    Create a new text file and write initial content.

    Args:
        file_path: Path where the new file should be created.
        content: Initial content to write into the file.

    Returns:
        JSON string containing:
        - "success": Boolean indicating success status.
        - "message": Description of the operation result.
        - "hash": SHA-256 hash of the newly created file.

    Raises:
        ValueError: If invalid parameters or file paths are used.

    Example:
        create_text_file(file_path="new_file.txt", content="This is the content")
    """
    try:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path must be a non-empty string")
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        if not validate_file_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")

        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        file_hash = calculate_file_hash(file_path)
        logging.info(f"Created file {file_path} successfully")
        return json.dumps({"success": True, "message": f"File {file_path} created successfully", "hash": file_hash}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to create file {file_path}: {str(e)}")
        return json.dumps({"success": False, "message": f"Failed to create file: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def append_text_file_contents(file_path: str, content: str) -> str:
    """
    Append content to an existing text file.

    Args:
        file_path: Path to the target file.
        content: Content to append to the file.

    Returns:
        JSON string containing:
        - "success": Boolean indicating success status.
        - "message": Description of the operation result.
        - "new_hash": SHA-256 hash of the modified file.

    Raises:
        ValueError: If file does not exist or invalid parameters are used.

    Example:
        append_text_file_contents(file_path="existing_file.txt", content="\nNew appended content")
    """
    try:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path must be a non-empty string")
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        if not validate_file_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} does not exist")

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)

        new_hash = calculate_file_hash(file_path)
        logging.info(f"Appended content to file {file_path} successfully")
        return json.dumps({"success": True, "message": f"Content appended to {file_path} successfully", "new_hash": new_hash}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to append to file {file_path}: {str(e)}")
        return json.dumps({"success": False, "message": f"Append failed: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def delete_text_file_contents(file_path: str, start_line: int, end_line: int, expected_hash: Optional[str] = None) -> str:
    """
    Delete a range of lines from a text file using concurrency-safe hash validation.

    Args:
        file_path: Path to the file to modify.
        start_line: Start line index (inclusive, 0-based).
        end_line: End line index (inclusive, 0-based).
        expected_hash: Expected SHA-256 hash of the file before modification.

    Returns:
        JSON string containing:
        - "success": Boolean indicating success status.
        - "message": Description of the operation result.
        - "new_hash": SHA-256 hash of the modified file.

    Raises:
        ValueError: If file doesn't exist, line range is invalid, or hash mismatch occurs.

    Example:
        delete_text_file_contents(file_path="example.txt", start_line=2, end_line=5)
    """
    try:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path must be a non-empty string")
        if not isinstance(start_line, int):
            raise ValueError("start_line must be an integer")
        if not isinstance(end_line, int):
            raise ValueError("end_line must be an integer")
        if not validate_file_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} does not exist")

        if expected_hash is not None:
            actual_hash = calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                raise ValueError("File has been modified by another process. Please refresh and try again.")

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        if start_line < 0 or end_line >= len(lines):
            raise ValueError(f"Line range invalid. File has {len(lines)} lines, requested deletion from {start_line} to {end_line}")
        if start_line > end_line:
            raise ValueError("start_line cannot be greater than end_line")

        del lines[start_line:end_line+1]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        new_hash = calculate_file_hash(file_path)
        logging.info(f"Deleted content from {file_path} successfully")
        return json.dumps({"success": True, "message": f"Successfully deleted lines {start_line}-{end_line} from {file_path}", "new_hash": new_hash}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to delete content from {file_path}: {str(e)}")
        return json.dumps({"success": False, "message": f"Delete failed: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def insert_text_file_contents(file_path: str, insert_line: int, content: str, expected_hash: Optional[str] = None) -> str:
    """
    Insert content at a specific position in a text file using concurrency-safe hash validation.

    Args:
        file_path: Path to the file to modify.
        insert_line: Line index where content should be inserted (before this line).
        content: Content to insert.
        expected_hash: Expected SHA-256 hash of the file before modification.

    Returns:
        JSON string containing:
        - "success": Boolean indicating success status.
        - "message": Description of the operation result.
        - "new_hash": SHA-256 hash of the modified file.

    Raises:
        ValueError: If file doesn't exist, line range is invalid, or hash mismatch occurs.

    Example:
        insert_text_file_contents(file_path="example.txt", insert_line=3, content="Inserted content\n")
    """
    try:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path must be a non-empty string")
        if not isinstance(insert_line, int):
            raise ValueError("insert_line must be an integer")
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        if not validate_file_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} does not exist")

        if expected_hash is not None:
            actual_hash = calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                raise ValueError("File has been modified by another process. Please refresh and try again.")

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        if insert_line < 0 or insert_line > len(lines):
            raise ValueError(f"Insert position invalid. File has {len(lines)} lines, requested insertion at {insert_line}")

        content_lines = content.split('\n')
        if content and content[-1] != '\n':
            content_lines.append('')
        inserted_lines = [line + '\n' for line in content_lines[:-1]]
        if content_lines[-1]:
            inserted_lines.append(content_lines[-1])
        lines[insert_line:insert_line] = inserted_lines

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        new_hash = calculate_file_hash(file_path)
        logging.info(f"Inserted content into {file_path} successfully")
        return json.dumps({"success": True, "message": f"Successfully inserted content into {file_path} at line {insert_line}", "new_hash": new_hash}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to insert content into {file_path}: {str(e)}")
        return json.dumps({"success": False, "message": f"Insert failed: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def patch_text_file_contents(file_path: str, line_number: int, old_content: str, new_content: str, expected_hash: Optional[str] = None) -> str:
    """
    Replace content on a specific line in a text file using concurrency-safe hash validation.

    Args:
        file_path: Path to the file to modify.
        line_number: Index of the line to replace.
        old_content: Current content of the line (for verification).
        new_content: New content to set.
        expected_hash: Expected SHA-256 hash of the file before modification.

    Returns:
        JSON string containing:
        - "success": Boolean indicating success status.
        - "message": Description of the operation result.
        - "new_hash": SHA-256 hash of the modified file.

    Raises:
        ValueError: If file doesn't exist, line number is invalid, content mismatch, or hash mismatch occurs.

    Example:
        patch_text_file_contents(file_path="example.txt", line_number=4, old_content="Old content", new_content="New content")
    """
    try:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path must be a non-empty string")
        if not isinstance(line_number, int):
            raise ValueError("line_number must be an integer")
        if not isinstance(old_content, str):
            raise ValueError("old_content must be a string")
        if not isinstance(new_content, str):
            raise ValueError("new_content must be a string")
        if not validate_file_path(file_path):
            raise ValueError(f"Invalid file path: {file_path}")
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} does not exist")

        if expected_hash is not None:
            actual_hash = calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                raise ValueError("File has been modified by another process. Please refresh and try again.")

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        if line_number < 0 or line_number >= len(lines):
            raise ValueError(f"Line number invalid. File has {len(lines)} lines, requested change at {line_number}")

        if lines[line_number].rstrip('\n') != old_content.rstrip('\n'):
            raise ValueError(f"Content mismatch. Expected '{old_content}', got '{lines[line_number].rstrip('\n')}'")

        lines[line_number] = new_content + ('' if lines[line_number].endswith('\n') else '\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        new_hash = calculate_file_hash(file_path)
        logging.info(f"Patched content in {file_path} successfully")
        return json.dumps({"success": True, "message": f"Successfully replaced line {line_number} in {file_path}", "new_hash": new_hash}, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to patch content in {file_path}: {str(e)}")
        return json.dumps({"success": False, "message": f"Patch failed: {str(e)}"}, ensure_ascii=False)

# ----------------------------- Main Execution -----------------------------
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()