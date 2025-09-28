# Test Report: mcp_academic_paper_search_engine

## 1. Test Summary

**Server:** `mcp_academic_paper_search_engine`  
**Objective:** This server provides an academic paper search engine that allows users to search for papers by keywords, topic, and optional year range, and retrieve detailed information about specific papers using their IDs and source. It utilizes both Semantic Scholar and Crossref APIs to fetch results.  
**Overall Result:** **Failed with critical issues** — Several core functionalities failed during testing, including timeout errors and incorrect exception handling.  
**Key Statistics:**
- Total Tests Executed: 10
- Successful Tests: 0
- Failed Tests: 10

---

## 2. Test Environment

**Execution Mode:** Automated plan-based execution  
**MCP Server Tools:**
- `search_papers`
- `fetch_paper_details`
- `search_by_topic`

---

## 3. Detailed Test Results

### Tool: `search_papers`

#### Step: Happy path: Search for 'machine learning' with a limit of 5 results.
- **Tool:** `search_papers`  
- **Parameters:** `{ "keywords": "machine learning", "limit": 5 }`  
- **Status:** ❌ Failure  
- **Result:** `"Tool 'search_papers' execution timed out (exceeded 60 seconds)."`

---

### Tool: `fetch_paper_details`

#### Step: Dependent call: Fetch detailed info for the first paper from the previous search.
- **Tool:** `fetch_paper_details`  
- **Parameters:** `{ "paper_id": null, "source": null }`  
- **Status:** ❌ Failure  
- **Result:** `"A required parameter resolved to None, likely due to a failure in a dependency. Failed placeholder: '$outputs.search_papers_happy_path[0].doi'"`

---

### Tool: `search_by_topic`

#### Step: Happy path: Search by topic 'deep learning' with a limit of 3 results.
- **Tool:** `search_by_topic`  
- **Parameters:** `{ "topic": "deep learning", "limit": 3 }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool search_by_topic: HTTPStatusError.__init__() missing 2 required keyword-only arguments: 'request' and 'response'"`

#### Step: Happy path with filtering: Search by topic 'neural networks' within year range 2010-2020.
- **Tool:** `search_by_topic`  
- **Parameters:** `{ "topic": "neural networks", "year_range": [2010, 2020], "limit": 4 }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool search_by_topic: HTTPStatusError.__init__() missing 2 required keyword-only arguments: 'request' and 'response'"`

---

### Edge Case Tests

#### Step: Edge case: Test server's handling of empty keywords in `search_papers`.
- **Tool:** `search_papers`  
- **Parameters:** `{ "keywords": "", "limit": 5 }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool search_papers: Keywords cannot be empty."`

#### Step: Edge case: Test server's handling of negative limit in `search_papers`.
- **Tool:** `search_papers`  
- **Parameters:** `{ "keywords": "quantum computing", "limit": -2 }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool search_papers: Limit must be a positive integer."`

#### Step: Edge case: Test server's handling of invalid source parameter in `fetch_paper_details`.
- **Tool:** `fetch_paper_details`  
- **Parameters:** `{ "paper_id": "some_valid_id", "source": "invalid_source" }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool fetch_paper_details: Source must be 'semantic_scholar' or 'crossref'."`

#### Step: Edge case: Test server's handling of empty `paper_id` in `fetch_paper_details`.
- **Tool:** `fetch_paper_details`  
- **Parameters:** `{ "paper_id": "", "source": "semantic_scholar" }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool fetch_paper_details: Paper ID cannot be empty."`

#### Step: Edge case: Test server's handling of empty topic in `search_by_topic`.
- **Tool:** `search_by_topic`  
- **Parameters:** `{ "topic": "", "limit": 5 }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool search_by_topic: Topic cannot be empty."`

#### Step: Edge case: Test server's handling of inverted year range in `search_by_topic`.
- **Tool:** `search_by_topic`  
- **Parameters:** `{ "topic": "robotics", "year_range": [2020, 2010] }`  
- **Status:** ❌ Failure  
- **Result:** `"Error executing tool search_by_topic: Year range must be a tuple of (start_year, end_year)."`

---

## 4. Analysis and Findings

