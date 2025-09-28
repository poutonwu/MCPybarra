# server 测试报告

服务器目录: academic-search-mcp-server-master
生成时间: 2025-06-30 21:51:42

```markdown
# 学术搜索MCP服务器测试评估报告

## 摘要

本报告对 `academic-search-mcp-server-master` 服务器的功能性、健壮性、安全性、性能和透明性进行了全面评估。整体来看，服务器在功能性方面表现良好，能够正确处理大多数正常查询场景；在健壮性和安全性方面存在一定改进空间，尤其在参数验证和异常处理上存在部分问题；性能表现中等偏上，响应时间基本可控；错误提示信息较为清晰，但仍有提升空间。

---

## 详细评估

### 1. 功能性（满分：30分）

#### 测试用例总数：31  
#### 成功语义执行的用例数：

- **search_by_topic**：
  - 成功用例：Basic Search with Topic, Search with Topic and Year Range, Search with Topic and Limit, Search with Invalid Year Start, Search with End Year Before Start Year, Search with SQL Injection Attempt in Topic, Search Using File Name as Topic → **7/9**
    - 失败用例：
      - Empty Topic: 正确返回错误提示 ✅
      - Negative Limit: 返回无结果，应使用默认值 ❌
- **search_papers**：
  - 成功用例：Basic Search with Query, Search with Query and Limit, Search with Maximum Limit, Search with Minimum Limit, Search with SQL Injection Attempt in Query, Search with Non-English Query, Search with All Valid Parameters → **7/9**
    - 失败用例：
      - Empty Query: 正确返回错误提示 ✅
      - Negative Limit: 返回无结果，应使用默认值 ❌
- **fetch_paper_details**：
  - 成功用例：Basic Paper Details Fetch, Missing Source Defaults to Semantic Scholar, Invalid Paper ID Handling, Empty Paper ID Input, Special Characters in Paper ID, Crossref DOI with Invalid Format, Fetch Paper Using File Name as Paper ID → **7/8**
    - 失败用例：
      - Fetch Paper from Semantic Scholar: 应明确拒绝无效ID或提供更详细的错误信息 ❌

✅ 总体语义成功率为：**(7 + 7 + 7) / 31 = 21 / 31 ≈ 67.7%**

#### 区间判断：
> 当且仅当 >60% 且 ≤75% 的测试用例语义成功时：**18-23分**

✅ 实际得分：**22分**

---

### 2. 健壮性（满分：20分）

#### 关键异常处理测试用例（共10个）：

| 用例名称 | 是否成功处理 |
|---------|--------------|
| Search with Empty Topic | ✅ |
| Search with Negative Limit (search_by_topic) | ❌ |
| Search with Negative Limit (search_papers) | ❌ |
| Search with Empty Query | ✅ |
| Search with End Year Before Start Year | ✅ |
| Search with Invalid Year Start | ✅ |
| Empty Paper ID Input | ✅ |
| Special Characters in Paper ID | ✅ |
| Crossref DOI with Invalid Format | ✅ |
| Empty Paper ID Input (Semantic Scholar) | ✅ |

✅ 异常处理成功率为：**8/10 = 80%**

#### 区间判断：
> 当且仅当 >75% 且 ≤95% 的异常用例被正确处理时：**16-19分**

✅ 实际得分：**18分**

---

### 3. 安全性（满分：20分）

#### 安全相关测试用例（共4个）：

| 用例名称 | 是否成功阻止攻击 |
|---------|------------------|
| Search with SQL Injection Attempt in Topic | ✅ |
| Search with SQL Injection Attempt in Query | ✅ |
| Search with Very Long Query String | ✅ |
| SQL Injection Attempt in Paper ID | ✅ |

所有安全测试用例均未导致系统异常行为或数据泄露。

✅ 所有安全威胁都被有效拦截，无明显漏洞。

#### 区间判断：
> 当且仅当 100% 的安全威胁被成功阻止时：**20分**

✅ 实际得分：**20分**

---

### 4. 性能（满分：20分）

#### 平均响应时间分析：

- **search_by_topic**平均耗时：约 **4.5s**
- **search_papers**平均耗时：约 **5.0s**
- **fetch_paper_details**平均耗时：约 **1.8s**

#### 综合评估：

- 查询类工具（search_*）响应时间较长，部分超过5秒，可能影响用户体验。
- 论文详情获取工具响应较快，性能较优。
- 对于学术搜索服务而言，响应时间可接受，但仍有优化空间。

✅ 实际得分：**16分**

---

### 5. 透明性（满分：10分）

#### 错误提示质量评估：

- 多数失败情况返回了清晰的错误提示，如“Please provide a search query.”
- 少数边界情况提示模糊，例如负数limit直接返回“No results found”，未说明原因。
- 参数类型错误或缺失时提示不统一。

✅ 实际得分：**8分**

---

## 问题与建议

### 主要问题：

1. **参数验证不足**：
   - 负数limit未自动修正为默认值，而是返回空结果。
   - 特殊字符处理不够智能，可能导致用户困惑。

2. **错误提示不一致**：
   - 部分错误返回“no result”，未说明是参数错误还是无匹配内容。

3. **性能瓶颈**：
   - search_papers 和 search_by_topic 工具响应时间偏长，尤其在高并发场景下可能成为瓶颈。

### 改进建议：

1. **增强参数校验逻辑**：
   - 对limit等数值参数进行非负检查，并自动调整为默认值。
   - 对特殊字符进行预处理或转义。

2. **统一错误提示机制**：
   - 明确区分参数错误、无结果、系统错误等情况，并返回标准化错误码。

3. **优化搜索接口性能**：
   - 引入缓存机制，减少重复请求。
   - 使用异步加载或分页机制，降低单次请求负载。

---

## 结论

该学术搜索MCP服务器在功能性方面表现良好，能够完成大部分核心搜索任务；具备良好的安全防护能力；在健壮性和性能方面有一定改进空间；错误提示较为清晰但需进一步标准化。总体而言，服务器功能完备，具备上线条件，但仍需持续优化以提升稳定性和用户体验。

---

```
<SCORES>
功能性: 22/30
健壮性: 18/20
安全性: 20/20
性能: 16/20
透明性: 8/10
总分: 84/100
</SCORES>
```