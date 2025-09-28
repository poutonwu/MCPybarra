# mcp_text_file_manipulator

A Model Context Protocol (MCP) server that provides a suite of tools for text file manipulation, including reading, creating, appending, deleting, inserting, and patching text files.

---

## Overview

The `mcp_text_file_manipulator` server enables seamless integration between large language models (LLMs) and common text file operations. It allows clients to perform precise and atomic manipulations on text files using a set of well-documented tools. This is particularly useful for code editing, log management, configuration updates, and general-purpose text file handling.

---

## Installation

1. Ensure Python 3.10 or higher is installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` yet, you can install the necessary packages directly:

```bash
pip install mcp
```

---

## Running the Server

To start the MCP server, run the Python script from the command line:

```bash
python mcp_text_file_manipulator.py
```

This will launch the server using the default `stdio` transport protocol.

---

## Available Tools

Below is a list of available tools provided by the server:

### `get_text_file_contents`

**Description:** Reads the contents of one or more text files, optionally within a specified line range.

**Args:**
- `filepaths`: List of file paths to read.
- `start_line`: Optional 1-indexed starting line.
- `end_line`: Optional 1-indexed ending line.

**Returns:** A dictionary containing the content lines and SHA-256 hash for each file, or an error message if the file is not found.

---

### `create_text_file`

**Description:** Creates a new text file with the given content. Fails if the file already exists.

**Args:**
- `filepath`: Path where the new file should be created.
- `content`: Initial string content to write into the file.

**Returns:** A status message indicating success or failure.

---

### `append_text_file_contents`

**Description:** Appends new content to the end of an existing text file.

**Args:**
- `filepath`: Path to the file to append to.
- `content`: String content to append.

**Returns:** A status message and the updated file's SHA-256 hash.

---

### `delete_text_file_contents`

**Description:** Deletes a range of lines (inclusive) from a text file.

**Args:**
- `filepath`: Path to the file to modify.
- `start_line`: 1-indexed starting line to delete.
- `end_line`: 1-indexed ending line to delete.

**Returns:** A status message and the updated file's SHA-256 hash.

---

### `insert_text_file_contents`

**Description:** Inserts a block of text at a specific line in a text file.

**Args:**
- `filepath`: Path to the file to modify.
- `insert_at_line`: 1-indexed line number to insert before.
- `content`: String content to insert.

**Returns:** A status message and the updated file's SHA-256 hash.

---

### `patch_text_file_contents`

**Description:** Atomically replaces a range of lines in a text file with new content, ensuring concurrency control via a hash check.

**Args:**
- `filepath`: Path to the file to patch.
- `start_line`: 1-indexed starting line of the range to replace.
- `end_line`: 1-indexed ending line of the range to replace.
- `new_content`: New content to insert.
- `expected_hash`: SHA-256 hash of the file before modification.

**Returns:** A status message and the updated file's SHA-256 hash if successful; otherwise, a conflict message.