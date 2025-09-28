### **MCP Tools Plan**  

#### **1. `list_folders`**  
- **Description**: Lists all available Outlook mail folders.  
- **Parameters**: None.  
- **Return Value**: A list of folder names (strings).  

#### **2. `list_recent_emails`**  
- **Description**: Retrieves email titles from a specified folder within a given number of days. Caches email metadata.  
- **Parameters**:  
  - `days` (int): Number of days to look back.  
  - `folder_name` (str, optional): Specific folder name (default: Inbox).  
- **Return Value**: A list of dictionaries containing `subject`, `sender`, and `received_time` for each email.  

#### **3. `search_emails`**  
- **Description**: Searches emails by keyword or sender within a specified time range and folder.  
- **Parameters**:  
  - `query` (str): Keyword or sender name.  
  - `start_date` (str, optional): Start date in `YYYY-MM-DD` format.  
  - `end_date` (str, optional): End date in `YYYY-MM-DD` format.  
  - `folder_name` (str, optional): Folder to search (default: Inbox).  
- **Return Value**: A list of dictionaries with `subject`, `sender`, and `received_time`.  

#### **4. `get_email_by_number`**  
- **Description**: Retrieves the full content (body + attachments) of an email from the cached list.  
- **Parameters**:  
  - `email_number` (int): Index of the email in the last retrieved list.  
- **Return Value**: A dictionary with `subject`, `sender`, `body`, and `attachments` (list of file paths).  

#### **5. `reply_to_email_by_number`**  
- **Description**: Replies to a specific email (by index) with a given message.  
- **Parameters**:  
  - `email_number` (int): Index of the email in the last retrieved list.  
  - `reply_text` (str): The reply message.  
- **Return Value**: Confirmation message (success/failure).  

#### **6. `compose_email`**  
- **Description**: Creates and sends a new email.  
- **Parameters**:  
  - `subject` (str): Email subject.  
  - `body` (str): Email body.  
  - `recipients` (list[str]): List of recipient email addresses.  
  - `cc` (list[str], optional): List of CC recipients.  
- **Return Value**: Confirmation message (success/failure).  

---  

### **Server Overview**  
A **MCP server** that automates Outlook email management using `win32com`. It allows listing folders, retrieving recent emails, searching by criteria, viewing full email content, replying, and composing new emails.  

---  

### **File to be Generated**  
- **Filename**: `outlook_mcp_server.py`  

---  

### **Dependencies**  
- `win32com.client` (via `pywin32`)  
- `python-mcp` (for MCP server setup)  
- `datetime` (for date handling)  

No external API calls are needed—this relies entirely on local Outlook integration.  

---  

This plan adheres strictly to the user's request and avoids unnecessary complexity. The implementation will use `win32com` for Outlook automation, ensuring all specified functionalities are covered.