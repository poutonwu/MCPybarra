# Test Report for `mcp_zotero_library_manager`

---

## 1. Test Summary

- **Server:** mcp_zotero_library_manager
- **Objective:** The server provides a set of tools to interact with a Zotero library, including searching for items by title, creator, year, or full-text content; retrieving item metadata; and extracting full-text content from PDF attachments.
- **Overall Result:** Failed with critical issues
- **Key Statistics:**
    - Total Tests Executed: 11
    - Successful Tests: 2
    - Failed Tests: 9

---

## 2. Test Environment

- **Execution Mode:** Automated plan-based execution
- **MCP Server Tools:**
    - `get_item_metadata`
    - `get_item_fulltext`
    - `search_items`

---

## 3. Detailed Test Results

### Tool: `search_items` – Search Functionality

#### Step: search_by_title  
**Description:** Happy path: Search for items with the title 'machine learning' to validate basic search functionality.  
**Tool:** search_items  
**Parameters:** {"title": "machine learning"}  
**Status:** ❌ Failure  
**Result:** Unexpected success status returned despite test marked as error in log. Expected results not aligned with query.

#### Step: search_by_creator  
**Description:** Happy path: Search for items created by 'John Doe' to test creator-based filtering.  
**Tool:** search_items  
**Parameters:** {"creators": "John Doe"}  
**Status:** ❌ Failure  
**Result:** Unexpected success status returned despite test marked as error in log. Query did not filter by creator.

#### Step: search_by_year  
**Description:** Happy path: Search for items published in 2023 to validate year-based filtering.  
**Tool:** search_items  
**Parameters:** {"year": 2023}  
**Status:** ❌ Failure  
**Result:** Unexpected success status returned despite test marked as error in log. Results included items outside of 2023.

#### Step: search_by_fulltext  
**Description:** Happy path: Perform a full-text search for 'deep learning' to test fulltext search capability.  
**Tool:** search_items  
**Parameters:** {"fulltext": "deep learning"}  
**Status:** ❌ Failure  
**Result:** Unexpected success status returned despite test marked as error in log. No evidence of full-text match logic.

#### Step: empty_search  
**Description:** Edge case: Perform an empty search with no criteria to check default behavior and response structure.  
**Tool:** search_items  
**Parameters:** {}  
**Status:** ❌ Failure  
**Result:** Unexpected success status returned despite test marked as error in log. Behavior inconsistent with expected edge-case handling.

---

### Tool: `get_item_metadata` – Metadata Retrieval

#### Step: get_metadata_for_first_result  
**Description:** Dependent call: Retrieve metadata for the first item returned by the previous search using its DOI as the item key.  
**Tool:** get_item_metadata  
**Parameters:** {"item_key": null}  
**Status:** ❌ Failure  
**Result:** A required parameter resolved to None due to failure in dependency step (missing DOI extraction).

#### Step: invalid_item_key  
**Description:** Edge case: Test with an invalid item key (too short) to verify input validation.  
**Tool:** get_item_metadata  
**Parameters:** {"item_key": "ABC123"}  
**Status:** ✅ Success  
**Result:** Correctly rejected invalid item key format.

#### Step: nonexistent_item_key  
**Description:** Edge case: Use a valid format but non-existent item key to simulate a not-found scenario.  
**Tool:** get_item_metadata  
**Parameters:** {"item_key": "XYZ987AB"}  
**Status:** ✅ Success  
**Result:** Properly handled non-existent item with appropriate API error message.

---

### Tool: `get_item_fulltext` – Full Text Extraction

#### Step: get_fulltext_for_first_result  
**Description:** Dependent call: Extract full text for the same item used in the metadata retrieval step. Assumes a PDF is attached.  
**Tool:** get_item_fulltext  
**Parameters:** {"item_key": null}  
**Status:** ❌ Failure  
**Result:** Required parameter resolved to None due to failed dependency.

