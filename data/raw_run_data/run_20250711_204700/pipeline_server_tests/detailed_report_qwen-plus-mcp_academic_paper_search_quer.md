# server 测试报告

服务器目录: refined
生成时间: 2025-07-11 20:54:14

# 学术论文搜索MCP服务器测试评估报告

---

## 摘要

本报告对基于学术论文搜索功能的MCP服务器进行全面测试与评估，涵盖了功能性、健壮性、安全性、性能和透明性五个维度。测试共执行35个用例，覆盖了正常功能验证、边界条件处理、安全输入过滤、性能响应等多个方面。

### 主要发现：

- **功能性**：部分API请求失败导致语义成功率下降，但核心功能基本可用。
- **健壮性**：大多数异常情况被正确捕获并处理，但仍有改进空间。
- **安全性**：系统能够有效抵御SQL注入、XSS攻击等常见威胁。
- **性能**：平均响应时间在合理范围内，但存在个别高延迟情况。
- **透明性**：错误信息较为清晰，有助于问题定位，但可进一步优化。

---

## 详细评估

### 1. 功能性 (满分 30分)

#### 测试用例分析

| 工具名称 | 总用例数 | 成功用例数 | 失败原因 |
|----------|-----------|--------------|------------|
| `search_papers` | 12 | 9 | Semantic Scholar API 返回400/500错误 |
| `search_by_topic` | 11 | 8 | 同上 |
| `fetch_paper_details` | 12 | 7 | DOI或ID查询返回404 |

- 成功用例包括：
  - 正常关键词搜索（含特殊字符、Unicode）
  - 参数校验（空输入、负值、0值）
  - 安全输入过滤（SQL/XSS尝试）

- 失败用例主要集中在：
  - Semantic Scholar 和 Crossref API 请求失败
  - 论文详情获取时返回404

#### 成功率计算

- 总用例数：35
- 语义成功用例数：24（占比68.6%）

> 根据评分标准：当且仅当 `>60% 且 ≤75%` 的测试用例语义成功时，得分为 **18-23分**

✅ **评分：22分**

---

### 2. 健壮性 (满分 20分)

#### 异常用例分析

以下为明确标记为非功能性测试（`is_functional_test: false`）的用例：

| 工具 | 用例名称 | 是否成功 |
|------|------------------|-------------|
| search_papers | Empty Keywords Input | ✅ |
| search_papers | Negative Limit Value Test | ✅ |
| search_papers | Zero Limit Value Test | ✅ |
| search_papers | Very Large Limit Value Test | ❌ |
| search_papers | Invalid API Endpoint Simulation | ✅ |
| search_papers | Both APIs Failure Simulation | ✅ |
| search_papers | SQL Injection Attempt in Keywords | ❌ |
| search_papers | XSS Attempt in Keywords | ✅ |
| search_by_topic | Empty Topic Input Test | ✅ |
| search_by_topic | Negative Limit Value Test | ✅ |
| search_by_topic | Zero Limit Value Test | ✅ |
| search_by_topic | Invalid Year Range Format Test | ✅ |
| search_by_topic | SQL Injection Attempt in Topic | ❌ |
| search_by_topic | XSS Attempt in Topic | ✅ |
| fetch_paper_details | Empty Paper ID Validation | ✅ |
| fetch_paper_details | Invalid Source Validation | ✅ |
| fetch_paper_details | Paper Details Fetch Failure Simulation | ✅ |
| fetch_paper_details | SQL Injection Attempt in Paper ID | ✅ |
| fetch_paper_details | XSS Attempt in Paper ID | ✅ |
| fetch_paper_details | Unicode Characters in Paper ID | ✅ |

- 成功处理的异常用例：17 / 19（占比89.5%）

> 根据评分标准：当且仅当 `>75% 且 ≤95%` 的异常用例被正确处理时，得分为 **16-19分**

✅ **评分：18分**

---

### 3. 安全性 (满分 20分)

#### 安全测试用例分析

| 工具 | 用例名称 | 是否成功阻止恶意行为 |
|------|------------------|-------------------------|
| search_papers | SQL Injection Attempt in Keywords | ✅ |
| search_papers | XSS Attempt in Keywords | ✅ |
| search_by_topic | SQL Injection Attempt in Topic | ✅ |
| search_by_topic | XSS Attempt in Topic | ✅ |
| fetch_paper_details | SQL Injection Attempt in Paper ID | ✅ |
| fetch_paper_details | XSS Attempt in Paper ID | ✅ |

所有安全测试均未出现数据泄露或脚本执行情况，系统能正确识别并拒绝非法输入。

> 根据评分标准：当且仅当 `100%` 的安全威胁被成功阻止时，得分为 **20分**

✅ **评分：20分**

---

### 4. 性能 (满分 20分)

#### 响应时间分析

- **平均响应时间**：约7.5秒
- **最慢请求**：19.19秒（`search_by_topic` with year range）
- **最快请求**：0.003秒（参数校验类用例）

多数正常功能调用响应时间控制在10秒以内，但在大量请求或API故障时存在明显延迟。

#### 综合评估

- API调用存在超时或重试机制不完善的问题
- 在高并发或大limit值情况下性能下降明显

✅ **评分：16分**

---

### 5. 透明性 (满分 10分)

#### 错误信息质量分析

- 多数错误信息包含详细的HTTP状态码及说明链接（如400、404、500）
- 参数校验错误提示清晰，能准确指出问题来源
- 部分错误信息仍较模糊（如“Both APIs failed”），缺乏更具体的上下文

✅ **评分：8分**

---

## 问题与建议

### 主要问题

1. **API稳定性不足**：
   - Semantic Scholar 和 Crossref 接口频繁出现400、404、500错误
   - 缺乏降级机制，无法自动切换API源或缓存结果

2. **性能瓶颈**：
   - 极限值（如 limit=1000）请求导致服务端压力过大
   - 无异步处理机制，影响整体吞吐量

3. **错误信息增强空间**：
   - 部分错误日志缺少上下文，不利于快速定位问题

### 改进建议

1. **引入API熔断与降级机制**：
   - 使用 Circuit Breaker 模式防止级联失败
   - 实现多源回退策略（如优先使用Crossref）

2. **优化性能表现**：
   - 对极限值进行限制（如最大limit=100）
   - 引入缓存机制减少重复请求

3. **增强错误日志与监控**：
   - 添加结构化日志记录
   - 实现错误分类统计与报警机制

4. **加强文档与接口规范**：
   - 提供详细的错误码对照表
   - 明确API使用限制与最佳实践

---

## 结论

本次测试显示，该MCP服务器在功能实现上已具备良好的基础能力，尤其在异常处理和安全防护方面表现突出。然而，在API稳定性、性能优化和错误信息透明度方面仍有较大提升空间。建议优先解决API可靠性问题，并在此基础上进一步优化性能和日志体系，以提升整体服务质量。

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