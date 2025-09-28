# mcp_outlook_manager

## Overview

The `mcp_outlook_manager` is an MCP (Model Context Protocol) server that enables large language models to interact with Microsoft Outlook via a set of tools. This server allows for listing folders, searching and retrieving emails, replying to messages, and composing new emails — all programmatically through the MCP interface.

This integration provides seamless access to Outlook data such as email folders, recent or filtered messages, and supports common operations like reading, replying, and sending emails.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install pywin32 mcp
```

These packages are also listed in a `requirements.txt` file if you prefer installing via:

```bash
pip install -r requirements.txt
```

> **Note:** This server uses `pywin32` to interface with Outlook and therefore only works on Windows systems where Outlook is installed and running.

## Running the Server

To start the MCP Outlook Manager server, run the Python script from the command line:

```bash
python mcp_outlook_server.py
```

This will launch the server using the default `stdio` transport protocol, allowing clients to communicate with it locally.

## Available Tools

Below is a list of available MCP tools exposed by this server:

### `list_folders()`
Retrieves and lists all accessible email folders in the user's main mailbox, including top-level and subfolders.

**Returns:**
- A JSON array of folder names.

---

### `list_recent_emails(days: int, folder_name: str = "Inbox")`
Fetches a list of the most recent emails received within the specified number of days from a given folder (default: Inbox).

**Parameters:**
- `days`: Number of past days to search.
- `folder_name`: Folder to search in (e.g., "Sent Items").

**Returns:**
- List of emails with assigned numbers, subjects, senders, and timestamps.

---

### `search_emails(query: str, start_date: str, end_date: str, folder_name: str = "Inbox")`
Searches for emails matching a keyword within a date range and folder. Supports filtering by subject, body, and sender.

**Parameters:**
- `query`: Search term.
- `start_date`: Start date (`YYYY-MM-DD`).
- `end_date`: End date (`YYYY-MM-DD`).
- `folder_name`: Folder to search in.

**Returns:**
- List of matching emails with metadata.

---

### `get_email_by_number(email_number: int)`
Retrieves full details of a previously listed email using its assigned number.

**Parameters:**
- `email_number`: The number assigned during listing/searching.

**Returns:**
- Email details including sender, recipients, subject, body, and attachments.

---

### `reply_to_email_by_number(email_number: int, reply_body: str)`
Sends a "Reply All" to a specific email using its number. The provided text is prepended to the original message.

**Parameters:**
- `email_number`: Cached email number.
- `reply_body`: Content of the reply.

**Returns:**
- Status confirmation of the reply.

---

### `compose_email(subject: str, body: str, recipients: List[str], cc_recipients: Optional[List[str]] = None)`
Composes and sends a new email with the given content and recipients.

**Parameters:**
- `subject`: Subject line.
- `body`: Main content of the email.
- `recipients`: List of recipient email addresses.
- `cc_recipients`: Optional CC recipients.

**Returns:**
- Confirmation message indicating success or failure.