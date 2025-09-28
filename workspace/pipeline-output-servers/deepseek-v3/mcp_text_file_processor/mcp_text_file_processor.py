import sys
import os
import hashlib
from typing import Dict, List, Tuple, Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_text_file_processor")

@mcp.tool()
def get_text_file_contents(file_paths: List[str], line_range: Optional[Tuple[int, int]] = None) -> Dict[str, Dict[str, str]]:
    """
    Reads the contents of multiple text files, optionally by line range, and returns the file contents along with a hash value for concurrency control.

    Args:
        file_paths: Paths to the text files to read.
        line_range: The start and end line numbers to read (inclusive). If not provided, reads the entire file.

    Returns:
        A dictionary where keys are file paths and values are dictionaries containing:
            content: The content of the file or the specified line range.
            hash: A hash value of the file content for concurrency control.

    Raises:
        ValueError: If any file path is invalid or the line range is incorrect.
        FileNotFoundError: If any file does not exist.
    """
    result = {}
    for file_path in file_paths:
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                lines = file.readlines()
                
                if line_range:
                    start, end = line_range
                    if start < 1 or end > len(lines) or start > end:
                        raise ValueError(f"Invalid line range: {line_range}")
                    content = ''.join(lines[start-1:end])
                else:
                    content = ''.join(lines)
                
                file_hash = hashlib.sha256(content.encode()).hexdigest()
                result[file_path] = {
                    "content": content,
                    "hash": file_hash
                }
        except Exception as e:
            raise ValueError(f"Error processing file {file_path}: {str(e)}")
    return result

@mcp.tool()
def create_text_file(file_path: str, content: str) -> Dict[str, str]:
    """
    Creates a new text file with the specified content.

    Args:
        file_path: The path where the new text file will be created.
        content: The content to write to the new file.

    Returns:
        A dictionary with:
            success: Indicates whether the file was created successfully.
            message: A status message (e.g., "File created successfully" or an error message).

    Raises:
        ValueError: If the file path is invalid or content is empty.
    """
    try:
        if not content:
            raise ValueError("Content cannot be empty")
        
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.write(content)
        
        return {
            "success": True,
            "message": "File created successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating file: {str(e)}"
        }

@mcp.tool()
def append_text_file_contents(file_path: str, content: str) -> Dict[str, str]:
    """
    Appends content to an existing text file.

    Args:
        file_path: The path to the text file.
        content: The content to append to the file.

    Returns:
        A dictionary with:
            success: Indicates whether the content was appended successfully.
            message: A status message.

    Raises:
        ValueError: If the file does not exist or content is empty.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not content:
            raise ValueError("Content cannot be empty")
        
        with open(file_path, 'a', encoding='utf-8-sig') as file:
            file.write(content)
        
        return {
            "success": True,
            "message": "Content appended successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error appending content: {str(e)}"
        }

@mcp.tool()
def delete_text_file_contents(file_path: str, line_range: Tuple[int, int]) -> Dict[str, str]:
    """
    Deletes a specific range of lines from a text file.

    Args:
        file_path: The path to the text file.
        line_range: The start and end line numbers to delete (inclusive).

    Returns:
        A dictionary with:
            success: Indicates whether the lines were deleted successfully.
            message: A status message.

    Raises:
        ValueError: If the file does not exist or the line range is invalid.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
        
        start, end = line_range
        if start < 1 or end > len(lines) or start > end:
            raise ValueError(f"Invalid line range: {line_range}")
        
        del lines[start-1:end]
        
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.writelines(lines)
        
        return {
            "success": True,
            "message": "Lines deleted successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting lines: {str(e)}"
        }

@mcp.tool()
def insert_text_file_contents(file_path: str, line_number: int, content: str) -> Dict[str, str]:
    """
    Inserts content into a text file at a specified line position.

    Args:
        file_path: The path to the text file.
        line_number: The line number where the content will be inserted.
        content: The content to insert.

    Returns:
        A dictionary with:
            success: Indicates whether the content was inserted successfully.
            message: A status message.

    Raises:
        ValueError: If the file does not exist or the line number is invalid.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if line_number < 1:
            raise ValueError("Line number must be at least 1")
        if not content:
            raise ValueError("Content cannot be empty")
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
        
        if line_number > len(lines) + 1:
            raise ValueError(f"Line number {line_number} is out of range")
        
        lines.insert(line_number - 1, content + '\n')
        
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.writelines(lines)
        
        return {
            "success": True,
            "message": "Content inserted successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error inserting content: {str(e)}"
        }

@mcp.tool()
def patch_text_file_contents(file_path: str, modifications: List[Dict], expected_hash: str) -> Dict[str, str]:
    """
    Applies precise modifications to a text file, with hash validation to avoid conflicts.

    Args:
        file_path: The path to the text file.
        modifications: A list of modifications, where each modification is a dictionary with:
            action: The action to perform (e.g., "insert", "delete", "replace").
            line_number: The line number to modify.
            content: The content to insert or replace (if applicable).
        expected_hash: The expected hash value of the file content before modifications.

    Returns:
        A dictionary with:
            success: Indicates whether the modifications were applied successfully.
            message: A status message.
            new_hash: The new hash value of the file content after modifications.

    Raises:
        ValueError: If the file does not exist, the hash does not match, or modifications are invalid.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            content = file.read()
        
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        if current_hash != expected_hash:
            raise ValueError(f"Hash mismatch. Expected: {expected_hash}, Actual: {current_hash}")
        
        lines = content.splitlines(keepends=True)
        
        for mod in modifications:
            action = mod.get("action")
            line_number = mod.get("line_number")
            mod_content = mod.get("content", "")
            
            if action == "insert":
                if line_number < 1 or line_number > len(lines) + 1:
                    raise ValueError(f"Invalid line number for insert: {line_number}")
                lines.insert(line_number - 1, mod_content + '\n')
            elif action == "delete":
                if line_number < 1 or line_number > len(lines):
                    raise ValueError(f"Invalid line number for delete: {line_number}")
                del lines[line_number - 1]
            elif action == "replace":
                if line_number < 1 or line_number > len(lines):
                    raise ValueError(f"Invalid line number for replace: {line_number}")
                lines[line_number - 1] = mod_content + '\n'
            else:
                raise ValueError(f"Invalid action: {action}")
        
        new_content = ''.join(lines)
        new_hash = hashlib.sha256(new_content.encode()).hexdigest()
        
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.write(new_content)
        
        return {
            "success": True,
            "message": "Modifications applied successfully",
            "new_hash": new_hash
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error applying modifications: {str(e)}",
            "new_hash": ""
        }

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()