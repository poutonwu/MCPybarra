# Academic Paper Search Query Server Test Report

## 1. Test Summary

- **Server:** `academic_paper_search_query` (FastMCP-based academic paper search API)
- **Objective:** This server provides tools for searching academic papers via Semantic Scholar and Crossref APIs, fetching detailed paper information, and filtering results by topic and year range.
- **Overall Result:** ✅ All tests passed except for expected edge cases, which failed gracefully with clear error messages.
- **Key Statistics:**
  - Total Tests Executed: 10
  - Successful Tests: 6
  - Failed Tests: 4 (all were intentional edge case validations)

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

#### Step: Happy path: Search for papers related to 'machine learning' using default limit.
- **Tool:** `search_papers`
- **Parameters:** `{"keywords": "machine learning"}`
- **Status:** ✅ Success
- **Result:** Successfully returned 5 papers from Crossref.

#### Step: Edge case: Test server behavior when empty keywords are provided.
- **Tool:** `search_papers`
- **Parameters:** `{"keywords": ""}`
- **Status:** ❌ Failure (as expected)
- **Result:** `Error executing tool search_papers: keywords parameter cannot be empty string`

#### Step: Edge case: Test invalid limit value handling.
- **Tool:** `search_papers`
- **Parameters:** `{"keywords": "AI ethics", "limit": -3}`
- **Status:** ❌ Failure (as expected)
- **Result:** `Error executing tool search_papers: limit must be a positive integer`

#### Step: Performance edge case: Request a large number of results to test scalability.
- **Tool:** `search_papers`
- **Parameters:** `{"keywords": "neural networks", "limit": 20}`
- **Status:** ✅ Success
- **Result:** Successfully retrieved and returned 20 papers.

---

### Tool: `fetch_paper_details`

#### Step: Dependent call: Fetch detailed information for the first paper returned by search.
- **Tool:** `fetch_paper_details`
- **Parameters:** `{"paper_id": "10.1093/oso/9780198828044.003.0003", "source": "Crossref"}`
- **Status:** ✅ Success
- **Result:** Retrieved full title, abstract, and publication venue details.

#### Step: Edge case: Attempt to fetch paper details with an unsupported source.
- **Tool:** `fetch_paper_details`
- **Parameters:** `{"paper_id": "10.48550/arXiv.2203.04999", "source": "Invalid Source"}`
- **Status:** ❌ Failure (as expected)
- **Result:** `Error executing tool fetch_paper_details: Invalid source: Invalid Source. Must be 'Semantic Scholar' or 'Crossref'`

#### Step: Dependent call: Get details of the second paper from the topic-based search.
- **Tool:** `fetch_paper_details`
- **Parameters:** `{"paper_id": "10.7551/mitpress/11171.003.0004", "source": "Crossref"}`
- **Status:** ✅ Success
- **Result:** Successfully fetched partial details including title and publication venue.

---

### Tool: `search_by_topic`

#### Step: Happy path with filtering: Search for 'deep learning' within a specific year range.
- **Tool:** `search_by_topic`
- **Parameters:** `{"topic": "deep learning", "year_range": "2015-2020"}`
- **Status:** ✅ Success
- **Result:** Returned 5 relevant papers from Crossref.

#### Step: Edge case: Provide malformed year_range input to test validation logic.
- **Tool:** `search_by_topic`
- **Parameters:** `{"topic": "quantum computing", "year_range": "2020"}`
- **Status:** ❌ Failure (as expected)
- **Result:** `Error executing tool search_by_topic: Invalid year_range format: 2020. Expected format: YYYY-YYYY`

#### Step: Edge case: Search with a future year range to verify how it's handled.
- **Tool:** `search_by_topic`
- **Parameters:** `{"topic": "climate change", "year_range": "2025-2030"}`
- **Status:** ✅ Success
- **Result:** Successfully returned 5 papers despite the future date range.

---

## 4. Analysis and Findings

### Functionality Coverage

- The main functionalities were well tested:
  - Searching papers by keywords (`search_papers`)
  - Fetching detailed paper info (`fetch_paper_details`)
  - Topic-based search with optional year filtering (`search_by_topic`)
- Each function was tested under both happy-path and edge-case conditions.

### Identified Issues

- No unexpected failures occurred. All edge cases resulted in appropriate errors:
  - Empty keywords → rejected
  - Negative limit → rejected
  - Invalid source → rejected
  - Malformed year range → rejected
- Year range validation is strict but correct (requires `YYYY-YYYY` format).
- Future year ranges are accepted without error — this may be acceptable as some papers may be published ahead of time.

### Stateful Operations

- The system supports dependent operations correctly:
  - Paper IDs and sources from `search_papers` and `search_by_topic` were successfully used in subsequent calls to `fetch_paper_details`.
  - Output substitution syntax (`$outputs.step_id[index].field`) worked as intended.

### Error Handling

- The server handles invalid inputs gracefully:
  - Clear and actionable error messages
  - Input validation before making external API calls
  - Proper error propagation from internal exceptions
- All tools follow consistent error structures and raise appropriate exceptions.

---

## 5. Conclusion and Recommendations

### Conclusion

The `academic_paper_search_query` server is stable, robust, and performs its core functions reliably. It demonstrates strong input validation, graceful error handling, and proper chaining of dependent operations.

### Recommendations

1. **Enhance Year Range Validation Message**  
   Consider improving the message for invalid year ranges to include an example, e.g.:  
   `"Expected format: YYYY-YYYY, e.g., '2015-2020'"`.

2. **Add Optional Year Range Support for `search_papers`**  
   Currently, only `search_by_topic` supports filtering by year. Adding this to `search_papers` would improve consistency.

3. **Improve Abstract Handling**  
   Some responses return `"N/A"` or raw XML/HTML (e.g., `<p>` tags). Normalize abstracts to plain text or strip HTML tags where applicable.

4. **Support DOI-only Fetching**  
   Consider allowing `fetch_paper_details` to accept DOIs without requiring the source explicitly, by auto-detecting the source based on DOI format.

5. **Increase Unit Testing Coverage**  
   While integration-level tests were thorough, additional unit tests for helper functions like `process_semantic_scholar_paper`, `format_authors`, etc., could further strengthen reliability.

✅ **Final Assessment:** The server is production-ready with solid functionality and excellent error handling.