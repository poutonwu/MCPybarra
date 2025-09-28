# Test Report: mcp_zotero_library_manager

---

## 1. Test Summary

- **Server:** `mcp_zotero_library_manager`
- **Objective:** The server acts as a Zotero library interface, offering tools to search items and retrieve metadata or full-text content for research management purposes.
- **Overall Result:** **Failed with critical issues**
- **Key Statistics:**
  - Total Tests Executed: 11
  - Successful Tests: 1
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

#### Step: Happy path: Search for items with 'machine learning' in the title using default search_type.
- **Tool:** `search_items`
- **Parameters:** `{ "query": "machine learning" }`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Failed to perform search: Invalid 'qmode' value 'title'

---

#### Step: Happy path: Search for items authored by Andrew Ng.
- **Tool:** `search_items`
- **Parameters:** `{ "query": "Andrew Ng", "search_type": "creator" }`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Failed to perform search: Invalid 'qmode' value 'author'

---

#### Step: Happy path: Search for items published in 2020.
- **Tool:** `search_items`
- **Parameters:** `{ "query": "2020", "search_type": "year" }`
- **Status:** ❌ Failure
- **Result:** Error executing tool `search_items`: Failed to perform search: Invalid 'qmode' value 'year'

---

#### Step: Happy path: Search for items containing 'neural networks' in full-text content.
- **Tool:** `search_items`
- **Parameters:** `{ "query": "neural networks", "search_type": "fulltext" }`
- **Status:** ✅ Success (partial due to truncation)
- **Result:** Successfully returned item data (truncated). This indicates that only the `fulltext` search mode works correctly.

---

#### Step: Edge case: Test server behavior when query is empty.
- **Tool:** `search_items`
- **Parameters:** `{ "query": "", "search_type": "title" }`
- **Status:** ❌ Failure
- **Result:** Error: "Valid search query must be provided."

---

#### Step: Edge case: Test server's handling of invalid `search_type` parameter.
- **Tool:** `search_items`
- **Parameters:** `{ "query": "quantum computing", "search_type": "invalidtype" }`
- **Status:** ❌ Failure
- **Result:** Error: "Invalid search_type: invalidtype. Must be one of ['title', 'creator', 'year', 'fulltext']."

---

### Tool: `get_item_metadata`

#### Step: Dependent call: Retrieve metadata for the first item returned from the search.
- **Tool:** `get_item_metadata`
- **Parameters:** `{ "item_key": null }`
- **Status:** ❌ Failure
- **Result:** A required parameter resolved to None, likely due to a failure in a dependency.

---

#### Step: Edge case: Attempt to get metadata for a non-existent item key.
- **Tool:** `get_item_metadata`
- **Parameters:** `{ "item_key": "invalid-key-123" }`
- **Status:** ❌ Failure
- **Result:** Error: "Failed to fetch metadata for item invalid-key-123: Code: 404 — Not found"

---

### Tool: `get_item_fulltext`

#### Step: Dependent call: Attempt to retrieve full-text content of the first result (may fail if not an attachment).
- **Tool:** `get_item_fulltext`
- **Parameters:** `{ "item_key": null }`
- **Status:** ❌ Failure
- **Result:** A required parameter resolved to None, likely due to a failure in a dependency.

---

#### Step: Edge case: Attempt to get fulltext for a non-existent item key.
- **Tool:** `get_item_fulltext`
- **Parameters:** `{ "item_key": "invalid-key-456" }`
- **Status:** ❌ Failure
- **Result:** Error: "Failed to fetch fulltext for item invalid-key-456: Code: 404 — Not found"

---

#### Step: Edge case: Attempt to get fulltext on an item that is not an attachment.
- **Tool:** `get_item_fulltext`
- **Parameters:** `{ "item_key": null }`
- **Status:** ❌ Failure
- **Result:** A required parameter resolved to None, likely due to a failure in a dependency.

---

## 4. Analysis and Findings

### Functionality Coverage
- The test suite covers all major functionalities:
  - Searching items by title, author, year, and full-text
  - Retrieving metadata
  - Extracting full-text content
- However, most tests failed due to incorrect API usage.

### Identified Issues

1. **Incorrect Mapping of `qmode` Parameters**
   - All searches except `fulltext` failed because the `qmode` values used (`title`, `author`, `year`) are invalid according to the Zotero API.
   - Only `everything` was accepted in the successful `fulltext` search.
   - This suggests a mismatch between the expected Zotero API parameters and what the code sends.

2. **Parameter Resolution Failures in Dependent Steps**
   - Several steps attempted to use output from previous steps but failed because earlier steps did not succeed.
   - This cascaded failures across dependent tests.

3. **Error Handling for Non-Existent Items**
   - Both `get_item_metadata` and `get_item_fulltext` correctly handle invalid keys by raising HTTP 404 errors.
   - Error messages are clear and informative.

4. **Input Validation**
   - Input validation for queries and search types is robust at the server level.
   - Empty queries and invalid search types are caught early with meaningful error messages.

### Stateful Operations
- The test suite attempts to chain results (e.g., retrieving metadata after a search), but since initial searches failed, dependent steps could not proceed.
- This highlights correct implementation of stateful logic in theory, but failure in practice due to upstream errors.

### Error Handling
- Error handling is generally strong:
  - Clear and descriptive exceptions are raised.
  - Input validation prevents misuse.
- However, there is room for improvement in mapping Zotero API parameters accurately.

---

## 5. Conclusion and Recommendations

The server shows good design principles and solid error handling, but suffers from **critical bugs in API parameter mapping**, which prevent core functionality from working properly.

### Recommendations:

1. **Fix `qmode` Parameter Mapping**
   - Replace `title`, `author`, and `year` with valid Zotero API values like `title` → `everything`, `author` → `creator`, etc.
   - Update the docstring and internal logic accordingly.

2. **Improve Documentation**
   - Clarify how each `search_type` maps to Zotero’s actual parameters.
   - Note any limitations (e.g., full-text search requires indexing).

3. **Enhance Dependency Management in Testing**
   - Add fallbacks or mock responses for dependent steps so that downstream functionality can still be tested independently.

4. **Consider Mocking for Integration Testing**
   - Use mocks or fixtures for Zotero API responses to ensure consistent testing without hitting live endpoints.

---

### BUG_REPORT_JSON

```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "Incorrect qmode parameter values used for Zotero API search.",
      "problematic_tool": "search_items",
      "failed_test_step": "Happy path: Search for items with 'machine learning' in the title using default search_type.",
      "expected_behavior": "Search should execute successfully using the specified search_type.",
      "actual_behavior": "Error executing tool search_items: Failed to perform search: Invalid 'qmode' value 'title'"
    },
    {
      "bug_id": 2,
      "description": "Author search fails due to invalid qmode parameter.",
      "problematic_tool": "search_items",
      "failed_test_step": "Happy path: Search for items authored by Andrew Ng.",
      "expected_behavior": "Should return items authored by Andrew Ng.",
      "actual_behavior": "Error executing tool search_items: Failed to perform search: Invalid 'qmode' value 'author'"
    },
    {
      "bug_id": 3,
      "description": "Year search fails due to invalid qmode parameter.",
      "problematic_tool": "search_items",
      "failed_test_step": "Happy path: Search for items published in 2020.",
      "expected_behavior": "Should return items published in 2020.",
      "actual_behavior": "Error executing tool search_items: Failed to perform search: Invalid 'qmode' value 'year'"
    }
  ]
}
```

### END_BUG_REPORT_JSON