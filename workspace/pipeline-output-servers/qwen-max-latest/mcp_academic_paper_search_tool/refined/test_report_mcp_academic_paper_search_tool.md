# Academic Paper Search Server Test Report

## 1. Test Summary

**Server:** academic_paper_search  
**Objective:** The server provides tools for searching and retrieving academic paper information from Semantic Scholar and Crossref sources, including basic search, detailed lookup by ID, and topic-based filtering with optional year ranges.  
**Overall Result:** Critical failures identified  
**Key Statistics:**
- Total Tests Executed: 11
- Successful Tests: 0
- Failed Tests: 11

All tests failed due to timeouts or dependency resolution issues.

## 2. Test Environment

**Execution Mode:** Automated plan-based execution  
**MCP Server Tools:**
- `search_papers_tool`
- `fetch_paper_details_tool`
- `search_by_topic_tool`

## 3. Detailed Test Results

### Tool: search_papers_tool

#### Step: Happy path: Search for papers related to 'machine learning' with max results of 5.
**Parameters:** {"keywords": "machine learning", "max_results": 5}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Tool 'search_papers_tool' execution timed out (exceeded 60 seconds).

#### Step: Edge case: Test server behavior when keywords are empty.
**Parameters:** {"keywords": "", "max_results": 5}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Error in search_papers_tool: Keywords cannot be empty or blank.

#### Step: Edge case: Test server behavior when max_results is out of range (less than 1).
**Parameters:** {"keywords": "neural networks", "max_results": 0}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Error in search_papers_tool: max_results must be between 1 and 100 inclusive.

### Tool: fetch_paper_details_tool

#### Step: Dependent call: Use the DOI from the first result of the previous search to fetch detailed paper information from Semantic Scholar.
**Parameters:** {"paper_id": null, "source": "Semantic Scholar"}  
**Status:** ❌ Failure  
**Result:** A required parameter resolved to None, likely due to a failure in a dependency.

#### Step: Edge case: Attempt to fetch details using an invalid source name.
**Parameters:** {"paper_id": "10.1093/mind/lix.236.433", "source": "Invalid Source"}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Error in fetch_paper_details_tool: Error while fetching paper details: Invalid source. Please choose 'Semantic Scholar' or 'Crossref'.

#### Step: Edge case: Fetch details using a DOI that likely does not exist.
**Parameters:** {"paper_id": "nonexistent-doi-12345", "source": "Crossref"}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Error in fetch_paper_details_tool: Error while fetching paper details: 'NoneType' object has no attribute 'get'

### Tool: search_by_topic_tool

#### Step: Happy path with optional filtering: Search for AI ethics papers between 2015 and 2020, limited to 3 results.
**Parameters:** {"topic_keywords": "AI ethics", "year_range_start": 2015, "year_range_end": 2020, "max_results": 3}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Tool 'search_by_topic_tool' execution timed out (exceeded 60 seconds).

#### Step: Happy path without year filter: Search for deep learning papers with max results of 4.
**Parameters:** {"topic_keywords": "deep learning", "max_results": 4}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Tool 'search_by_topic_tool' execution timed out (exceeded 60 seconds).

#### Step: Edge case: Test server behavior when topic_keywords are empty.
**Parameters:** {"topic_keywords": "", "max_results": 5}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Error in search_by_topic_tool: topic_keywords cannot be empty or blank.

#### Step: Edge case: Test server behavior when max_results exceeds upper limit.
**Parameters:** {"topic_keywords": "quantum computing", "max_results": 101}  
**Status:** ❌ Failure  
**Result:** Error executing tool: Error in search_by_topic_tool: max_results must be between 1 and 100 inclusive.

### Dependent Operation

#### Step: Dependent call: Use the DOI from the first result of the AI ethics topic search to fetch detailed paper info from Crossref.
**Parameters:** {"paper_id": null, "source": "Crossref"}  
**Status:** ❌ Failure  
**Result:** A required parameter resolved to None, likely due to a failure in a dependency.

