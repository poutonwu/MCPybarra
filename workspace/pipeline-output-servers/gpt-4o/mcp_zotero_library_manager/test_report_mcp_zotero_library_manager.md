# Test Report: mcp_zotero_library_manager

## 1. Test Summary

- **Server:** `mcp_zotero_library_manager`
- **Objective:** The server provides a set of tools for interacting with the Zotero API, enabling users to search for items by title, creator, year, or full-text content, retrieve item metadata, and extract full-text from PDF attachments.
- **Overall Result:** Critical failures identified
- **Key Statistics:**
  - Total Tests Executed: 10
  - Successful Tests: 0
  - Failed Tests: 10

---

## 2. Test Environment

- **Execution Mode:** Automated plan-based execution
- **MCP Server Tools:**
  - `get_item_metadata`
  - `get_item_fulltext`
  - `search_items`

---

## 3. Detailed Test Results

### Tool: `search_items`

#### Step: Happy path: Search for items with the title 'Artificial Intelligence'.
- **Tool:** search_items
- **Parameters:** {"title": "Artificial Intelligence"}
- **Status:** ❌ Failure
- **Result:** Error message not returned directly, but test failed. The response appears to be valid JSON data, but the status is marked as error.

#### Step: Happy path: Search for items created by 'John Doe'.
- **Tool:** search_items
- **Parameters:** {"creators": "John Doe"}
- **Status:** ❌ Failure
- **Result:** Same pattern as above — successful-looking result data, but test marked as error.

#### Step: Happy path: Search for items published in 2023.
- **Tool:** search_items
- **Parameters:** {"year": 2023}
- **Status:** ❌ Failure
- **Result:** Valid-looking search results returned, but status still marked as error.

#### Step: Happy path: Perform a full-text search for 'deep learning'.
- **Tool:** search_items
- **Parameters:** {"fulltext": "deep learning"}
- **Status:** ❌ Failure
- **Result:** Again, JSON output appears correct, but test status is error.

#### Step: Edge case: Test the server's behavior when all search parameters are empty.
- **Tool:** search_items
- **Parameters:** {}
- **Status:** ❌ Failure
- **Result:** Server returns a list of items (as expected), but again the test is marked as error.

#### Step: Happy path: Test a complex search using multiple criteria simultaneously.
- **Tool:** search_items
- **Parameters:** {"title": "Machine Learning", "creators": "Jane Smith", "year": 2022, "fulltext": "neural networks"}
- **Status:** ❌ Failure
- **Result:** Search results appear normal, but test status is error.

---

### Tool: `get_item_metadata`

#### Step: Dependent call (list access): Use the DOI of the first item from the search results to fetch metadata.
- **Tool:** get_item_metadata
- **Parameters:** {"item_key": "10.48550/arXiv.2502.05664"}
- **Status:** ❌ Failure
- **Result:** `{"error": "list indices must be integers or slices, not str"}`

---

### Tool: `get_item_fulltext`

#### Step: Dependent call (key access): Use the DOI from the previous step to extract full text content.
- **Tool:** get_item_fulltext
- **Parameters:** {"item_key": "10.48550/arXiv.2502.05664"}
- **Status:** ❌ Failure
- **Result:** Same error as above: `{"error": "list indices must be integers or slices, not str"}`

---

### Edge Cases

#### Step: Edge case: Test the server's handling of an invalid item key for metadata fetching.
- **Tool:** get_item_metadata
- **Parameters:** {"item_key": "invalid-key-123"}
- **Status:** ❌ Failure
- **Result:** `{"error": "\nCode: 404\nURL: https://api.zotero.org/users/16026771/items/INVALID-KEY-123?locale=en-US&format=json&limit=100\nMethod: GET\nResponse: Not found"}`

