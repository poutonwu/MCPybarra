import sys
import json
import datetime
from datetime import timedelta
import win32com.client
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("mcp_outlook_manager")

# Global variables to cache last listed emails
last_listed_emails = []
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

@mcp.tool()
def list_folders() -> str:
    """
    Lists all available Outlook mail folders.

    Returns:
        A JSON-formatted string containing a list of folder names.

    Example:
        list_folders()
    """
    try:
        folders = []
        for i in range(1, 21):  # Assuming max 20 folders for simplicity
            try:
                folder = outlook.GetDefaultFolder(i)
                folders.append(folder.Name)
            except Exception:
                continue
        return json.dumps(folders)
    except Exception as e:
        return json.dumps({"error": f"Failed to list folders: {str(e)}"})

@mcp.tool()
def list_recent_emails(days: int, folder: str = None) -> str:
    """
    Retrieves a list of email subject lines from a specified folder within a given number of days.

    Args:
        days: Number of days to look back for recent emails.
        folder: Name of the folder to search in (optional; defaults to the inbox).

    Returns:
        A JSON-formatted string containing a list of email subject lines.

    Example:
        list_recent_emails(days=7, folder="Inbox")
    """
    global last_listed_emails
    try:
        if folder is None:
            inbox = outlook.GetDefaultFolder(6)  # Inbox folder
        else:
            inbox = outlook.Folders.Item(folder)

        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        date_from = datetime.datetime.now() - timedelta(days=days)
        recent_emails = [msg.Subject for msg in messages if msg.ReceivedTime >= date_from]

        last_listed_emails = recent_emails
        return json.dumps(recent_emails)
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve recent emails: {str(e)}"})

@mcp.tool()
def search_emails(keyword: str = None, contact: str = None, start_date: str = None, end_date: str = None, folder: str = None) -> str:
    """
    Searches for emails based on keywords or contact names within a specified time range and folder.

    Args:
        keyword: Keyword to search for in the email body or subject.
        contact: Contact name or email address to filter results.
        start_date: Start date for the search range (format: `YYYY-MM-DD`).
        end_date: End date for the search range (format: `YYYY-MM-DD`).
        folder: Name of the folder to search in (optional; defaults to the inbox).

    Returns:
        A JSON-formatted string containing a list of matching email subject lines.

    Example:
        search_emails(keyword="urgent", contact="john.doe@example.com", start_date="2023-01-01", end_date="2023-01-31", folder="Inbox")
    """
    try:
        if folder is None:
            inbox = outlook.GetDefaultFolder(6)  # Inbox folder
        else:
            inbox = outlook.Folders.Item(folder)

        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        matching_emails = []

        start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        for msg in messages:
            received_time = msg.ReceivedTime
            if ((start_datetime is None or received_time >= start_datetime) and
                (end_datetime is None or received_time <= end_datetime) and
                (keyword is None or (keyword in msg.Subject or keyword in msg.Body)) and
                (contact is None or (contact in msg.SenderEmailAddress or contact in msg.To))):
                matching_emails.append(msg.Subject)

        return json.dumps(matching_emails)
    except Exception as e:
        return json.dumps({"error": f"Failed to search emails: {str(e)}"})

@mcp.tool()
def get_email_by_number(email_number: int) -> str:
    """
    Retrieves detailed information (body and attachments) for a specific email from the last listed set of emails.

    Args:
        email_number: Index of the email in the last listed set of emails.

    Returns:
        A JSON-formatted string containing the email's body, subject, and attachment details.

    Example:
        get_email_by_number(email_number=5)
    """
    global last_listed_emails
    try:
        if not last_listed_emails or email_number < 0 or email_number >= len(last_listed_emails):
            return json.dumps({"error": "Invalid email number."})

        inbox = outlook.GetDefaultFolder(6)  # Inbox folder
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        message = None

        for msg in messages:
            if msg.Subject == last_listed_emails[email_number]:
                message = msg
                break

        if not message:
            return json.dumps({"error": "Email not found."})

        attachments = [attachment.FileName for attachment in message.Attachments]
        email_details = {
            "subject": message.Subject,
            "body": message.Body,
            "attachments": attachments
        }

        return json.dumps(email_details)
    except Exception as e:
        return json.dumps({"error": f"Failed to get email details: {str(e)}"})

@mcp.tool()
def reply_to_email_by_number(email_number: int, reply_content: str) -> str:
    """
    Sends a reply to a specific email from the last listed set of emails.

    Args:
        email_number: Index of the email in the last listed set of emails.
        reply_content: Content of the reply message.

    Returns:
        A string indicating success or failure of the operation.

    Example:
        reply_to_email_by_number(email_number=5, reply_content="Thank you for your email. I will review it shortly.")
    """
    global last_listed_emails
    try:
        if not last_listed_emails or email_number < 0 or email_number >= len(last_listed_emails):
            return json.dumps({"error": "Invalid email number."})

        inbox = outlook.GetDefaultFolder(6)  # Inbox folder
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        message = None

        for msg in messages:
            if msg.Subject == last_listed_emails[email_number]:
                message = msg
                break

        if not message:
            return json.dumps({"error": "Email not found."})

        reply = message.Reply()
        reply.Body = reply_content
        reply.Send()

        return json.dumps({"success": "Reply sent successfully."})
    except Exception as e:
        return json.dumps({"error": f"Failed to send reply: {str(e)}"})

@mcp.tool()
def compose_email(to: str, cc: str = None, subject: str = None, body: str = None, attachments: list = None) -> str:
    """
    Creates and sends a new email with specified recipients, subject, body, and optional attachments.

    Args:
        to: Comma-separated list of recipient email addresses.
        cc: Comma-separated list of CC recipient email addresses (optional).
        subject: Subject of the email.
        body: Body content of the email.
        attachments: List of file paths to attach (optional).

    Returns:
        A string indicating success or failure of the operation.

    Example:
        compose_email(
            to="recipient@example.com",
            cc="cc_recipient@example.com",
            subject="Meeting Reminder",
            body="Please remember to attend the meeting tomorrow at 10 AM.",
            attachments=["path/to/file1.pdf", "path/to/file2.docx"]
        )
    """
    try:
        mail = outlook.CreateItem(0)
        mail.To = to
        if cc:
            mail.CC = cc
        mail.Subject = subject
        mail.Body = body

        if attachments:
            for attachment in attachments:
                mail.Attachments.Add(attachment)

        mail.Send()
        return json.dumps({"success": "Email sent successfully."})
    except Exception as e:
        return json.dumps({"error": f"Failed to send email: {str(e)}"})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()