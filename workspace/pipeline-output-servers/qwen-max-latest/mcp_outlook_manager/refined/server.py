import sys
import json
import datetime
from datetime import timedelta
import win32com.client
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("mcp_outlook_manager")

# Global variables to cache last listed emails and their subjects
last_listed_emails = []
last_listed_email_subjects = []
try:
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
except Exception as e:
    print(f"Failed to initialize Outlook COM object: {str(e)}")
    outlook = None

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
        if outlook is None:
            return json.dumps({"error": "Outlook initialization failed"})
            
        folders = []
        # Get the Session object to access all stores
        session = outlook.Session
        # Get the root folder for all stores
        root_folder = session.Folders
        
        # Iterate through all stores (email accounts)
        for store in root_folder:
            # Get the top-level folders for this store
            for folder in store.Folders:
                folders.append(folder.Name)
        
        return json.dumps(folders)
    except Exception as e:
        return json.dumps({"error": f"Failed to list folders: {str(e)}"})

@mcp.tool()
def list_recent_emails(days: int, folder: str = None) -> str:
    """
    Retrieves a list of email subject lines from a specified folder within a given number of days.

    Args:
        days: Number of days to look back for recent emails (must be non-negative).
        folder: Name of the folder to search in (optional; defaults to the inbox).

    Returns:
        A JSON-formatted string containing a list of email subject lines.

    Example:
        list_recent_emails(days=7, folder="Inbox")
    """
    global last_listed_emails, last_listed_email_subjects
    try:
        if outlook is None:
            return json.dumps({"error": "Outlook initialization failed"})
            
        # Input validation
        if days < 0:
            return json.dumps({"error": "Days value must be non-negative"})

        # Get the specified folder or default to Inbox
        if folder is None:
            inbox = outlook.GetDefaultFolder(6)  # Inbox folder
        else:
            # Use Session to get folder by name
            inbox = outlook.Session.Folders.Item(folder)
            if inbox is None:
                return json.dumps({"error": f"Folder '{folder}' not found"})

        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        date_from = datetime.datetime.now() - timedelta(days=days)
        
        # Clear previous lists
        last_listed_emails = []
        last_listed_email_subjects = []
        
        # Collect recent emails
        for msg in messages:
            # Break loop if we pass the date threshold (since items are sorted)
            if msg.ReceivedTime < date_from:
                break
            last_listed_emails.append(msg)
            last_listed_email_subjects.append(msg.Subject)

        return json.dumps(last_listed_email_subjects)
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
        if outlook is None:
            return json.dumps({"error": "Outlook initialization failed"})
            
        # Get the specified folder or default to Inbox
        if folder is None:
            inbox = outlook.GetDefaultFolder(6)  # Inbox folder
        else:
            inbox = outlook.Session.Folders.Item(folder)
            if inbox is None:
                return json.dumps({"error": f"Folder '{folder}' not found"})

        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        matching_emails = []

        try:
            start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
        except ValueError as ve:
            return json.dumps({"error": f"Date format error: {str(ve)}"})

        for msg in messages:
            received_time = msg.ReceivedTime
            
            # Date range check
            if start_datetime and received_time < start_datetime:
                continue
            if end_datetime and received_time > end_datetime:
                continue
                
            # Keyword search check
            if keyword and keyword not in msg.Subject and keyword not in msg.Body:
                continue
                
            # Contact search check
            if contact and contact not in msg.SenderEmailAddress and contact not in msg.To:
                continue

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
        if outlook is None:
            return json.dumps({"error": "Outlook initialization failed"})
            
        if not last_listed_emails or email_number < 0 or email_number >= len(last_listed_emails):
            return json.dumps({"error": "Invalid email number."})

        message = last_listed_emails[email_number]

        # Get attachments
        attachments = []
        for attachment in message.Attachments:
            attachments.append(attachment.FileName)

        email_details = {
            "subject": message.Subject,
            "body": message.Body,
            "sender": message.SenderName,
            "sender_email": message.SenderEmailAddress,
            "received_time": str(message.ReceivedTime),
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
        if outlook is None:
            return json.dumps({"error": "Outlook initialization failed"})
            
        if not last_listed_emails or email_number < 0 or email_number >= len(last_listed_emails):
            return json.dumps({"error": "Invalid email number."})

        message = last_listed_emails[email_number]
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
        if outlook is None:
            return json.dumps({"error": "Outlook initialization failed"})
            
        mail = outlook.CreateItem(0)  # 0 represents a MailItem
        mail.To = to
        
        if cc:
            mail.CC = cc
            
        # Set default values if not provided
        mail.Subject = subject if subject is not None else ""
        mail.Body = body if body is not None else ""

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