# server Test Report

Server Directory: refined
Generated at: 2025-07-13 04:09:31

# Qwen-Plus MCP Academic Paper Search Server 测试评估报告

---

## 摘要

本次测试对Qwen-Plus MCP学术论文搜索服务器进行了全面评估，涵盖功能性、健壮性、安全性、性能和透明性五个维度。服务器共包含3个工具（`search_papers`, `fetch_paper_details`, `search_by_topic`），共计24个测试用例。

整体来看，服务器在功能实现上表现良好，异常处理机制较为完善，安全输入处理基本合规，响应速度适中，错误信息具备一定诊断价值。主要问题集中在部分API调用失败的容错机制不强，以及个别查询参数校验不够严格。

---

## 详细评估

### 1. 功能性 (满分 30分)

#### 统计分析

- **总测试用例数**：24
- **功能性测试用例数（is_functional_test为true）**：16
- **语义成功用例数**：
  - 成功返回有效数据并符合预期逻辑：15
  - 一个失败案例为`fetch_paper_details`使用Semantic Scholar ID时返回429 Too Many Requests，属于API限制而非功能缺陷

> **成功率 = 15 / 16 = 93.75%**

#### 区间判断

根据评分标准：
- 93.75% ∈ (75%, 95%]
- 对应分数区间：**24-29分**

#### 最终评分

考虑到该失败案例为外部API限流所致，并非服务端自身逻辑错误，因此给予较高评分：

✅ **功能性: 28/30**

---

### 2. 健壮性 (满分 20分)

#### 异常用例分析

| 用例名称 | 是否正确处理 |
|---------|--------------|
| Empty Keywords Input | ✅ |
| Negative Limit Value Handling | ✅ |
| API Failure Fallback Mechanism | ❌（未触发预期的RuntimeError）|
| Invalid Source Handling | ✅ |
| Missing Paper ID Validation | ✅ |
| Non-existent Paper ID Test | ✅（返回404视为正常处理）|
| Large Limit Value Boundary Test | ✅ |

- **总异常用例数**：7
- **正确处理用例数**：6

> **成功率 = 6 / 7 ≈ 85.7%**

#### 区间判断

- 85.7% ∈ (75%, 95%]
- 对应分数区间：**16-19分**

#### 最终评分

考虑到唯一失败的“API Failure Fallback”用例未能验证是否抛出`RuntimeError`，但结果仍返回了部分数据，影响较小：

✅ **健壮性: 18/20**

---

### 3. 安全性 (满分 20分)

#### 安全相关用例分析

| 用例名称 | 是否正确处理 |
|---------|--------------|
| XSS Attempt in Keywords (`<script>alert('xss')</script>`) | ✅ |
| SQL Injection Attempt in Paper ID (`'; DROP TABLE papers;--`) | ✅ |
| Special Characters in Paper ID | ✅ |
| XSS Attempt in Paper ID | ✅ |

- **总安全用例数**：4
- **全部通过，无漏洞暴露**

> **成功率 = 4 / 4 = 100%**

#### 最终评分

所有潜在攻击尝试均被正确拦截或转义，未发现任何安全漏洞：

✅ **安全性: 20/20**

---

### 4. 性能 (满分 20分)

#### 执行时间分析

- **平均执行时间**：
  - `search_papers`: ~3.8s
  - `search_by_topic`: ~5.8s
  - `fetch_paper_details`: ~2.2s

- **最长执行时间**：
  - `XSS Attempt in Keywords`（search_by_topic）：7.66s

#### 评估结论

- 在学术论文搜索场景下，平均响应时间在合理范围内；
- 部分请求因MCP适配器截断输出导致延迟略高，但不影响实际可用性；
- 未出现显著性能瓶颈。

✅ **性能: 17/20**

---

### 5. 透明性 (满分 10分)

#### 错误信息分析

- 多数错误返回格式统一，如：
  ```
  ToolException: Error executing tool fetch_paper_details: paper_id parameter cannot be empty string
  ```

- 提供了明确的错误类型（ValueError, RuntimeError等）和上下文信息；
- 个别错误提示可进一步优化，例如：
  - “limit must be a positive integer” 可加入最小值建议；
  - API调用失败时应说明是否是临时问题或永久性错误。

✅ **透明性: 8/10**

---

## 问题与建议

### 主要问题

1. **API失败回退机制未完全验证**：
   - `API Failure Fallback Mechanism`测试用例未明确验证是否抛出`RuntimeError`；
   - 当前响应仅返回部分数据，无法确认是否已尝试两个API均失败。

2. **参数校验边界模糊**：
   - `year_range`字段未进行格式校验（如非法格式"2025-2020"）；
   - `topic`字段长度未设上限。

3. **部分响应内容截断**：
   - 虽属MCP适配器限制，但应在文档中明确告知用户最大返回字符数。

### 改进建议

1. **增强异常反馈机制**：
   - 明确记录每个API调用状态，便于回溯失败原因；
   - 对多API失败情况增加日志追踪。

2. **细化参数校验规则**：
   - 增加`year_range`正则表达式校验；
   - 对`topic`、`keywords`添加最大长度限制。

3. **提升用户体验**：
   - 若结果被截断，建议在响应中添加`has_more`字段提示用户是否需分页获取；
   - 提供更详细的错误码和排查建议。

---

## 结论

Qwen-Plus MCP学术论文搜索服务器在功能性和安全性方面表现出色，健壮性和性能也处于良好水平，错误信息具备一定指导意义。尽管存在少量改进空间，但整体质量稳定，适用于生产环境部署。

---

```
<SCORES>
功能性: 28/30
健壮性: 18/20
安全性: 20/20
性能: 17/20
透明性: 8/10
总分: 91/100
</SCORES>
```