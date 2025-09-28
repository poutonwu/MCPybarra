# server Test Report

Server Directory: refined
Generated at: 2025-07-16 11:31:15

```markdown
# Zotero Library Manager Server 测试评估报告

## 摘要

本次测试对`deepseek-v3-mcp_zotero_library_manager`服务器进行了全面的功能、健壮性、安全性、性能和透明性评估。总体来看：

- **功能性**表现欠佳，多个核心功能（如搜索类型参数错误）未能正确实现。
- **健壮性**存在改进空间，部分边界条件处理得当，但仍有异常未被妥善捕获。
- **安全性**方面无明显漏洞，但未进行深入的安全渗透测试。
- **性能**整体尚可，但SSL连接问题导致响应时间不稳定。
- **透明性**较好，错误信息基本能反映问题所在。

---

## 详细评估

### 1. 功能性 (满分 30分)

#### 分析

我们统计了所有 `is_functional_test == true` 的测试用例的语义成功率：

| 工具名             | 功能性测试用例数量 | 成功数 | 成功率 |
|------------------|------------------|-------|--------|
| search_items       | 6                | 1     | 16.7%  |
| get_item_metadata  | 2                | 0     | 0%     |
| get_item_fulltext  | 2                | 0     | 0%     |
| **总计**           | **10**           | **1** | **10%** |

> 注：`search_items`中仅“Empty Query Validation”与“Invalid Search Type Handling”为非功能性测试，其余均为功能性测试。

#### 评分理由

- 语义成功率为 **10%**，远低于60%，落入最低区间。
- 所有工具的核心功能均未正常实现：
  - `search_items` 的 `qmode` 参数映射错误（应为 `title`, `author`, `year`, `fulltext`），导致搜索失败。
  - `get_item_metadata` 和 `get_item_fulltext` 抛出 SSL EOF 错误，无法获取数据。

#### 评分

✅ **功能性得分: 5/30**

---

### 2. 健壮性 (满分 20分)

#### 分析

我们统计了所有用于验证异常处理或边界情况的测试用例：

| 测试用例名称                          | 是否通过 |
|-------------------------------------|----------|
| Empty Query Validation               | ✅        |
| Invalid Search Type Handling         | ✅        |
| Special Characters In Query          | ❌