### Server Overview

This document outlines the implementation plan for an MCP (Model Context Protocol) server designed for automated text file processing. The server will provide a suite of tools to read, create, and modify text files on the local filesystem. Key features include the ability to read specific line ranges, perform atomic updates using file content hashes for concurrency control, and execute precise content manipulation operations such as appending, deleting, inserting, and patching.

### File to be Generated

*   `mcp_file_processing_server.py`

### Dependencies

*   No third-party libraries are required. The implementation will rely on Python's standard libraries, specifically `os` and `hashlib`.

### MCP Tools Plan

---

#### **Tool 1: `get_text_file_contents`**

*   **Function Name**: `get_text_file_contents`
*   **Description**: Reads the contents of one or more text files. It can read the entire file or a specified range of lines. For each file, it returns the content along with a SHA-256 hash of the entire file's content, which can be used for optimistic concurrency control in subsequent operations.
*   **Parameters**:
    *   `filepaths: list[str]`: A list of strings, where each string is the absolute or relative path to a text file.
    *   `start_line: int | None = None`: The starting line number for reading (1-indexed, inclusive). If `None`, reading starts from the beginning of the file.
    *   `end_line: int | None = None`: The ending line number for reading (1-indexed, inclusive). If `None`, reading continues to the end of the file.
*   **Return Value**:
    *   `dict`: A dictionary where keys are the file paths provided in the request. The value for each key is another dictionary containing:
        *   `content: list[str]`: A list of strings, where each string is a line from the specified range of the file.
        *   `hash: str`: The SHA-256 hash of the entire file's content.
        *   `error: str` (optional): If an error occurs (e.g., file not found), this key will hold an error message.

---

#### **Tool 2: `create_text_file`**

*   **Function Name**: `create_text_file`
*   **Description**: Creates a new text file at a specified path and writes initial content to it. If the file already exists, the operation will fail to prevent accidental overwrites.
*   **Parameters**:
    *   `filepath: str`: The path where the new text file will be created.
    *   `content: str`: The initial string content to be written to the new file.
*   **Return Value**:
    *   `dict`: A dictionary containing:
        *   `status: str`: A message indicating success (e.g., "File 'path/to/file.txt' created successfully.") or failure (e.g., "Error: File 'path/to/file.txt' already exists.").

---

#### **Tool 3: `append_text_file_contents`**

*   **Function Name**: `append_text_file_contents`
*   **Description**: Appends new content to the end of an existing text file.
*   **Parameters**:
    *   `filepath: str`: The path to the text file to be modified.
    *   `content: str`: The string content to append to the file.
*   **Return Value**:
    *   `dict`: A dictionary containing:
        *   `status: str`: A message indicating the result of the append operation.
        *   `new_hash: str`: The new SHA-256 hash of the file after the content has been appended.

---

#### **Tool 4: `delete_text_file_contents`**

*   **Function Name**: `delete_text_file_contents`
*   **Description**: Deletes a specified range of lines from a text file.
*   **Parameters**:
    *   `filepath: str`: The path to the text file to be modified.
    *   `start_line: int`: The starting line number of the range to delete (1-indexed, inclusive).
    *   `end_line: int`: The ending line number of the range to delete (1-indexed, inclusive).
*   **Return Value**:
    *   `dict`: A dictionary containing:
        *   `status: str`: A message indicating the result of the deletion.
        *   `new_hash: str`: The new SHA-256 hash of the file after the lines have been deleted.

---

#### **Tool 5: `insert_text_file_contents`**

*   **Function Name**: `insert_text_file_contents`
*   **Description**: Inserts a block of text at a specific line number in an existing text file. Existing content from that line onward is shifted down.
*   **Parameters**:
    *   `filepath: str`: The path to the text file to be modified.
    *   `insert_at_line: int`: The line number (1-indexed) at which to insert the new content.
    *   `content: str`: The string content to insert. Each newline character in the string will be treated as a new line.
*   **Return Value**:
    *   `dict`: A dictionary containing:
        *   `status: str`: A message indicating the result of the insertion.
        *   `new_hash: str`: The new SHA-256 hash of the file after the content has been inserted.

---

#### **Tool 6: `patch_text_file_contents`**

*   **Function Name**: `patch_text_file_contents`
*   **Description**: Atomically replaces a specific range of lines with new content. This operation requires a file hash to ensure the file has not been modified by another process since it was last read, preventing race conditions.
*   **Parameters**:
    *   `filepath: str`: The path to the text file to be patched.
    *   `start_line: int`: The starting line number of the content to be replaced (1-indexed, inclusive).
    *   `end_line: int`: The ending line number of the content to be replaced (1-indexed, inclusive).
    *   `new_content: str`: The new string content that will replace the specified line range.
    *   `expected_hash: str`: The SHA-256 hash of the file *before* this patch operation. The server will verify this hash against the current file's hash before proceeding.
*   **Return Value**:
    *   `dict`: A dictionary containing:
        *   `status: str`: A message indicating success, a hash mismatch conflict, or another error.
        *   `new_hash: str | None`: If the patch is successful, this will be the new SHA-256 hash of the modified file. If it fails, this will be `None`.