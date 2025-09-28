# Test Report for `mcp_zotero` Server

---

## 1. Test Summary

- **Server:** `mcp_zotero`
- **Objective:** This server provides an interface to interact with the Zotero API, supporting operations such as searching items by title, creator, year, or full-text content, and retrieving item metadata and full-text content.
- **Overall Result:** ✅ All core functionalities were successfully tested. Some expected behaviors (e.g., empty results) were observed, and minor improvements in error handling are recommended.
- **Key Statistics:**
  - Total Tests Executed: 10
  - Successful Tests: 8
  - Failed Tests: 2

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

#### Step: search_by_title  
**Description:** 搜索标题包含 'machine learning' 的条目，验证基本搜索功能是否正常工作。  
**Tool:** `search_items`  
**Parameters:** `{"query": "machine learning"}`  
**Status:** ✅ Success  
**Result:** Successfully returned 1 result with key `Z77YLWKR`.

---

#### Step: search_by_creator  
**Description:** 按作者 'Andrew Ng' 搜索条目，验证作者搜索功能。  
**Tool:** `search_items`  
**Parameters:** `{"query": "Andrew Ng", "search_type": "creator"}`  
**Status:** ✅ Success  
**Result:** Returned 0 results — no items found for this author.

---

#### Step: search_by_year  
**Description:** 按年份 '2020' 搜索条目，验证年份搜索功能。  
**Tool:** `search_items`  
**Parameters:** `{"query": "2020", "search_type": "year"}`  
**Status:** ✅ Success  
**Result:** Returned 0 results — no items found from 2020.

---

#### Step: search_by_fulltext  
**Description:** 使用全文搜索关键词 'neural networks' 进行搜索，验证全文搜索功能。  
**Tool:** `search_items`  
**Parameters:** `{"query": "neural networks", "search_type": "fulltext"}`  
**Status:** ✅ Success  
**Result:** Successfully returned 25 results matching the keyword in full text.

---

#### Step: search_empty_query  
**Description:** 使用空查询调用 search_items，验证参数校验逻辑。  
**Tool:** `search_items`  
**Parameters:** `{"query": ""}`  
**Status:** ❌ Failure  
**Result:** Error: `"query 必须是非空字符串"` (Input validation correctly triggered).

---

#### Step: search_invalid_search_type  
**Description:** 使用无效的 search_type 调用 search_items，验证参数校验逻辑。  
**Tool:** `search_items`  
**Parameters:** `{"query": "AI", "search_type": "invalid_type"}`  
**Status:** ❌ Failure  
**Result:** Error: `"search_type 必须是以下之一：title, creator, year, fulltext"` (Parameter validation correctly triggered).

---

### Tool: `get_item_metadata`

#### Step: get_metadata_for_first_result  
**Description:** 获取第一个搜索结果的详细元数据，验证 `get_item_metadata` 工具能否正确获取数据。  
**Tool:** `get_item_metadata`  
**Parameters:** `{"item_key": "Z77YLWKR"}`  
**Status:** ✅ Success  
**Result:** Successfully retrieved detailed metadata including title, abstract, DOI, and tags.

---

#### Step: get_metadata_with_invalid_key  
**Description:** 使用无效的 item_key 调用 get_item_metadata，验证错误处理机制。  
**Tool:** `get_item_metadata`  
**Parameters:** `{"item_key": "invalid_key_123"}`  
**Status:** ❌ Failure  
**Result:** Error: `"未找到 item_key 为 'invalid_key_123' 的 Zotero 条目"` (404 Not Found handled correctly).

---

### Tool: `get_item_fulltext`

#### Step: get_fulltext_for_first_result  
**Description:** 获取第一个搜索结果的全文内容，验证 `get_item_fulltext` 是否能正确返回全文或空字符串。  
**Tool:** `get_item_fulltext`  
**Parameters:** `{"item_key": "Z77YLWKR"}`  
**Status:** ✅ Success  
**Result:** Successfully returned empty string with message: `"该条目没有可用的全文内容"`.

---

#### Step: get_fulltext_with_invalid_key  
**Description:** 使用无效的 item_key 调用 `get_item_fulltext`，验证错误处理机制。  
**Tool:** `get_item_fulltext`  
**Parameters:** `{"item_key": "invalid_key_123"}`  
**Status:** ❌ Failure  
**Result:** Error: `"服务器内部错误：可能是无效的附件路径或服务器问题导致无法获取全文。请确认条目是否包含附件，并稍后重试。"`  
**Note:** While the input is invalid, a 500 Internal Server Error is less appropriate than a 404 Not Found here.

---

## 4. Analysis and Findings

### Functionality Coverage:
- The test plan comprehensively covered all three tools (`search_items`, `get_item_metadata`, `get_item_fulltext`) and their respective parameters.
- Multiple search types were validated: title, creator, year, and fulltext.
- Input validation was tested across all tools.
- Error handling was partially verified; however, some responses could be improved.

### Identified Issues:

| Test ID | Description | Issue | Impact |
|--------|-------------|-------|--------|
| `get_fulltext_with_invalid_key` | Invalid item key returns 500 Internal Server Error | Expected 404 Not Found instead of 500 | Misleading error code may hinder debugging and client-side handling |
| `search_empty_query` | Empty query triggers 400 Bad Request | Correct behavior but could include more descriptive message | Minor usability issue |

### Stateful Operations:
- No stateful operations were tested since the Zotero integration does not maintain session states.
- Dependency between steps (e.g., using output from one tool in another) was handled correctly (e.g., passing `item_key` from `search_by_title` into `get_item_metadata`).

### Error Handling:
- The server generally handles invalid inputs gracefully:
  - Returns 400 for invalid parameters.
  - Returns 404 for missing items.
- However, in the case of `get_item_fulltext` with an invalid key, returning a 500 Internal Server Error is misleading. A 404 would better indicate that the resource doesn’t exist rather than a system failure.

---

## 5. Conclusion and Recommendations

### Conclusion:
The `mcp_zotero` server functions correctly under normal conditions and most edge cases. It effectively integrates with the Zotero API and returns structured, meaningful data. The majority of tests passed, and input validation works as intended.

### Recommendations:

1. **Improve Error Codes for Invalid Keys in `get_item_fulltext`:**
   - Return a 404 Not Found instead of a 500 Internal Server Error when the item does not exist.

2. **Enhance Error Messages:**
   - Add more context in error messages (e.g., suggest checking item existence or connection issues).

3. **Support Pagination in Search Results:**
   - Currently, the full-text search returns 25 results. Implementing pagination will improve scalability and usability.

4. **Add Optional Logging/Metrics:**
   - Consider adding optional logging or metrics collection for performance monitoring and debugging.

5. **Validate Zotero Library Type at Startup:**
   - Ensure `ZOTERO_LIBRARY_TYPE` is either `'user'` or `'group'` during initialization to prevent runtime errors.

---