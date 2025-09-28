# Outlook Email Manager Test Report

## 1. Test Summary

**Server:** `mcp_outlook_email_manager`  
**Objective:** The server provides an interface to interact with Microsoft Outlook via MCP, enabling users to list folders, search and retrieve emails, view details, reply, and compose new messages.  

**Overall Result:** **Failed with critical issues** – Core functionalities like listing recent emails, searching emails, and retrieving specific email content failed due to a recurring error related to accessing the `ReceivedTime` property of email objects.

**Key Statistics:**
- Total Tests Executed: 10
- Successful Tests: 2
- Failed Tests: 8

---

## 2. Test Environment

**Execution Mode:** Automated plan-based execution  
**MCP Server Tools:**
- `list_folders`
- `list_recent_emails`
- `search_emails`
- `get_email_by_number`
- `reply_to_email_by_number`
- `compose_email`

---

## 3. Detailed Test Results

### ✅ list_folders — List all available Outlook folders

- **Step:** Happy path: List all available Outlook folders to verify basic connectivity and access.
- **Tool:** `list_folders`
- **Parameters:** {}
- **Status:** ✅ Success
- **Result:** Successfully returned three email accounts as folder names (e.g., "1291980381@qq.com").

---

### ❌ list_recent_emails — Retrieve emails from last 7 days in Inbox

- **Step:** Happy path: Retrieve emails from the last 7 days in the Inbox folder. Caches email metadata for further use.
- **Tool:** `list_recent_emails`
- **Parameters:** {"days": 7, "folder_name": "Inbox"}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"Failed to list recent emails: <unknown>.ReceivedTime"`

---

### ❌ search_emails — Search for 'meeting' within a full year range

- **Step:** Dependent call (context): Search for emails containing 'meeting' within a full year range.
- **Tool:** `search_emails`
- **Parameters:** {"query": "meeting", "start_date": "2025-01-01", "end_date": "2025-12-31", "folder_name": "Inbox"}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"Failed to search emails: <unknown>.ReceivedTime"`

---

### ❌ get_email_by_number — Get full details of first cached email

- **Step:** Dependent call (after list_recent_emails): Retrieve full details of the first email in the cached list.
- **Tool:** `get_email_by_number`
- **Parameters:** {"email_number": 0}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"Failed to get email by number: Invalid email number"`

---

### ❌ reply_to_email_by_number — Reply to previously retrieved email

- **Step:** Dependent call (after get_email_by_number): Reply to the same email used in the previous step.
- **Tool:** `reply_to_email_by_number`
- **Parameters:** {"email_number": 0, "reply_text": "Thank you for the update. I'll get back to you shortly."}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"Failed to reply to email: Invalid email number"`

---

### ✅ compose_email — Send a test email

- **Step:** Happy path: Send a new email to validate outgoing capabilities.
- **Tool:** `compose_email`
- **Parameters:** {"subject": "Test Email from MCP", "body": "This is a test email sent via the Model-driven Co-routine Protocol server.", "recipients": ["test@example.com"], "cc": ["cc_test@example.com"]}
- **Status:** ✅ Success
- **Result:** `"Email sent successfully"`

---

### ❌ list_recent_emails — Invalid folder name

- **Step:** Edge case: Test behavior when an invalid folder name is provided.
- **Tool:** `list_recent_emails`
- **Parameters:** {"days": 5, "folder_name": "InvalidFolderName"}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"(-2147352567, '发生意外。', (4096, 'Microsoft Outlook', '尝试的操作失败。找不到某个对象。', None, 0, -2147221233), None)"`

---

### ❌ search_emails — Empty query with valid start date

- **Step:** Edge case: Test how the system handles an empty query string with a valid start date.
- **Tool:** `search_emails`
- **Parameters:** {"query": "", "start_date": "2025-01-01"}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"Failed to search emails: <unknown>.ReceivedTime"`

---

### ❌ get_email_by_number — Negative index

