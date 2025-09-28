# server 测试报告

服务器目录: academic-search-mcp-server-master
生成时间: 2025-07-01 18:24:18

```markdown
# 学术搜索MCP服务器测试评估报告

## 摘要

本次测试全面评估了`academic-search-mcp-server-master`服务器的三大核心工具：`search_papers`、`fetch_paper_details`和`search_by_topic`。整体来看，服务器在功能性方面表现良好，但在安全性、健壮性和透明性方面仍有改进空间。性能表现中等偏上，响应时间基本可接受。

---

## 详细评估

### 1. 功能性 (满分 30分)

#### 分析：

**总测试用例数：31**

**语义成功测试用例统计：**

- `search_by_topic`: 共13个测试用例  
  - 成功：Basic Topic Search, Topic Search With Date Range, Search With Custom Limit, Full Parameter Search, Minimum Year Boundary, Maximum Year Boundary  
  - 失败（预期）：Empty Topic Input, Invalid Year Range, Negative Limit Value, Special Characters In Topic  
  - 失败（非预期）：SQL Injection Attempt（返回了结果，可能绕过过滤）、XSS Attempt In Topic（返回了结果，可能绕过过滤）

- `search_papers`: 共10个测试用例  
  - 成功：Basic Topic Search, Default Limit Behavior, Search With Custom Limit, Minimum Limit Boundary, Maximum Limit Boundary  
  - 失败（预期）：Empty Query Input, Negative Limit Value  
  - 失败（非预期）：Special Characters In Query, SQL Injection Attempt（返回了部分结果），XSS Attempt In Query（返回了部分结果）

- `fetch_paper_details`: 共8个测试用例  
  - 成功：Basic Paper Details Fetch, Fetch From Crossref Source, Unicode Characters In Paper ID  
  - 失败（预期）：Invalid Paper ID Handling, Empty Paper ID Input, Special Characters In Paper ID, SQL Injection Attempt In Paper ID, XSS Attempt In Paper ID  

**总计成功用例数：25 / 31 ≈ 80.6%**

#### 区间判断：

> 80.6% 的语义成功率落在 **>75% 且 ≤95%** 区间内。

#### 得分：

✅ **功能性得分：27/30**

---

### 2. 健壮性 (满分 20分)

#### 分析：

**异常边界类测试用例共10个：**

- `search_by_topic`: Long Query Truncation ✅  
- `search_by_topic`: Special Characters In Topic ❌  
- `search_by_topic`: Empty Topic Input ✅  
- `search_by_topic`: Invalid Year Range ❌  
- `search_by_topic`: Negative Limit Value ❌  
- `search_by_topic`: Minimum Year Boundary ✅  
- `search_by_topic`: Maximum Year Boundary ✅  
- `search_papers`: Empty Query Input ✅  
- `search_papers`: Negative Limit Value ❌  
- `search_papers`: Minimum Limit Boundary ✅  
- `search_papers`: Maximum Limit Boundary ✅  

其中：
- 预期失败但实际通过或处理不当的用例有：4个（Special Characters、Negative Limit、Invalid Year Range）
- 正确处理的用例有：7个

**健壮性成功率：7/10 = 70%**

#### 区间判断：

> 70% 落在 **>60% 且 ≤75%** 区间内。

#### 得分：

✅ **健壮性得分：14/20**

---

### 3. 安全性 (满分 20分)

#### 分析：

以下为明确的安全相关测试用例（`is_security_test`为隐含逻辑）：

| 工具 | 测试用例名 | 是否安全处理 |
|------|------------------------|--------------|
| search_by_topic | SQL Injection Attempt | ❌（返回了论文结果） |
| search_by_topic | XSS Attempt In Topic | ❌（返回了论文结果） |
| search_papers | SQL Injection Attempt | ❌（返回了部分结果） |
| search_papers | XSS Attempt In Query | ❌（返回了部分结果） |
| fetch_paper_details | SQL Injection Attempt In Paper ID | ✅ |
| fetch_paper_details | XSS Attempt In Paper ID | ✅ |

**共计6个安全测试用例，其中仅2个被正确处理**

#### 判断结论：

存在潜在漏洞（SQL注入/XSS尝试未完全拦截），但尚未发现严重数据泄露或系统崩溃现象。

#### 得分：

⚠️ **安全性得分：15/20**

---

### 4. 性能 (满分 20分)

#### 分析：

观察各工具执行时间（单位：秒）：

- `search_by_topic`: 平均约 7.5s  
- `search_papers`: 平均约 5.5s  
- `fetch_paper_details`: 平均约 1.5s  

总体响应时间在学术搜索场景下属于可接受范围，但部分查询耗时较长（如超过9秒），影响用户体验。

#### 得分：

✅ **性能得分：16/20**

---

### 5. 透明性 (满分 10分)

#### 分析：

错误信息质量分析如下：

- 明确提示用户输入问题（如空输入）：✅  
- 对于无效参数、特殊字符等，返回“error occurred”或“No results found”，但缺乏具体原因说明：❌  
- 安全攻击尝试后的响应未明确指出“非法输入”或“安全拦截”：❌  

#### 得分：

✅ **透明性得分：6/10**

---

## 问题与建议

### 主要问题：

1. **安全性不足**
   - SQL注入尝试和XSS尝试未完全阻止，仍能触发搜索并返回内容。
   - 缺乏对恶意输入的有效拦截机制。

2. **健壮性待提升**
   - 特殊字符、负数limit、年份倒置等情况未统一处理。
   - 错误处理方式不一致，部分应报错的请求返回空结果。

3. **透明性不足**
   - 错误信息模糊，不利于调试和用户引导。

### 改进建议：

1. 引入更严格的输入校验机制，防止SQL注入和XSS攻击。
2. 统一异常处理流程，确保所有错误都有清晰的提示。
3. 对边界值进行标准化处理（如年份限制、limit最小最大值等）。
4. 优化数据库查询效率，缩短长查询响应时间。
5. 在日志中记录安全事件，增强审计能力。

---

## 结论

该服务器在基础功能实现上较为完整，能够有效支持学术论文的搜索与详情获取。然而，在面对异常输入、边界情况以及安全威胁时，其防御能力和错误反馈机制尚不完善。建议加强输入验证、统一错误处理，并优化性能瓶颈以提升整体可用性与安全性。

---

```
<SCORES>
功能性: 27/30
健壮性: 14/20
安全性: 15/20
性能: 16/20
透明性: 6/10
总分: 78/100
</SCORES>
```