## 4. Analysis and Findings

**Functionality Coverage:**  
The test plan covered all three available tools and tested both happy paths and edge cases including:
- Basic keyword search functionality
- Detailed paper lookup by ID
- Topic-based search with and without year filters
- Error handling for invalid inputs
- Dependent operations requiring output from prior steps

**Identified Issues:**  
All tests failed with either timeout errors or dependency resolution problems:

1. **Timeouts on External API Calls**: All primary function calls to external services (Semantic Scholar and Crossref) timed out after 60 seconds. This suggests potential performance issues or connectivity problems with these external services.

2. **Dependency Resolution Failures**: Several dependent tests failed because they relied on outputs from previous steps that had not executed successfully. This is primarily due to the timeout failures in the prerequisite steps.

3. **Error Handling**: While the error messages were generally clear and descriptive, the implementation did not handle some edge cases gracefully (e.g., missing DOIs). For example, the fetch_paper_details_tool crashed with an unhandled NoneType error when given a nonexistent DOI.

**Stateful Operations:**  
The server attempted to support stateful operations through output referencing (e.g., `$outputs.search_papers_happy_path[0].doi`), but this mechanism failed whenever the dependency step did not complete successfully.

**Error Handling:**  
The server's error handling was mostly appropriate, with clear validation errors for empty keywords and out-of-range max_results values. However, there were opportunities for improvement:
- Better handling of non-existent DOIs with more informative error messages
- Timeouts suggest the need for asynchronous processing or better connection management
- More robust handling of external service failures

## 5. Conclusion and Recommendations

The server implementation shows good design intent with proper input validation and comprehensive tool coverage, but it fails in actual execution due to timeout errors when accessing external services. The fundamental issue appears to be with the integration with Semantic Scholar and Crossref APIs rather than the server logic itself.

**Recommendations:**
1. Investigate and resolve timeout issues with external API calls - consider implementing asynchronous processing or increasing timeout limits
2. Improve error handling for non-existent DOIs and other edge cases
3. Implement retry mechanisms for failed external API calls
4. Add circuit breaker patterns to handle unreliable external services
5. Consider caching frequently accessed paper information to improve performance
6. Implement rate limiting and API key management for external services
7. Add better logging and monitoring to help diagnose integration issues

### BUG_REPORT_JSON
{
  "overall_status": "FAILED",
  "identified_bugs": [
    {
      "bug_id": 1,
      "description": "External API calls to Semantic Scholar and Crossref consistently time out after 60 seconds.",
      "problematic_tool": "search_papers_tool",
      "failed_test_step": "Happy path: Search for papers related to 'machine learning' with max results of 5.",
      "expected_behavior": "Should return search results within reasonable time",
      "actual_behavior": "Tool 'search_papers_tool' execution timed out (exceeded 60 seconds)."
    },
    {
      "bug_id": 2,
      "description": "External API calls to Semantic Scholar and Crossref consistently time out after 60 seconds affecting topic-based searches.",
      "problematic_tool": "search_by_topic_tool",
      "failed_test_step": "Happy path with optional filtering: Search for AI ethics papers between 2015 and 2020, limited to 3 results.",
      "expected_behavior": "Should return topic-based search results within reasonable time",
      "actual_behavior": "Tool 'search_by_topic_tool' execution timed out (exceeded 60 seconds)."
    },
    {
      "bug_id": 3,
      "description": "Improper handling of non-existent DOIs in paper detail lookup",
      "problematic_tool": "fetch_paper_details_tool",
      "failed_test_step": "Edge case: Fetch details using a DOI that likely does not exist.",
      "expected_behavior": "Should return a clear error message when a DOI doesn't exist",
      "actual_behavior": "Error executing tool: Error in fetch_paper_details_tool: Error while fetching paper details: 'NoneType' object has no attribute 'get'"
    }
  ]
}
### END_BUG_REPORT_JSON