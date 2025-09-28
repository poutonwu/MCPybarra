import sys
import os
import hashlib
import json
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional

# Initialize FastMCP server
mcp = FastMCP("mcp_text_file_manipulator")

def _calculate_hash(filepath: str) -> Optional[str]:
    """
    Calculates the SHA-256 hash of a file's content.

    Args:
        filepath: The path to the file.

    Returns:
        The SHA-256 hash as a hex digest, or None if the file doesn't exist.
    """
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
            hasher = hashlib.sha256()
            hasher.update(file_bytes)
            return hasher.hexdigest()
    except FileNotFoundError:
        return None

@mcp.tool()
def get_text_file_contents(
    filepaths: List[str],
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Reads the contents of one or more text files, with optional line range selection.

    Args:
        filepaths: A list of paths to the text files to be read.
                   Example: ["/path/to/file1.txt", "relative/path/to/file2.py"]
        start_line: The 1-indexed starting line for reading. If None, starts from the beginning.
                    Example: 10
        end_line: The 1-indexed ending line for reading. If None, reads to the end.
                  Example: 20

    Returns:
        A dictionary where keys are file paths and values contain the content, hash, or an error message.
        Example:
        {
            "/path/to/file1.txt": {
                "content": ["line 1", "line 2"],
                "hash": "sha256_hash_string"
            },
            "non_existent_file.txt": {
                "error": "File not found."
            }
        }
    """
    results = {}
    for filepath in filepaths:
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")

            file_hash = _calculate_hash(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Adjust for 1-based indexing and slice the lines
            s_line = start_line - 1 if start_line is not None and start_line > 0 else 0
            e_line = end_line if end_line is not None else len(lines)

            content_lines = [line.rstrip('\n') for line in lines[s_line:e_line]]

            results[filepath] = {
                "content": content_lines,
                "hash": file_hash
            }
        except Exception as e:
            results[filepath] = {"error": str(e)}
    return results

@mcp.tool()
def create_text_file(filepath: str, content: str) -> Dict[str, str]:
    """
    Creates a new text file with initial content. Fails if the file already exists.

    Args:
        filepath: The path where the new text file will be created.
                  Example: "new_project/main.py"
        content: The initial string content to write to the file.
                 Example: "print('Hello, World!')"

    Returns:
        A dictionary with a status message indicating success or failure.
        Example:
        {"status": "File 'new_project/main.py' created successfully."}
    """
    try:
        if os.path.exists(filepath):
            return {"status": f"Error: File '{filepath}' already exists."}

        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": f"File '{filepath}' created successfully."}
    except Exception as e:
        return {"status": f"Error creating file '{filepath}': {e}"}

@mcp.tool()
def append_text_file_contents(filepath: str, content: str) -> Dict[str, Optional[str]]:
    """
    Appends new content to the end of an existing text file.

    Args:
        filepath: The path to the text file to be modified.
                  Example: "logs/app.log"
        content: The string content to append to the file.
                 Example: "\\n2023-10-27: User logged in."

    Returns:
        A dictionary with a status message and the new file hash.
        Example:
        {"status": "Content appended successfully.", "new_hash": "new_sha256_hash"}
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content)

        new_hash = _calculate_hash(filepath)
        return {
            "status": f"Content appended successfully to '{filepath}'.",
            "new_hash": new_hash
        }
    except Exception as e:
        return {"status": f"Error appending to file '{filepath}': {e}", "new_hash": None}

