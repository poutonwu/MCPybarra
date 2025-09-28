import os
import json
import hashlib
from itertools import islice
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp_text_file_manager")
def resolve_path(file_path: str) -> str:
    """
    Resolve placeholder variables in file paths.
    
    Currently supports:
    - $temp_dir: System's temporary directory
    - $cwd: Current working directory
    """
    if not file_path:
        return file_path
        
    # Replace $temp_dir with actual temporary directory
    if file_path.startswith("$temp_dir"):
        temp_dir = os.getenv('TEMP', os.getenv('TMPDIR', '/tmp'))
        return file_path.replace("$temp_dir", temp_dir, 1)
        
    # Replace $cwd with current working directory
    if file_path.startswith("$cwd"):
        cwd = os.getcwd()
        return file_path.replace("$cwd", cwd, 1)
        
    return file_path

def ensure_directory_exists(file_path: str):
    """
    Ensure that the directory for the given file path exists.
    If not, create it.
    """
    directory = os.path.dirname(resolve_path(file_path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

@mcp.tool()
def get_text_file_contents(file_path: str, start_line: int = None, end_line: int = None) -> str:
    """
    Reads the content of a text file within a specified line range and returns the file's hash for concurrency control.

    Args:
        file_path (str): Path to the text file.
        start_line (int, optional): The starting line number (inclusive). Defaults to None.
        end_line (int, optional): The ending line number (inclusive). Defaults to None.

    Returns:
        str: JSON string containing 'content' and 'hash'.

    Example:
        get_text_file_contents("example.txt", start_line=1, end_line=5)
    """
    try:
        resolved_path = resolve_path(file_path)
        
        if not os.path.exists(resolved_path):
            return json.dumps({"error": f"File does not exist: {file_path}"})

        with open(resolved_path, "r", encoding="utf-8") as file:
            if start_line is not None and end_line is not None:
                lines = list(islice(file, start_line - 1, end_line))
            else:
                lines = file.readlines()
                
            content = "".join(lines)

        with open(resolved_path, "rb") as file:
            file_hash = hashlib.sha256(file.read()).hexdigest()

        return json.dumps({"content": content, "hash": file_hash})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def create_text_file(file_path: str, content: str) -> str:
    """
    Creates a new text file and writes the provided content to it.

    Args:
        file_path (str): Path where the new file should be created.
        content (str): The content to write to the new file.

    Returns:
        str: Success message.

    Example:
        create_text_file("new_file.txt", "Hello, World!")
    """
    try:
        resolved_path = resolve_path(file_path)
        ensure_directory_exists(resolved_path)
        
        with open(resolved_path, "w", encoding="utf-8") as file:
            file.write(content)
        return json.dumps({"message": "File created successfully."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def append_text_file_contents(file_path: str, content: str) -> str:
    """
    Appends content to an existing text file.

    Args:
        file_path (str): Path to the existing text file.
        content (str): The content to append to the file.

    Returns:
        str: Success message.

    Example:
        append_text_file_contents("example.txt", "Additional text.")
    """
    try:
        resolved_path = resolve_path(file_path)
        ensure_directory_exists(resolved_path)
        
        with open(resolved_path, "a", encoding="utf-8") as file:
            file.write(content + "\n")
        return json.dumps({"message": "Content appended successfully."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def delete_text_file_contents(file_path: str, start_line: int, end_line: int) -> str:
    """
    Deletes content within a specified line range in a text file.

    Args:
        file_path (str): Path to the text file.
        start_line (int): The starting line number (inclusive).
        end_line (int): The ending line number (inclusive).

    Returns:
        str: Success message.

    Example:
        delete_text_file_contents("example.txt", start_line=2, end_line=4)
    """
    try:
        resolved_path = resolve_path(file_path)
        
        if not os.path.exists(resolved_path):
            return json.dumps({"error": f"File does not exist: {file_path}"})

        with open(resolved_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            return json.dumps({"error": f"Invalid line range: start_line={start_line}, end_line={end_line}. File has {len(lines)} lines."})

        with open(resolved_path, "w", encoding="utf-8") as file:
            file.writelines(lines[:start_line - 1] + lines[end_line:])

        return json.dumps({"message": "Specified lines deleted successfully."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def insert_text_file_contents(file_path: str, line_number: int, content: str) -> str:
    """
    Inserts content at a specified position in a text file.

    Args:
        file_path (str): Path to the text file.
        line_number (int): The line number before which the content will be inserted.
        content (str): The content to insert into the file.

    Returns:
        str: Success message.

    Example:
        insert_text_file_contents("example.txt", line_number=3, content="Inserted text.")
    """
    try:
        resolved_path = resolve_path(file_path)
        ensure_directory_exists(resolved_path)
        
        with open(resolved_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if line_number < 1 or line_number > len(lines) + 1:
            return json.dumps({"error": f"Invalid line number: {line_number}. File has {len(lines)} lines."})

        lines.insert(line_number - 1, content + "\n")

        with open(resolved_path, "w", encoding="utf-8") as file:
            file.writelines(lines)

        return json.dumps({"message": "Content inserted successfully."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def patch_text_file_contents(file_path: str, patch_data: list, expected_hash: str) -> str:
    """
    Applies precise edits to a text file based on provided changes. Validates the file hash to avoid concurrency conflicts.

    Args:
        file_path (str): Path to the text file.
        patch_data (list of dict): A list of changes, each specifying:
            - start_line (int): Start line for the patch.
            - end_line (int): End line for the patch.
            - new_content (str): New content to replace the specified range.
        expected_hash (str): Expected SHA256 hash of the file to confirm no concurrent modifications.

    Returns:
        str: Success message if the patch is applied successfully, or error message if the hash does not match.

    Example:
        patch_text_file_contents(
            "example.txt",
            patch_data=[{"start_line": 2, "end_line": 3, "new_content": "Patched content."}],
            expected_hash="abc123"
        )
    """
    try:
        resolved_path = resolve_path(file_path)
        
        if not os.path.exists(resolved_path):
            return json.dumps({"error": f"File does not exist: {file_path}"})

        with open(resolved_path, "rb") as file:
            current_hash = hashlib.sha256(file.read()).hexdigest()

        if expected_hash and current_hash != expected_hash:
            return json.dumps({"error": f"File hash mismatch. Patch aborted. Current hash: {current_hash}"})

        with open(resolved_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for patch in patch_data:
            start_line = patch["start_line"]
            end_line = patch["end_line"]
            new_content = patch["new_content"]
            
            if start_line < 1 or end_line < start_line:
                return json.dumps({"error": f"Invalid line range: start_line={start_line}, end_line={end_line}. Lines must be >= 1 and end_line >= start_line"})

            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            
            lines[start_idx:end_idx] = [new_content + "\n"]

        with open(resolved_path, "w", encoding="utf-8") as file:
            file.writelines(lines)

        with open(resolved_path, "rb") as file:
            new_hash = hashlib.sha256(file.read()).hexdigest()

        return json.dumps({"message": "Patch applied successfully.", "new_hash": new_hash})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    mcp.run(transport="stdio")