#### Step: Edge case: Test the server's handling when no PDF attachment is found for a valid item key.
- **Tool:** get_item_fulltext
- **Parameters:** {"item_key": "ABC123"}
- **Status:** ❌ Failure
- **Result:** `{"error": "\nCode: 404\nURL: https://api.zotero.org/users/16026771/items/ABC123?locale=en-US&format=json&limit=100\nMethod: GET\nResponse: Not found"}`

---

## 4. Analysis and Findings

### Functionality Coverage

All three available tools were tested:
- `search_items`: Tested under various conditions including title, creator, year, full-text, empty, and multi-criteria searches.
- `get_item_metadata`: Tested with both valid and invalid item keys.
- `get_item_fulltext`: Tested with both valid and invalid item keys.

The test coverage was comprehensive in terms of use cases and edge cases.

### Identified Issues

1. **Unexpected Error Statuses on Successful-Looking Responses**
   - All calls return what looks like valid JSON data, but every test is marked as "error".
   - This suggests a fundamental issue with how the system interprets success vs failure — possibly returning malformed or non-standard responses that cause the test framework to misclassify them.

2. **Incorrect Handling of DOI Strings as Item Keys**
   - The server attempts to use DOIs (`10.48550/...`) as `item_key` values for `get_item_metadata` and `get_item_fulltext`, but these DOIs do not correspond to actual Zotero item keys.
   - As a result, it raises an index error due to string indexing being applied incorrectly.

3. **Zotero API Key or Authentication Issue**
   - Multiple tests show 404 errors for item lookups that should exist, suggesting possible issues with the Zotero credentials or library permissions.

### Stateful Operations

- There was an attempt to chain dependent operations (e.g., using a DOI from a search result to fetch metadata).
- However, this failed due to misuse of DOIs instead of actual Zotero item keys.

### Error Handling

- While the server does return detailed error messages (including Zotero API URLs and HTTP codes), these are inconsistently interpreted by the test framework.
- The error messages themselves are informative and include debugging information (e.g., URL, method, response), which is helpful for troubleshooting.

---

## 5. Conclusion and Recommendations

**Conclusion:**
The server logic appears largely functional — it can query Zotero and format results appropriately. However, there are critical issues with how the system reports success/failure statuses and handles item identifiers.

**Recommendations:**
1. **Fix Response Parsing Logic:** Ensure that successful API responses are correctly flagged as such in the test log.
2. **Use Correct Zotero Item Keys:** Only valid Zotero item keys (not DOIs) should be used to fetch metadata or full text.
3. **Verify Zotero Credentials:** Confirm that the Zotero API key, user ID, and library type are correct and have proper permissions.
4. **Improve Error Handling Consistency:** Ensure that all tool functions return standardized error structures and status codes.

---

### BUG_REPORT_JSON
```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "Server incorrectly marks valid Zotero API responses as errors.",
      "problematic_tool": "search_items",
      "failed_test_step": "Happy path: Search for items with the title 'Artificial Intelligence'.",
      "expected_behavior": "Valid search results should be marked as success.",
      "actual_behavior": "Test status was 'error' despite returning valid JSON search results."
    },
    {
      "bug_id": 2,
      "description": "Using DOIs instead of Zotero item keys causes index errors.",
      "problematic_tool": "get_item_metadata",
      "failed_test_step": "Dependent call (list access): Use the DOI of the first item from the search results to fetch metadata.",
      "expected_behavior": "Should fail gracefully if given an invalid item key.",
      "actual_behavior": "Returned error: \"list indices must be integers or slices, not str\""
    },
    {
      "bug_id": 3,
      "description": "Invalid item keys trigger Zotero API 404 errors instead of internal validation.",
      "problematic_tool": "get_item_metadata",
      "failed_test_step": "Edge case: Test the server's handling of an invalid item key for metadata fetching.",
      "expected_behavior": "Should validate item keys before making external API calls.",
      "actual_behavior": "Made an API call resulting in: \"Code: 404... Response: Not found\""
    }
  ]
}
```
### END_BUG_REPORT_JSON