- **Step:** Edge case: Attempt to retrieve an email with a negative index to test error handling.
- **Tool:** `get_email_by_number`
- **Parameters:** {"email_number": -1}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"Failed to get email by number: Invalid email number"`

---

### ❌ compose_email — Missing recipient

- **Step:** Edge case: Attempt to send an email with an empty recipients list to test validation logic.
- **Tool:** `compose_email`
- **Parameters:** {"subject": "Incomplete Email Test", "body": "This email should fail due to missing recipient.", "recipients": []}
- **Status:** ❌ Failure
- **Result:** Error executing tool: `"(-2147352567, '发生意外。', (4096, 'Microsoft Outlook', '我们需要知道此内容的收件人。请确保至少输入一个名称。', None, 0, -2147467259), None)"`

---

## 4. Analysis and Findings

### Functionality Coverage

The test plan covered most core functionalities:
- Folder listing ✅
- Email retrieval (recent/search) ❌
- Email detail access ❌
- Email reply ❌
- Email composition ✅

However, several key functions failed, particularly those relying on the `ReceivedTime` property.

### Identified Issues

1. **Critical Bug: Accessing `ReceivedTime` Fails**
   - Tools affected: `list_recent_emails`, `search_emails`, `get_email_by_number`
   - Root cause: The `ReceivedTime` attribute appears inaccessible or improperly handled in the Outlook COM object interaction.
   - Impact: Breaks all time-based filtering and caching functionality.

2. **Error Handling Inconsistencies**
   - Some tools return structured COM errors (e.g., Chinese error messages), while others raise generic Python exceptions.
   - Example: `list_recent_emails` fails silently without indicating the root cause clearly.

3. **Stateful Operation Failures**
   - Tools depending on prior state (`get_email_by_number`, `reply_to_email_by_number`) failed because earlier steps did not populate the cache properly.

4. **Validation Gaps**
   - `search_emails` allows an empty query with only a start date, leading to failure instead of early validation.

### Error Handling Evaluation

- **Good:** Clear error messages for out-of-bounds indices.
- **Poor:** Generic failures like `<unknown>.ReceivedTime` are unhelpful for debugging.
- **Missing:** No input validation in some cases (e.g., empty query).

---

## 5. Conclusion and Recommendations

The server currently has **critical stability and correctness issues**, primarily centered around the inability to access the `ReceivedTime` property of Outlook emails. This breaks nearly all core functionality except folder listing and email sending.

### Recommendations:

1. **Fix `ReceivedTime` Access**
   - Investigate whether the Outlook COM API returns a compatible datetime format or requires conversion.
   - Add try-catch blocks around `ReceivedTime` access to provide meaningful feedback if unavailable.

2. **Improve Input Validation**
   - Reject empty queries in `search_emails`.
   - Validate that folder names exist before querying.

3. **Enhance Error Messaging**
   - Replace generic errors like `<unknown>.ReceivedTime` with actionable messages.
   - Return consistent English error strings regardless of underlying COM language settings.

4. **Improve State Management**
   - Ensure dependent operations fail gracefully when preconditions aren't met (e.g., no cache exists).
   - Consider resetting state after certain operations or providing explicit reset/clear tools.

5. **Add Unit Tests for COM Interactions**
   - Mock Outlook responses or add unit tests for COM interactions to catch these types of runtime failures during development.

---

### BUG_REPORT_JSON
```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "Accessing ReceivedTime property of email objects fails unexpectedly.",
      "problematic_tool": "list_recent_emails",
      "failed_test_step": "Happy path: Retrieve emails from the last 7 days in the Inbox folder. Caches email metadata for further use.",
      "expected_behavior": "Should return a list of recent emails with subject, sender, and received_time.",
      "actual_behavior": "Error executing tool: Failed to list recent emails: <unknown>.ReceivedTime"
    },
    {
      "bug_id": 2,
      "description": "Searching emails with query and date range fails due to ReceivedTime issue.",
      "problematic_tool": "search_emails",
      "failed_test_step": "Dependent call (context): Search for emails containing 'meeting' within a full year range.",
      "expected_behavior": "Should return matching emails filtered by time range and query.",
      "actual_behavior": "Error executing tool: Failed to search emails: <unknown>.ReceivedTime"
    },
    {
      "bug_id": 3,
      "description": "Empty query in search_emails leads to unexpected failure.",
      "problematic_tool": "search_emails",
      "failed_test_step": "Edge case: Test how the system handles an empty query string with a valid start date.",
      "expected_behavior": "Should either return all emails in the date range or reject the empty query.",
      "actual_behavior": "Error executing tool: Failed to search emails: <unknown>.ReceivedTime"
    },
    {
      "bug_id": 4,
      "description": "Email cache not populated, causing dependent tools to fail.",
      "problematic_tool": "get_email_by_number",
      "failed_test_step": "Dependent call (after list_recent_emails): Retrieve full details of the first email in the cached list.",
      "expected_behavior": "Should return full email content including body and attachments.",
      "actual_behavior": "Error executing tool: Failed to get email by number: Invalid email number"
    }
  ]
}
```
### END_BUG_REPORT_JSON