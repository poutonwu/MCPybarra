# 🧪 Test Report: `mcp_zotero_manager`

---

## 1. Test Summary

- **Server:** `mcp_zotero_manager`
- **Objective:** The server provides an interface to interact with the Zotero API, allowing users to search for items and retrieve metadata or full-text content using item keys.
- **Overall Result:** ❌ Critical failures identified
- **Key Statistics:**
  - Total Tests Executed: 11
  - Successful Tests: 0
  - Failed Tests: 11

---

## 2. Test Environment

- **Execution Mode:** Automated plan-based execution
- **MCP Server Tools:**
  - `get_item_metadata`
  - `get_item_fulltext`
  - `search_items`

---

## 3. Detailed Test Results

### 🔍 Tool: `search_items`

#### Step: Happy path: Search for items related to 'Machine Learning' using default search parameters.
- **Tool:** `search_items`
- **Parameters:** `{"query": "Machine Learning"}`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items?q=Machine+Learning&qmode=titleCreatorYear&include=data

#### Step: Test search with title-only filtering.
- **Tool:** `search_items`
- **Parameters:** `{"query": "AI Ethics", "search_by_title": true, "search_by_creator": false, "search_by_year": false, "search_by_fulltext": false}`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items?q=AI+Ethics&qmode=titleCreatorYear&include=data

#### Step: Test search based only on creator name.
- **Tool:** `search_items`
- **Parameters:** `{"query": "John Doe", "search_by_title": false, "search_by_creator": true, "search_by_year": false, "search_by_fulltext": false}`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items?q=John+Doe&qmode=titleCreatorYear&include=data

#### Step: Test search by publication year.
- **Tool:** `search_items`
- **Parameters:** `{"query": "2023", "search_by_title": false, "search_by_creator": false, "search_by_year": true, "search_by_fulltext": false}`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items?q=2023&qmode=titleCreatorYear&include=data

#### Step: Edge case: Test server behavior when query is empty.
- **Tool:** `search_items`
- **Parameters:** `{"query": ""}`
- **Status:** ❌ Failure
- **Result:** `'query' must be a non-empty string.`

#### Step: Edge case: Test server handling of special characters in query.
- **Tool:** `search_items`
- **Parameters:** `{"query": "!@#$%^&*()"}` 
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items?q=%21%40%23%24%25%5E%26%2A%28%29&qmode=titleCreatorYear&include=data

#### Step: Test full-text search functionality.
- **Tool:** `search_items`
- **Parameters:** `{"query": "deep learning", "search_by_title": false, "search_by_creator": false, "search_by_year": false, "search_by_fulltext": true}`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items?q=deep+learning&qmode=everything&include=data

---

### 📄 Tool: `get_item_metadata`

#### Step: Dependent call: Fetch metadata of the first item returned by the previous search.
- **Tool:** `get_item_metadata`
- **Parameters:** `{"item_key": null}`
- **Status:** ❌ Failure
- **Result:** A required parameter resolved to None, likely due to a failure in a dependency.

#### Step: Edge case: Attempt to fetch metadata with an invalid item key.
- **Tool:** `get_item_metadata`
- **Parameters:** `{"item_key": "invalid-key-123"}`
- **Status:** ❌ Failure
- **Result:** Error executing tool `get_item_metadata`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items/invalid-key-123

---

### 📄 Tool: `get_item_fulltext`

#### Step: Dependent call: Retrieve full text content of the first item from the search results.
- **Tool:** `get_item_fulltext`
- **Parameters:** `{"item_key": null}`
- **Status:** ❌ Failure
- **Result:** A required parameter resolved to None, likely due to a failure in a dependency.

#### Step: Edge case: Attempt to fetch full text with an invalid item key.
- **Tool:** `get_item_fulltext`
- **Parameters:** `{"item_key": "invalid-key-456"}`
- **Status:** ❌ Failure
- **Result:** Error executing tool `get_item_fulltext`: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items/invalid-key-456/fulltext

---

## 4. Analysis and Findings

### Functionality Coverage
All main functionalities were tested:
- Searching for items by various criteria (title, creator, year, fulltext)
- Retrieving metadata for specific items
- Extracting full-text content

### Identified Issues
- All HTTP requests resulted in 404 Not Found errors.
- This suggests that either:
  - The Zotero library ID or credentials are incorrect.
  - The Zotero API endpoint URL is misconfigured.
  - The test environment does not have access to real Zotero data.
- No dependent calls could proceed because the initial `search_items` call failed.
- Empty query validation works correctly, but other input validations did not get fully tested due to prior failures.

### Stateful Operations
No stateful operations succeeded. All dependent steps failed due to missing outputs from earlier steps.

### Error Handling
- The server correctly raises descriptive exceptions for invalid inputs (e.g., empty query).
- However, it fails to handle or report meaningful issues when interacting with the Zotero API (e.g., returns generic 404 without diagnosing auth or ID issues).

---

## 5. Conclusion and Recommendations

The server encountered critical failures across all test cases due to 404 errors during Zotero API interactions. While basic input validation was confirmed functional, no meaningful Zotero interaction occurred.

### Recommendations:
1. **Verify Zotero Credentials and Library ID**: Ensure the provided `ZOTERO_LIBRARY_ID`, `ZOTERO_API_KEY`, and `ZOTERO_LIBRARY_TYPE` are valid and correspond to a real Zotero account with accessible data.
2. **Check API Endpoint URL**: Confirm that `ZOTERO_API_BASE` points to the correct and currently active Zotero API endpoint.
3. **Enhance Error Messages**: Improve error reporting for failed API requests to distinguish between authentication issues, invalid item keys, and connectivity problems.
4. **Mock External Dependencies**: Consider mocking external Zotero API responses during testing to validate internal logic independently.
5. **Improve Documentation**: Clarify expected preconditions for successful operation (e.g., valid API key format, supported Zotero versions, etc.).

---

### BUG_REPORT_JSON
```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "All Zotero API requests fail with 404 Not Found errors.",
      "problematic_tool": "search_items",
      "failed_test_step": "Happy path: Search for items related to 'Machine Learning' using default search parameters.",
      "expected_behavior": "Successful search and return of matching Zotero items.",
      "actual_behavior": "Error executing tool search_items: Request failed: 404 Client Error: Not Found for url: https://api.zotero.org/user/16026771/items?q=Machine+Learning&qmode=titleCreatorYear&include=data"
    },
    {
      "bug_id": 2,
      "description": "Dependent calls fail due to missing outputs from failed parent steps.",
      "problematic_tool": "get_item_metadata",
      "failed_test_step": "Dependent call: Fetch metadata of the first item returned by the previous search.",
      "expected_behavior": "Fetch metadata of the first item if available.",
      "actual_behavior": "A required parameter resolved to None, likely due to a failure in a dependency."
    }
  ]
}
```
### END_BUG_REPORT_JSON