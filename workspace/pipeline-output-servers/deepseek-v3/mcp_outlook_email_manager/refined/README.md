# mcp_outlook_email_manager

A MCP server that provides tools for managing Outlook emails through the Model Context Protocol (MCP).

## Overview

This server provides a set of tools to interact with Microsoft Outlook, allowing you to list folders, search emails, read recent messages, and send replies or new emails. It uses the `win32com.client` library to interface with Outlook and the `FastMCP` framework to expose these capabilities via MCP.

## Installation

Before running the server, ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

Make sure you have Microsoft Outlook installed on your system, as this server uses the Outlook COM API to interact with your email client.

## Running the Server

To start the server, run the following command:

```bash
python mcp_outlook_email_manager.py
```

The server will initialize and begin listening for MCP requests via standard input/output.

## Available Tools

The following tools are available for use:

### `list_folders`

**Description:** Lists all available Outlook mail folders.

**Returns:** A list of folder names (strings).

---

### `list_recent_emails`

**Description:** Retrieves email titles, senders, and received times from a specified folder within a given number of days. Caches email metadata for later retrieval.

**Arguments:**
- `days`: Number of days to look back.
- `folder_name`: Specific folder name (default: "Inbox").

**Returns:** A list of dictionaries containing `'subject'`, `'sender'`, and `'received_time'` for each email.

---

### `search_emails`

**Description:** Searches emails by keyword or sender within a specified time range and folder.

**Arguments:**
- `query`: Keyword or sender name.
- `start_date`: Start date in `'YYYY-MM-DD'` format.
- `end_date`: End date in `'YYYY-MM-DD'` format.
- `folder_name`: Folder to search (default: "Inbox").

**Returns:** A list of dictionaries with `'subject'`, `'sender'`, and `'received_time'`.

---

### `get_email_by_number`

**Description:** Retrieves the full content (body and attachments) of an email from the cached list.

**Arguments:**
- `email_number`: Index of the email in the last retrieved list.

**Returns:** A dictionary with `'subject'`, `'sender'`, `'body'`, and `'attachments'` (list of file paths).

---

### `reply_to_email_by_number`

**Description:** Replies to a specific email (by index) with a given message.

**Arguments:**
- `email_number`: Index of the email in the last retrieved list.
- `reply_text`: The reply message.

**Returns:** Confirmation message (success/failure).

---

### `compose_email`

**Description:** Creates and sends a new email.

**Arguments:**
- `subject`: Email subject.
- `body`: Email body.
- `recipients`: List of recipient email addresses.
- `cc`: List of CC recipients (optional).

**Returns:** Confirmation message (success/failure).