@mcp.tool()
def delete_text_file_contents(filepath: str, start_line: int, end_line: int) -> Dict[str, Optional[str]]:
    """
    Deletes a specified range of lines (inclusive) from a text file.

    Args:
        filepath: The path to the text file to be modified.
                  Example: "config.txt"
        start_line: The 1-indexed starting line of the range to delete.
                    Example: 5
        end_line: The 1-indexed ending line of the range to delete.
                  Example: 7

    Returns:
        A dictionary with a status message and the new file hash.
        Example:
        {"status": "Lines 5-7 deleted successfully.", "new_hash": "new_sha256_hash"}
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Validate line numbers
        if not (0 < start_line <= end_line <= len(lines)):
            raise IndexError(f"Invalid line range: {start_line}-{end_line}. File has {len(lines)} lines.")

        # Adjust for 0-based indexing
        del lines[start_line-1:end_line]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        new_hash = _calculate_hash(filepath)
        return {
            "status": f"Lines {start_line}-{end_line} deleted successfully from '{filepath}'.",
            "new_hash": new_hash
        }
    except Exception as e:
        return {"status": f"Error deleting lines from '{filepath}': {e}", "new_hash": None}

@mcp.tool()
def insert_text_file_contents(filepath: str, insert_at_line: int, content: str) -> Dict[str, Optional[str]]:
    """
    Inserts a block of text at a specific line number in a file.

    Args:
        filepath: The path to the text file to be modified.
                  Example: "document.txt"
        insert_at_line: The 1-indexed line number at which to insert the new content.
                        Example: 3
        content: The string content to insert. Newlines create multiple lines.
                 Example: "This is a new line.\\nAnd another one."

    Returns:
        A dictionary with a status message and the new file hash.
        Example:
        {"status": "Content inserted at line 3.", "new_hash": "new_sha256_hash"}
    """
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Validate line number
        if not (0 < insert_at_line <= len(lines) + 1):
             raise IndexError(f"Invalid insert position: {insert_at_line}. File has {len(lines)} lines.")

        # Adjust for 0-based indexing
        insert_index = insert_at_line - 1
        content_lines = [line + '\n' for line in content.splitlines()]

        lines[insert_index:insert_index] = content_lines

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        new_hash = _calculate_hash(filepath)
        return {
            "status": f"Content inserted successfully at line {insert_at_line} in '{filepath}'.",
            "new_hash": new_hash
        }
    except Exception as e:
        return {"status": f"Error inserting content in '{filepath}': {e}", "new_hash": None}

@mcp.tool()
def patch_text_file_contents(
    filepath: str,
    start_line: int,
    end_line: int,
    new_content: str,
    expected_hash: str
) -> Dict[str, Optional[str]]:
    """
    Atomically replaces a range of lines with new content, using a hash for concurrency control.

    Args:
        filepath: The path to the text file to be patched.
                  Example: "source_code.py"
        start_line: The 1-indexed starting line of the content to be replaced.
                    Example: 15
        end_line: The 1-indexed ending line of the content to be replaced.
                  Example: 20
        new_content: The new string content that will replace the specified line range.
                     Example: "def new_function():\\n    pass"
        expected_hash: The SHA-256 hash of the file before this patch operation.
                       Example: "sha256_hash_of_the_original_file"

    Returns:
        A dictionary with a status message and the new hash if successful.
        Example on success:
        {"status": "Patch applied successfully.", "new_hash": "new_sha256_hash"}
        Example on hash mismatch:
        {"status": "Conflict: File has been modified by another process.", "new_hash": null}
    """
    try:
        current_hash = _calculate_hash(filepath)
        if current_hash is None:
            raise FileNotFoundError(f"File not found: {filepath}")

        if current_hash != expected_hash:
            return {
                "status": "Conflict: File has been modified since it was last read. Please re-read the file and try again.",
                "new_hash": None
            }

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Validate line numbers
        if not (0 < start_line <= end_line <= len(lines)):
            raise IndexError(f"Invalid line range: {start_line}-{end_line}. File has {len(lines)} lines.")

        # Adjust for 0-based indexing
        start_index = start_line - 1
        end_index = end_line

        # Prepare new content lines, ensuring they end with a newline
        new_content_lines = [line + '\n' for line in new_content.splitlines()]

        lines[start_index:end_index] = new_content_lines

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        new_hash = _calculate_hash(filepath)
        return {
            "status": f"Patch applied successfully to '{filepath}'.",
            "new_hash": new_hash
        }
    except Exception as e:
        return {"status": f"Error patching file '{filepath}': {e}", "new_hash": None}


if __name__ == "__main__":
    # This basic configuration is for running the server.
    # It ensures that UTF-8 encoding is used for standard output,
    # which is crucial for handling various text file contents.
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()