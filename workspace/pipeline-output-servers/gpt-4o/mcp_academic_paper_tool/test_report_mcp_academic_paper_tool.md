# 📄 Test Report for Academic Paper MCP Server

---

## 1. Test Summary

- **Server:** `academic_paper_mcp`
- **Objective:** The server provides tools to search and retrieve academic paper data from external sources like Semantic Scholar and Crossref. It supports keyword-based searches, topic filtering with year ranges, and detailed paper information lookup.
- **Overall Result:** ❌ Critical failures identified
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

### 🔍 Tool: `search_papers`

#### Step: Happy path: Search for papers related to 'machine learning' with a limit of 5 results.
- **Tool:** `search_papers`
- **Parameters:** `{ "keywords": "machine learning", "limit": 5 }`
- **Status:** ❌ Failure
- **Result:** `"error": "Cannot send a request, as the client has been closed."`

#### Step: Edge case: Test server behavior when keywords are empty.
- **Tool:** `search_papers`
- **Parameters:** `{ "keywords": "", "limit": 5 }`
- **Status:** ❌ Failure
- **Result:** `"error": "Cannot send a request, as the client has been closed."`

#### Step: Edge case: Test server handling of invalid (negative) limit value.
- **Tool:** `search_papers`
- **Parameters:** `{ "keywords": "deep learning", "limit": -1 }`
- **Status:** ❌ Failure
- **Result:** `"error": "Cannot send a request, as the client has been closed."`

---

### 📄 Tool: `fetch_paper_details`

#### Step: Dependent call: Fetch detailed information about the first paper returned by search_papers using its DOI from Semantic Scholar.
- **Tool:** `fetch_paper_details`
- **Parameters:** `{ "paper_id": null, "source": "Semantic Scholar" }`
- **Status:** ❌ Failure
- **Result:** `"A required parameter resolved to None, likely due to a failure in a dependency."`

#### Step: Edge case: Test server handling of unsupported source input.
- **Tool:** `fetch_paper_details`
- **Parameters:** `{ "paper_id": "10.1145/invalid-doi", "source": "Invalid Source" }`
- **Status:** ❌ Failure
- **Result:** `"error": "Invalid source specified. Use 'Semantic Scholar' or 'Crossref'."`

#### Step: Edge case: Attempt to fetch details for an invalid DOI.
- **Tool:** `fetch_paper_details`
- **Parameters:** `{ "paper_id": "invalid.doi.12345", "source": "Semantic Scholar" }`
- **Status:** ❌ Failure
- **Result:** `"error": "Cannot send a request, as the client has been closed."`

---

### 🧠 Tool: `search_by_topic`

#### Step: Happy path with filtering: Search for AI-related papers between 2015 and 2020 with a limit of 3 results.
- **Tool:** `search_by_topic`
- **Parameters:** `{ "topic": "artificial intelligence", "year_range": [2015, 2020], "limit": 3 }`
- **Status:** ❌ Failure
- **Result:** `"error": "Cannot send a request, as the client has been closed."`

#### Step: Happy path without year filter: Search for neural network papers with default year range.
- **Tool:** `search_by_topic`
- **Parameters:** `{ "topic": "neural networks", "limit": 4 }`
- **Status:** ❌ Failure
- **Result:** `"error": "Cannot send a request, as the client has been closed."`

#### Step: Edge case: Search for papers in a future year range that likely returns no results.
- **Tool:** `search_by_topic`
- **Parameters:** `{ "topic": "quantum computing", "year_range": [2050, 2060], "limit": 2 }`
- **Status:** ❌ Failure
- **Result:** `"error": "Cannot send a request, as the client has been closed."`

---

### 🔄 Tool: Dependent Calls (via placeholders)

#### Step: Dependent call: Fetch details for the first paper in the topic search using Crossref as the source.
- **Tool:** `fetch_paper_details`
- **Parameters:** `{ "paper_id": null, "source": "Crossref" }`
- **Status:** ❌ Failure
- **Result:** `"A required parameter resolved to None, likely due to a failure in a dependency."`

---

## 4. Analysis and Findings

### Functionality Coverage
All three main functionalities (`search_papers`, `fetch_paper_details`, `search_by_topic`) were tested across various scenarios including happy paths, edge cases, and dependent operations.

### Identified Issues

1. **Client Already Closed Before Requests**
   - All tests failed with the error: `"Cannot send a request, as the client has been closed."`
   - This indicates that the `httpx.AsyncClient()` instance is being closed before it's used, likely due to the placement of `asyncio.run(async_client.aclose())` **before** the server starts in the `if __name__ == "__main__"` block.
   - **Impact:** No actual HTTP requests can be made; all tool calls fail silently.

2. **No Input Validation in Some Cases**
   - While negative limit values and empty keywords are handled gracefully in some tools (e.g., `fetch_paper_details` correctly rejects invalid sources), others simply pass them to the API without validation, leading to potential unnecessary requests.

3. **Dependent Call Failures**
   - Since the initial search steps failed, dependent steps relying on placeholder resolution also failed due to missing inputs.
   - **Impact:** Cascading failures across test suite.

### Stateful Operations
The server does not maintain state outside of individual tool calls. However, since placeholder resolution depends on prior successful executions, the cascading failures prevented testing of inter-step dependencies.

### Error Handling
- **Positive:** The server correctly validates source input in `fetch_paper_details` and returns a clear message.
- **Negative:** Most errors stem from internal misconfiguration (closed client), which should be caught at startup rather than during runtime.
- **Improvement Needed:** Better early validation of configuration and initialization steps.

---

## 5. Conclusion and Recommendations

### Conclusion
The server's core functionality was never reached due to premature closure of the HTTP client. As a result, **all tests failed**, and no meaningful interaction with external APIs occurred.

### Recommendations
1. ✅ **Fix Client Initialization Order**
   - Move `asyncio.run(async_client.aclose())` after `mcp.run()` to ensure the client remains open during operation.

2. ✅ **Add Early Configuration Validation**
   - Validate that the proxy environment variables and async client are properly configured before starting the server loop.

3. ✅ **Improve Logging**
   - Add debug logs during initialization to catch misconfigurations earlier.

4. ✅ **Input Validation**
   - Enhance validation for parameters like `keywords` and `limit` to prevent sending invalid queries to upstream services.

5. ✅ **Error Recovery Strategy**
   - Implement retry logic or better fallbacks for failed requests, especially for dependent calls.

---

### BUG_REPORT_JSON
```json
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "Async HTTP client is closed before server starts, preventing any API requests.",
      "problematic_tool": "ALL",
      "failed_test_step": "Happy path: Search for papers related to 'machine learning' with a limit of 5 results.",
      "expected_behavior": "The server should perform the requested search and return results.",
      "actual_behavior": "\"error\": \"Cannot send a request, as the client has been closed.\""
    },
    {
      "bug_id": 2,
      "description": "Dependent steps fail due to unresolved placeholders caused by previous failures.",
      "problematic_tool": "fetch_paper_details",
      "failed_test_step": "Dependent call: Fetch detailed information about the first paper returned by search_papers using its DOI from Semantic Scholar.",
      "expected_behavior": "Should fetch full details if given valid DOI and source.",
      "actual_behavior": "Failed placeholder: '$outputs.search_papers_happy_path[0].doi'"
    }
  ]
}
```
### END_BUG_REPORT_JSON