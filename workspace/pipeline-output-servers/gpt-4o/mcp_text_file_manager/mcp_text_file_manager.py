import os
import json
import hashlib
from itertools import islice
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("mcp_text_file_manager")

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
        with open(file_path, "r", encoding="utf-8-sig") as file:
            lines = list(islice(file, start_line - 1 if start_line else None, end_line))
            content = "".join(lines)

        with open(file_path, "rb") as file:
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
        with open(file_path, "w", encoding="utf-8-sig") as file:
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
        with open(file_path, "a", encoding="utf-8-sig") as file:
            file.write(content)
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
        with open(file_path, "r", encoding="utf-8-sig") as file:
            lines = file.readlines()

        with open(file_path, "w", encoding="utf-8-sig") as file:
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
        with open(file_path, "r", encoding="utf-8-sig") as file:
            lines = file.readlines()

        lines.insert(line_number - 1, content + "\n")

        with open(file_path, "w", encoding="utf-8-sig") as file:
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
        with open(file_path, "rb") as file:
            current_hash = hashlib.sha256(file.read()).hexdigest()

        if current_hash != expected_hash:
            return json.dumps({"error": "File hash mismatch. Patch aborted."})

        with open(file_path, "r", encoding="utf-8-sig") as file:
            lines = file.readlines()

        for patch in patch_data:
            lines[patch["start_line"] - 1:patch["end_line"]] = [patch["new_content"] + "\n"]

        with open(file_path, "w", encoding="utf-8-sig") as file:
            file.writelines(lines)

        return json.dumps({"message": "Patch applied successfully."})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    mcp.run(transport="stdio")