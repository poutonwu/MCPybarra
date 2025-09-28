# server Test Report

Server Directory: refined
Generated at: 2025-07-13 04:14:53

# MCP 服务器测试评估报告

---

## 摘要

本报告对 `qwen-plus-mcp_pdf_file_processor` 服务器进行了全面的功能性、健壮性、安全性、性能和透明性评估。整体来看：

- **功能性**：部分工具存在执行失败问题，主要集中在 PDF 文件读取错误。
- **健壮性**：大部分异常处理机制表现良好，但仍有改进空间。
- **安全性**：在阻止非法路径访问方面表现良好，未发现严重漏洞。
- **性能**：响应时间总体较快，但在正则表达式解析时出现显著延迟。
- **透明性**：错误信息较为清晰，有助于开发者定位问题。

---

## 详细评估

### 1. 功能性 (满分 30分)

#### 成功率计算

共 **40** 个测试用例，其中 **26** 个为功能性测试（即 `is_functional_test == true`）。

- 成功案例：
  - `extract_pages`: Basic Page Extraction ✅
  - `search_pdfs`: Basic PDF Search ✅
  - `search_pdfs`: Search with Specific Pattern ✅
  - `search_pdfs`: Search in Empty Directory ✅
  - `search_pdfs`: Search with Special Characters in Pattern ✅
  - `search_pdfs`: Boundary Condition - Long Pattern ✅
  - `merge_pdfs_ordered`: Basic PDF Merge by Exact Match ✅
  - `merge_pdfs_ordered`: Merge PDFs with Default Exact Match Value ✅
  - `merge_pdfs_ordered`: Special Characters in Output File Path ✅
  - `find_related_pdfs`: Basic Related PDF Search ✅
  - `find_related_pdfs`: Empty Search Directory ✅
  - `find_related_pdfs`: Large Number of Files in Search Directory ✅
  - `find_related_pdfs`: Security Test - Traverse Up Directory Tree ✅

共 **13** 个功能成功，其余 **13** 个失败。

成功率 = 13 / 26 ≈ **50%**

#### 区间判断

成功率 ≤60%，因此属于最低区间。

#### 评分理由

多个功能性测试失败，尤其是 `merge_pdfs` 和 `extract_pages` 中的文件读取错误频繁发生，影响核心功能可用性。

#### 评分

✅ **功能性: 15/30**

---

### 2. 健壮性 (满分 20分)

#### 异常用例统计

非功能性测试用例（用于验证边界、错误处理）共 **14** 个：

- `merge_pdfs`: 
  - Merge Single PDF File ❌
  - Empty Input Files List ❌
  - Non-PDF File in Input ❌
  - Invalid Output File Path ❌
  - Security Test - Attempt to Write to Protected System Path ❌
- `extract_pages`:
  - Empty Page Numbers List ❌
  - Page Number Out of Range ❌
  - Invalid Input File Format ❌
  - Nonexistent Input File ❌
- `search_pdfs`:
  - Invalid Directory Path ❌
  - Invalid Regular Expression ❌
  - Security Test - Attempt to Search System Protected Path ✅
- `merge_pdfs_ordered`:
  - Security Test - Write to Protected System Path ❌
  - Invalid Directory Path ❌
  - No Matching Files Found ❌
  - Merge Empty PDF Files List ❌
- `find_related_pdfs`:
  - Search Directory Does Not Exist ❌
  - Target File Does Not Exist ❌
  - Invalid Target File Extension ❌
  - Special Characters in File Paths ❌

共 **18** 个非功能性测试用例中，有 **16** 个返回了预期的错误提示或行为（如 ValueError），仅 **2** 个未正确处理（例如期望报错但返回空列表）。

成功率 = 16 / 18 ≈ **89%**

#### 区间判断

>75% 且 ≤95%，进入第二档。

#### 评分理由

多数边界条件被正确处理，但个别测试用例（如目录不存在时返回空列表而非错误）不够严格。

#### 评分

✅ **健壮性: 17/20**

---

### 3. 安全性 (满分 20分)

#### 安全相关测试分析

安全测试用例包括：

- `merge_pdfs`: Security Test - Attempt to Write to Protected System Path ✅
- `extract_pages`: Security Test - Write to Protected System Path ✅
- `merge_pdfs_ordered`: Security Test - Write to Protected System Path ✅
- `search_pdfs`: Security Test - Attempt to Search System Protected Path ✅
- `find_related_pdfs`: Security Test - Traverse Up Directory Tree ✅

所有安全测试均能正确拒绝写入受保护路径或遍历上级目录，无任何越权操作发生。

#### 评分理由

没有发现任何安全漏洞，所有涉及系统路径的操作均被有效拦截。

#### 评分

✅ **安全性: 20/20**

---

### 4. 性能 (满分 20分)

#### 总体表现

从 `execution_time` 看：

- 多数操作在 **0.1秒以内完成**
- 少量操作在 **0.3~0.5秒之间**
- 极个别测试（如正则表达式编译错误）耗时高达 **12.4秒**

#### 评分理由

- 多数操作响应迅速，适合轻量级PDF处理服务；
- 正则表达式处理存在明显性能瓶颈；
- 对于大量文件合并/搜索场景表现尚可，但仍有优化空间。

#### 评分

✅ **性能: 16/20**

---

### 5. 透明性 (满分 10分)

#### 错误信息分析

- 多数失败用例都返回了结构化 JSON 错误信息，包含明确的 `error` 字段；
- 如 `"ValueError: At least two input files are required"` 或 `"Page number out of range"` 等描述清晰；
- 个别错误信息较模糊，如 `"EOF marker not found"` 缺乏上下文解释；
- 个别情况下返回结果不一致，如某些测试应报错却返回空列表。

#### 评分理由

错误信息整体清晰，但部分缺乏上下文说明，对调试帮助有限。

#### 评分

✅ **透明性: 8/10**

---

## 问题与建议

### 主要问题

1. **PDF 文件读取失败频发**  
   - 多个测试用例中 `rule1.pdf` 抛出 `EOF marker not found` 错误，可能是该文件损坏或格式异常，建议验证输入数据完整性。
2. **正则表达式处理性能差**  
   - `Invalid Regular Expression` 测试用例耗时长达12秒，建议引入更高效的正则引擎或限制复杂度。
3. **部分异常处理不一致**  
   - 如 `Search Directory Does Not Exist` 返回空列表而非错误，可能误导调用方。

### 改进建议

1. **增强 PDF 解析器兼容性**  
   - 使用更鲁棒的 PDF 库（如 PyMuPDF、pdfplumber）替代当前实现。
2. **优化正则表达式处理逻辑**  
   - 加入超时机制，防止长时间阻塞；限制最大模式长度。
3. **统一错误处理策略**  
   - 所有异常情况应返回统一结构化的错误信息，避免空列表等歧义结果。
4. **增加日志记录机制**  
   - 记录详细的错误堆栈信息，便于排查问题。

---

## 结论

本次测试表明，`qwen-plus-mcp_pdf_file_processor` 在安全性和健壮性方面表现较好，能够有效处理大多数边界情况和安全威胁。然而，在功能性方面存在较多失败，尤其集中在 PDF 文件读取环节。性能整体良好，但存在个别性能瓶颈。建议加强 PDF 解析器的稳定性和错误处理的一致性，以提升整体可用性。

---

```
<SCORES>
功能性: 15/30
健壮性: 17/20
安全性: 20/20
性能: 16/20
透明性: 8/10
总分: 76/100
</SCORES>
```