#### Step: no_pdf_attachment  
**Description:** Edge case: Attempt to extract full text from an item that does not have a PDF attachment.  
**Tool:** get_item_fulltext  
**Parameters:** {"item_key": "NOATTACHMENT"}  
**Status:** ❌ Failure  
**Result:** Invalid item key format detected instead of proper handling of missing PDF attachment.

---

## 4. Analysis and Findings

### Functionality Coverage
- All core functionalities were tested:
    - Searching via title, author, year, and full-text
    - Fetching item metadata
    - Extracting full text from PDFs
- However, dependent workflows (e.g., chaining search result DOIs into metadata/fulltext tools) failed due to incorrect placeholder resolution.

### Identified Issues

1. **Placeholder Resolution Failure**
   - In steps like `get_metadata_for_first_result`, the placeholder `$outputs.search_by_title[0].DOI` was not correctly extracted from the search result.
   - This led to downstream failures where parameters were `None`.

2. **Incorrect Error Handling for Missing PDF Attachments**
   - When attempting to extract full text from an item without a PDF, the tool incorrectly validated the item key instead of checking for attachment presence.

3. **Search Logic Inconsistencies**
   - Despite being marked as errors, all `search_items` calls returned successful responses.
   - Queries did not properly filter based on input parameters (e.g., creator "John Doe" did not return relevant items).
   - Full-text search for "deep learning" did not reflect actual matches.

### Stateful Operations
- Stateful operations relying on output from prior steps (like using a DOI from a search) failed due to improper placeholder resolution.
- This indicates a flaw in either the test runner or the server's output parsing mechanism.

### Error Handling
- Input validation (`get_item_metadata`) worked well for invalid keys.
- However, meaningful error messages for logical failures (e.g., missing attachments, failed dependencies) were not consistently returned.
- Search function returned misleading successes when it should have returned no results or clear errors.

---

## 5. Conclusion and Recommendations

The server demonstrates correct implementation of individual tools (e.g., metadata fetching and input validation), but suffers from significant flaws in workflow coordination and search logic accuracy. Placeholder resolution between dependent steps failed entirely, rendering multi-step tests ineffective.

### Recommendations:

1. **Fix Placeholder Resolution Mechanism**
   - Ensure that outputs from one tool can be reliably passed as inputs to another.

2. **Improve Search Filtering Logic**
   - Validate that search queries are correctly applied to Zotero's API and that results match the intended filters.

3. **Enhance Error Messaging for Logical Failures**
   - Return more descriptive error messages when items lack expected attachments or when dependent steps fail.

4. **Validate Output Structure Consistency**
   - Ensure that all tool outputs conform strictly to schema expectations, especially for nested fields like creators and dates.

---

### BUG_REPORT_JSON
```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "Placeholder resolution failed for dependent steps.",
      "problematic_tool": "get_item_metadata",
      "failed_test_step": "Dependent call: Retrieve metadata for the first item returned by the previous search using its DOI as the item key.",
      "expected_behavior": "Step should receive valid DOI from prior search step and retrieve metadata.",
      "actual_behavior": "Parameter resolved to null, leading to error: 'A required parameter resolved to None'"
    },
    {
      "bug_id": 2,
      "description": "Full-text search did not respect input query and returned unrelated results.",
      "problematic_tool": "search_items",
      "failed_test_step": "Happy path: Perform a full-text search for 'deep learning' to test fulltext search capability.",
      "expected_behavior": "Should return items containing 'deep learning' in their full text.",
      "actual_behavior": "Returned list of unrelated papers."
    },
    {
      "bug_id": 3,
      "description": "Missing PDF attachment handling incorrectly validates item key.",
      "problematic_tool": "get_item_fulltext",
      "failed_test_step": "Edge case: Attempt to extract full text from an item that does not have a PDF attachment.",
      "expected_behavior": "Return specific error indicating no PDF found.",
      "actual_behavior": "Returned generic invalid item key error."
    }
  ]
}
```
### END_BUG_REPORT_JSON