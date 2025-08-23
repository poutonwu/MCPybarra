# Outlook MCP Server

A Model Context Protocol (MCP) server that provides access to Microsoft Outlook email functionality, allowing LLMs and other MCP clients to read, search, and manage emails through a standardized interface.

## Features

- **Folder Management**: List available mail folders in your Outlook client
- **Email Listing**: Retrieve emails from specified time periods
- **Email Search**: Search emails by contact name, keywords, or phrases with OR operators
- **Email Details**: View complete email content, including attachments
- **Email Composition**: Create and send new emails
- **Email Replies**: Reply to existing emails

## Prerequisites

- Windows operating system
- Python 3.10 or later
- Microsoft Outlook installed and configured with an active account
- Claude Desktop or another MCP-compatible client

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install mcp>=1.2.0 pywin32>=305
```

3. Configure Claude Desktop (or your preferred MCP client) to use this server

## Configuration

### Claude Desktop Configuration

Add the following to your `MCP_client_config.json` file:

```json
{
  "mcpServers": {
    "outlook": {
      "command": "python",
      "args": ["Your path\\outlook_mcp_server.py"],
      "env": {}
    }
  }
}
```


## Usage

### Starting the Server

You can start the server directly:

```bash
python outlook_mcp_server.py
```

Or allow an MCP client like Claude Desktop to start it via the configuration.

### Available Tools

The server provides the following tools:

1. `list_folders`: Lists all available mail folders in Outlook
2. `list_recent_emails`: Lists email titles from the specified number of days
3. `search_emails`: Searches emails by contact name or keyword
4. `get_email_by_number`: Retrieves detailed content of a specific email
5. `reply_to_email_by_number`: Replies to a specific email
6. `compose_email`: Creates and sends a new email

### Example Workflow

1. Use `list_folders` to see all available mail folders
2. Use `list_recent_emails` to view recent emails (e.g., from last 7 days)
3. Use `search_emails` to find specific emails by keywords
4. Use `get_email_by_number` to view a complete email
5. Use `reply_to_email_by_number` to respond to an email

## Examples

### Listing Recent Emails
```
Could you show me my unread emails from the last 3 days?
```

### Searching for Emails
```
Search for emails about "project update OR meeting notes" in the last week
```

### Reading Email Details
```
Show me the details of email #2 from the list
```

### Replying to an Email
```
Reply to email #3 with: "Thanks for the information. I'll review this and get back to you tomorrow."
```

### Composing a New Email
```
Send an email to john.doe@example.com with subject "Meeting Agenda" and body "Here's the agenda for our upcoming meeting..."
```

## Troubleshooting

- **Connection Issues**: Ensure Outlook is running and properly configured
- **Permission Errors**: Make sure the script has permission to access Outlook
- **Search Problems**: For complex searches, try using OR operators between terms
- **Email Access Errors**: Check if the email ID is valid and accessible
- **Server Crashes**: Check Outlook's connection and stability

## Security Considerations

This server has access to your Outlook email account and can read, send, and manage emails. Use it only with trusted MCP clients and in secure environments.

## Limitations

- Currently supports text emails only (not HTML)
- Maximum email history is limited to 30 days
- Search capabilities depend on Outlook's built-in search functionality
- Only supports basic email functions (no calendar, contacts, etc.)
