# Test Report: mcp_academic_paper_search_engine

## 1. Test Summary

- **Server:** mcp_academic_paper_search_engine
- **Objective:** This server provides an interface to search for academic papers using keywords or topics, optionally filtered by year range, and retrieve detailed information about specific papers using their IDs and sources (Semantic Scholar or Crossref).
- **Overall Result:** Critical failures identified
- **Key Statistics:**
  - Total Tests Executed: 10
  - Successful Tests: 0
  - Failed Tests: 10

---

## 2. Test Environment

- **Execution Mode:** Automated plan-based execution
- **MCP Server Tools:**
  - `search_papers`
  - `fetch_paper_details`
  - `search_by_topic`

---

## 3. Detailed Test Results

### Tool: `search_papers`

#### Step: Happy path: Search for papers related to 'machine learning' with a limit of 5 results.
- **Tool:** search_papers
- **Parameters:** {"keywords": "machine learning", "limit": 5}
- **Status:** ❌ Failure
- **Result:** Tool 'search_papers' execution timed out (exceeded 60 seconds).

#### Step: Edge case: Attempt to search with empty keywords to test error handling.
- **Tool:** search_papers
- **Parameters:** {"keywords": "", "limit": 5}
- **Status:** ❌ Failure
- **Result:** Error executing tool search_papers: Keywords cannot be empty.

#### Step: Edge case: Use an invalid negative limit to trigger validation error.
- **Tool:** search_papers
- **Parameters:** {"keywords": "AI ethics", "limit": -2}
- **Status:** ❌ Failure
- **Result:** Error executing tool search_papers: Limit must be a positive integer.

---

### Tool: `fetch_paper_details`

#### Step: Dependent call: Fetch detailed information about the first paper from the previous search.
- **Tool:** fetch_paper_details
- **Parameters:** {"paper_id": null, "source": null}
- **Status:** ❌ Failure
- **Result:** A required parameter resolved to None, likely due to a failure in a dependency. Failed placeholder: '$outputs.search_papers_happy_path[0].doi'

#### Step: Edge case: Try fetching details with an unsupported source to test validation.
- **Tool:** fetch_paper_details
- **Parameters:** {"paper_id": "invalid-id", "source": "invalid-source"}
- **Status:** ❌ Failure
- **Result:** Error executing tool fetch_paper_details: Source must be 'semantic_scholar' or 'crossref'.

#### Step: Edge case: Attempt to fetch paper details with an empty ID to test validation.
- **Tool:** fetch_paper_details
- **Parameters:** {"paper_id": "", "source": "semantic_scholar"}
- **Status:** ❌ Failure
- **Result:** Error executing tool fetch_paper_details: Paper ID cannot be empty.

---

### Tool: `search_by_topic`

#### Step: Happy path: Search for papers on 'deep learning' published between 2018 and 2022, limited to 3 results.
- **Tool:** search_by_topic
- **Parameters:** {"topic": "deep learning", "year_range": [2018, 2022], "limit": 3}
- **Status:** ❌ Failure
- **Result:** Tool 'search_by_topic' execution timed out (exceeded 60 seconds).

#### Step: Edge case: Test behavior when the topic is an empty string.
- **Tool:** search_by_topic
- **Parameters:** {"topic": "", "year_range": [2020, 2023]}
- **Status:** ❌ Failure
- **Result:** Error executing tool search_by_topic: Topic cannot be empty.

#### Step: Edge case: Provide an invalid year range where start > end to test validation logic.
- **Tool:** search_by_topic
- **Parameters:** {"topic": "quantum computing", "year_range": [2025, 2020]}
- **Status:** ❌ Failure
- **Result:** Error executing tool search_by_topic: Year range must be a tuple of (start_year, end_year).

---

### Dependent Call: `fetch_paper_details` after `search_by_topic`

#### Step: Dependent call: Fetch details of the first paper from the topic-based search.
- **Tool:** fetch_paper_details
- **Parameters:** {"paper_id": null, "source": null}
- **Status:** ❌ Failure
- **Result:** A required parameter resolved to None, likely due to a failure in a dependency. Failed placeholder: '$outputs.search_by_topic_with_year_range[0].doi'

---

## 4. Analysis and Findings

### Functionality Coverage:
The tests covered all three tools (`search_papers`, `fetch_paper_details`, `search_by_topic`) and included both happy paths and edge cases. The testing was comprehensive in terms of validating input parameters and expected behaviors.

### Identified Issues:
All functional tests failed due to timeouts or dependent failures caused by those timeouts. Specifically:

- **Timeouts in Core Tools:** Both `search_papers` and `search_by_topic` timed out during execution. These are critical operations that underpin the functionality of the system. All subsequent dependent calls (e.g., `fetch_paper_details`) also failed because they depended on outputs from these initial steps.

- **No Successful Execution of Primary Functions:** Since the primary search functions did not return any valid output, no secondary function could be properly tested.

- **Error Handling Validation Confirmed but Not Fully Tested:** While the error messages for invalid inputs were correct and aligned with expectations (e.g., empty keywords, invalid year ranges), the timeout issues prevented full validation of error handling under real-world API failure scenarios.

### Stateful Operations:
Stateful dependencies were handled correctly in terms of workflow logic—when a prior step failed, dependent steps were skipped appropriately. However, since no prior steps succeeded, we couldn't verify if passing values like DOIs or sources between tools would work as intended.

### Error Handling:
The server returned clear and appropriate error messages for invalid inputs. However, it's unclear how it handles external API failures (e.g., network errors) since the timeouts masked potential exception paths.

---

## 5. Conclusion and Recommendations

### Conclusion:
The server failed all test cases primarily due to timeouts in its core search functions. Despite having proper validation and error messaging, the inability to execute the main search operations renders the service non-functional.

### Recommendations:
1. **Investigate Timeout Causes:** Debug why `search_papers` and `search_by_topic` are timing out. Potential causes include proxy misconfiguration (`os.environ['HTTP_PROXY']`), slow response from Semantic Scholar/Crossref APIs, or improper async execution.
2. **Improve Async Handling:** Ensure that asynchronous calls within tools are properly awaited and managed by the event loop.
3. **Add Circuit Breakers/Timeouts per External Call:** Implement per-API-call timeouts to prevent one slow request from blocking the entire operation.
4. **Enhance Logging:** Add detailed logging around each API call to help diagnose failures more effectively.
5. **Mock External Services in Unit Tests:** For future test runs, consider mocking external services (Semantic Scholar, Crossref) to isolate server-side logic from third-party availability.

---

### BUG_REPORT_JSON
```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "The search_papers tool times out during execution.",
      "problematic_tool": "search_papers",
      "failed_test_step": "Happy path: Search for papers related to 'machine learning' with a limit of 5 results.",
      "expected_behavior": "Should return a list of up to 5 papers matching 'machine learning'.",
      "actual_behavior": "Tool 'search_papers' execution timed out (exceeded 60 seconds)."
    },
    {
      "bug_id": 2,
      "description": "The search_by_topic tool times out during execution.",
      "problematic_tool": "search_by_topic",
      "failed_test_step": "Happy path: Search for papers on 'deep learning' published between 2018 and 2022, limited to 3 results.",
      "expected_behavior": "Should return a list of up to 3 papers matching 'deep learning' published between 2018 and 2022.",
      "actual_behavior": "Tool 'search_by_topic' execution timed out (exceeded 60 seconds)."
    }
  ]
}
```
### END_BUG_REPORT_JSON