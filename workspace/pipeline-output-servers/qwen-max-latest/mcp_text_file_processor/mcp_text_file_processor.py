import os
import hashlib
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Union

# Initialize the FastMCP server with a specific name.
mcp = FastMCP("mcp_text_file_processor")

def calculate_file_hash(file_path: str) -> str:
    """
    Helper function to calculate the hash of a file using SHA256.

    Args:
        file_path: Path to the file whose hash needs to be calculated.

    Returns:
        A string containing the hexadecimal representation of the file's hash.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        raise IOError(f"Error reading file {file_path}: {e}")

@mcp.tool()
def get_text_file_contents(file_paths: List[str], start_line: int = None, end_line: int = None) -> Dict[str, Union[List[str], str]]:
    """
    Reads the contents of multiple text files, optionally by line range, and returns the file's hash value for concurrency control.

    Args:
        file_paths: List of paths to the text files.
        start_line: (Optional) The starting line number for partial content retrieval.
        end_line: (Optional) The ending line number for partial content retrieval.

    Returns:
        A dictionary containing the list of lines read from the file(s) and the hash value as a string.

    Example:
        To read lines 5-10 from 'example.txt' and get its hash:
        get_text_file_contents(file_paths=["example.txt"], start_line=5, end_line=10)
    """
    results = {}
    try:
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, 'r', encoding='utf-8-sig') as file:
                lines = file.readlines()
                selected_lines = lines[start_line:end_line] if start_line is not None and end_line is not None else lines
                file_hash = calculate_file_hash(file_path)
                results[file_path] = {'lines': [line.rstrip('\n') for line in selected_lines], 'hash': file_hash}

        return results

    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_text_file(file_path: str, content: str) -> str:
    """
    Creates a new text file and writes initial content to it.

    Args:
        file_path: The path where the new file will be created.
        content: The initial content to write into the new file.

    Returns:
        A message indicating the success or failure of the operation.

    Example:
        To create a file named 'new_file.txt' with content 'Hello World':
        create_text_file(file_path="new_file.txt", content="Hello World")
    """
    try:
        with open(file_path, 'w', encoding='utf-8-sig') as file:
            file.write(content)
        return f"File created successfully at {file_path}"
    except Exception as e:
        return f"Failed to create file: {str(e)}"

@mcp.tool()
def append_text_file_contents(file_path: str, content: str) -> str:
    """
    Appends additional content to an existing text file.

    Args:
        file_path: The path to the existing text file.
        content: The content to append to the file.

    Returns:
        A message indicating the success or failure of the operation.

    Example:
        To append 'More content' to 'existing_file.txt':
        append_text_file_contents(file_path="existing_file.txt", content="More content")
    """
    try:
        with open(file_path, 'a', encoding='utf-8-sig') as file:
            file.write(content)
        return f"Content appended successfully to {file_path}"
    except Exception as e:
        return f"Failed to append content: {str(e)}"

@mcp.tool()
def delete_text_file_contents(file_path: str, start_line: int, end_line: int) -> str:
    """
    Deletes a specific range of content from a text file.

    Args:
        file_path: The path to the text file.
        start_line: The starting line number of the content range to delete.
        end_line: The ending line number of the content range to delete.

    Returns:
        A message indicating the success or failure of the operation.

    Example:
        To delete lines 3-7 from 'data.txt':
        delete_text_file_contents(file_path="data.txt", start_line=3, end_line=7)
    """
    try:
        with open(file_path, 'r+', encoding='utf-8-sig') as file:
            lines = file.readlines()
            del lines[start_line:end_line]
            file.seek(0)
            file.writelines(lines)
            file.truncate()
        return f"Lines {start_line}-{end_line} deleted successfully from {file_path}"
    except Exception as e:
        return f"Failed to delete content: {str(e)}"

@mcp.tool()
def insert_text_file_contents(file_path: str, content: str, position: int) -> str:
    """
    Inserts content into a specified position within a text file.

    Args:
        file_path: The path to the text file.
        content: The content to insert into the file.
        position: The line number before which the content will be inserted.

    Returns:
        A message indicating the success or failure of the operation.

    Example:
        To insert 'Inserted text' before line 5 in 'document.txt':
        insert_text_file_contents(file_path="document.txt", content="Inserted text", position=5)
    """
    try:
        with open(file_path, 'r+', encoding='utf-8-sig') as file:
            lines = file.readlines()
            lines.insert(position, content + '\n')
            file.seek(0)
            file.writelines(lines)
        return f"Content inserted successfully at line {position} in {file_path}"
    except Exception as e:
        return f"Failed to insert content: {str(e)}"

@mcp.tool()
def patch_text_file_contents(file_path: str, content_patches: List[Dict[str, Union[int, str]]], expected_hash: str) -> str:
    """
    Applies precise modifications to a text file with hash verification to prevent conflicts.

    Args:
        file_path: The path to the text file.
        content_patches: A list of dictionaries each containing 'position' (int) and 'new_content' (str).
        expected_hash: The expected hash value of the file for concurrency control.

    Returns:
        A message indicating the success or failure of the operation, including whether the hash matched and changes were applied.

    Example:
        To apply patches to 'config.txt' only if the current hash matches 'abc123':
        patch_text_file_contents(
            file_path="config.txt",
            content_patches=[{'position': 2, 'new_content': 'Updated line'}, {'position': 5, 'new_content': 'Another update'}],
            expected_hash="abc123"
        )
    """
    try:
        current_hash = calculate_file_hash(file_path)
        if current_hash != expected_hash:
            return f"Hash mismatch: Current hash {current_hash} does not match expected hash {expected_hash}. Changes not applied."

        with open(file_path, 'r+', encoding='utf-8-sig') as file:
            lines = file.readlines()
            for patch in content_patches:
                pos = patch.get('position')
                new_content = patch.get('new_content')
                if pos is None or new_content is None:
                    return f"Invalid patch data. Missing 'position' or 'new_content'. No changes applied."
                if 0 <= pos < len(lines):
                    lines[pos] = new_content + '\n'
                else:
                    return f"Invalid position {pos} in patch. No changes applied."

            file.seek(0)
            file.writelines(lines)
            file.truncate()
        return f"Patches applied successfully to {file_path}"
    except Exception as e:
        return f"Failed to apply patches: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server on the standard I/O transport.
    mcp.run()