### Functionality Coverage
- The test plan covers all major functionalities of the server, including:
  - Basic paper search (`search_papers`)
  - Detailed paper lookup (`fetch_paper_details`)
  - Topic-based search with optional year filtering (`search_by_topic`)
- Edge cases for invalid input handling were also tested.

### Identified Issues
1. **Timeout in `search_papers`**
   - **Description:** The server failed to return results within 60 seconds.
   - **Impact:** Users will experience poor performance or no results for keyword-based searches.
   - **Potential Cause:** Possibly due to proxy misconfiguration (`os.environ['HTTP_PROXY']`) or API rate limiting.

2. **Incorrect Exception Handling in `search_by_topic`**
   - **Description:** The server raises an `HTTPStatusError` without required `request` and `response` parameters.
   - **Impact:** Errors are not logged or handled properly, leading to unclear debugging.
   - **Potential Cause:** The exception is raised incorrectly in the `search_by_topic` function.

3. **Failure to Handle Dependent Calls**
   - **Description:** The `fetch_paper_details` call failed because it relied on a previous step that timed out.
   - **Impact:** Chained operations will fail if any prior step fails, even if the current step is valid.

4. **Input Validation Works, but Execution Fails**
   - **Description:** Input validation (e.g., empty keywords, invalid source) works correctly, but actual API execution fails.
   - **Impact:** Valid inputs are accepted but not processed correctly, leading to poor user experience.

### Stateful Operations
- The server **did not handle dependent operations** properly due to the failure of the initial `search_papers` call, which prevented the dependent `fetch_paper_details` step from executing.

### Error Handling
- The server **does perform input validation** and returns meaningful messages for invalid inputs.
- However, **API-level errors** (e.g., timeouts, malformed exceptions) are not handled correctly, leading to unclear error messages and uncaught exceptions.

---

## 5. Conclusion and Recommendations

### Conclusion
The server failed critical tests, particularly in handling API requests and raising exceptions properly. While input validation is implemented, core functionalities like searching for papers and fetching details did not execute successfully.

### Recommendations
1. **Fix Exception Handling in `search_by_topic`:**
   - Ensure `HTTPStatusError` is raised with both `request` and `response` parameters.
2. **Improve Timeout Handling:**
   - Investigate proxy configuration or add timeout handling in API calls.
3. **Enhance Error Recovery:**
   - Add retry logic or fallback mechanisms for failed API calls.
4. **Ensure Dependent Steps Can Execute Independently:**
   - Allow test cases to run independently, or mock outputs from prior steps during testing.
5. **Improve Logging:**
   - Log detailed error information to help diagnose failures like timeouts or API errors.

---

### BUG_REPORT_JSON
```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "The 'search_papers' tool times out after 60 seconds and fails to return results.",
      "problematic_tool": "search_papers",
      "failed_test_step": "Happy path: Search for 'machine learning' with a limit of 5 results.",
      "expected_behavior": "Should return a list of up to 5 papers related to 'machine learning'.",
      "actual_behavior": "Tool 'search_papers' execution timed out (exceeded 60 seconds)."
    },
    {
      "bug_id": 2,
      "description": "The 'search_by_topic' tool raises an improperly constructed HTTPStatusError.",
      "problematic_tool": "search_by_topic",
      "failed_test_step": "Happy path: Search by topic 'deep learning' with a limit of 3 results.",
      "expected_behavior": "Should return a list of up to 3 papers related to 'deep learning'.",
      "actual_behavior": "Error executing tool search_by_topic: HTTPStatusError.__init__() missing 2 required keyword-only arguments: 'request' and 'response'"
    },
    {
      "bug_id": 3,
      "description": "The 'fetch_paper_details' tool fails due to missing parameters from a failed dependency.",
      "problematic_tool": "fetch_paper_details",
      "failed_test_step": "Dependent call: Fetch detailed info for the first paper from the previous search.",
      "expected_behavior": "Should return detailed information for the first paper from the previous search.",
      "actual_behavior": "A required parameter resolved to None, likely due to a failure in a dependency. Failed placeholder: '$outputs.search_papers_happy_path[0].doi'"
    }
  ]
}
```
### END_BUG_REPORT_JSON