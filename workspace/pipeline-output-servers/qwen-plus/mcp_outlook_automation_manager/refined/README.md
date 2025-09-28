# mcp_outlook_automation_manager

## Overview

`mcp_outlook_automation_manager` is an MCP server that enables automation of Microsoft Outlook tasks through a set of tools. It allows users to interact with Outlook for actions such as listing folders, retrieving emails, searching messages, replying to emails, and composing new ones.

This server uses the `win32com.client` library to interface directly with Outlook and provides JSON-based responses for seamless integration with LLMs via the Model Context Protocol (MCP).

---

## Installation

Before running the server, ensure you have Python 3.10 or higher installed.

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure the following packages are included in your `requirements.txt` file:

```
mcp[cli]
pywin32
```

2. Ensure Microsoft Outlook is installed on the system where this script runs, as it relies on COM automation.

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_outlook_automation_manager.py
```

This will launch the MCP server using standard input/output (`stdio`) transport protocol.

---

## Available Tools

The following tools are available for use with the MCP client:

### 1. `list_folders`

**Description:** Lists all available Outlook mail folders.

**Returns:** A list of folder objects containing name and path (e.g., `{"name": "收件箱", "path": "\\收件箱"}`).

---

### 2. `list_recent_emails`

**Description:** Retrieves emails received within the specified number of days from a given folder.

**Parameters:**
- `days`: Number of days to look back.
- `folder_path`: Path to the folder (default is Inbox).

**Returns:** List of recent email objects with subject, sender, and date.

---

### 3. `search_emails`

**Description:** Searches emails by date range, contact, or keyword.

**Parameters:**
- `start_date`: Start date in `YYYY-MM-DD` format.
- `end_date`: End date in `YYYY-MM-DD` format.
- `folder_path`: Folder path to search in (default is Inbox).
- `contact`: Contact name or email address filter.
- `keyword`: Keyword to search in subject or body.

**Returns:** List of matching email objects with subject, sender, and date.

---

### 4. `get_email_by_number`

**Description:** Gets detailed information about a specific email from the most recently retrieved list.

**Parameters:**
- `email_index`: Index of the email in the last query result.

**Returns:** Email details including subject, sender, date, body, and attachments.

---

### 5. `reply_to_email_by_number`

**Description:** Replies to a specific email from the recent list.

**Parameters:**
- `email_index`: Index of the email to reply to.
- `reply_content`: Content of the reply message.

**Returns:** Confirmation message indicating successful reply.

---

### 6. `compose_email`

**Description:** Creates and sends a new email.

**Parameters:**
- `subject`: Subject of the email.
- `body`: Body text of the email.
- `to`: Recipient email address.
- `cc`: Optional CC recipient address.

**Returns:** Confirmation message indicating successful delivery.