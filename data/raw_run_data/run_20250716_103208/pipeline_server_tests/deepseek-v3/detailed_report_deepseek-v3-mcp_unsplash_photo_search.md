# server Test Report

Server Directory: refined
Generated at: 2025-07-16 10:43:45

```markdown
# MCP服务器测试评估报告

## 摘要

本次测试对`deepseek-v3-mcp_unsplash_photo_search`服务器进行了全面评估，涵盖功能性、健壮性、安全性、性能和透明性五个维度。总体来看：

- **功能性**：大部分功能实现良好，但部分API请求失败，影响了成功率。
- **健壮性**：在边界条件处理方面表现尚可，但仍存在参数验证不严谨的情况。
- **安全性**：面对XSS攻击输入时未完全阻止，存在一定风险。
- **性能**：响应时间整体较好，但在SSL握手阶段存在延迟问题。
- **透明性**：错误信息较为清晰，有助于开发者排查问题。

---

## 详细评估

### 1. 功能性 (满分 30分)

#### 分析

共12个测试用例，其中9个为功能性测试（`is_functional_test == true`）：

| 测试用例名称 | 成功？ |
|--------------|--------|
| Basic Photo Search With Default Parameters | ❌（SSL超时） |
| Search Photos With Custom Page And PerPage | ✅ |
| Search Sorted By Latest | ❌（SSL超时） |
| Search Filtered By Color | ✅ |
| Search Filtered By Portrait Orientation | ✅ |
| Search With Special Characters In Query | ❌（SSL超时） |
| Invalid Query Parameter | ✅（正确报错） |
| Negative Page Number Handling | ✅（正确报错） |
| Large PerPage Value Test | ❌（SSL超时） |

成功用例数：6  
总功能性用例数：9  
**语义成功率 = 6 / 9 ≈ 66.7%**

根据评分标准：
- `>60% 且 ≤75%` 的测试用例语义成功 → **18-23分**
- 实际得分：**21分**

#### 结论
基础搜索、颜色过滤、方向筛选等功能基本可用，但默认查询与排序等核心功能因SSL连接问题失败，影响整体体验。

---

### 2. 健壮性 (满分 20分)

#### 分析

关注以下异常/边界测试用例：

| 测试用例名称 | 成功？ |
|--------------|--------|
| Invalid Query Parameter | ✅ |
| Negative Page Number Handling | ✅ |
| Invalid Color Filter | ❌（抛出无效错误） |
| XSS Attempt In Query | ✅（返回非恶意结果） |
| Search With NonExistent Query | ✅（返回空相关图片） |

成功处理的异常用例数：4  
总异常用例数：5  
**成功率 = 4 / 5 = 80%**

根据评分标准：
- `>75% 且 ≤95%` 的异常用例被正确处理 → **16-19分**
- 实际得分：**18分**

#### 结论
系统能有效处理多数边界情况，但对非法颜色值的处理存在缺陷。

---

### 3. 安全性 (满分 20分)

#### 分析

仅有一个安全测试用例：

- **XSS Attempt In Query**: 输入包含 `<script>` 标签的查询字符串，期望拒绝或转义。
- 实际响应：返回了包含该标签内容的图片描述（如`text`、`a laptop computer...`），说明系统未完全阻止潜在XSS输入。

虽然未直接执行脚本，但允许将恶意内容作为文本索引进入图像库，仍构成潜在漏洞。

#### 结论
存在潜在安全漏洞，建议增强输入过滤机制。

- **实际得分：16分**

---

### 4. 性能 (满分 20分)

#### 分析

查看所有`execution_time`字段：

| 用例 | 时间（秒） |
|------|------------|
| Basic Photo Search | 5.51 |
| Custom Page & PerPage | 1.46 |
| Search Sorted By Latest | 5.39 |
| Search Filtered By Color | 1.57 |
| Portrait Orientation Filter | 1.19 |
| Special Characters In Query | 5.41 |
| Large PerPage Value | 5.37 |
| NonExistent Query | 1.41 |
| Invalid Query | 0.003 |
| Negative Page | 0.003 |

- 多次出现约5秒的SSL超时现象，表明网络层存在问题。
- 正常执行平均时间约为1.4秒，属于合理范围。

#### 结论
性能中等偏上，但SSL连接不稳定影响整体表现。

- **实际得分：16分**

---

### 5. 透明性 (满分 10分)

#### 分析

错误信息示例：

- `"The 'query' parameter is required and must be a non-empty string."` ✅ 清晰
- `"httpx.HTTPStatusError"` ✅ 明确指出网络错误
- `"ValueError: ..."`, `"ToolException: ..."` ✅ 包含上下文信息
- 个别错误缺少完整堆栈或原始请求信息 ❌

#### 结论
错误提示整体清晰，有助于调试，但部分细节缺失。

- **实际得分：8分**

---

## 问题与建议

### 主要问题

1. **SSL连接不稳定**
   - 多个测试用例因SSL握手超时失败。
   - 影响用户正常使用，需排查代理、证书或网络配置。

2. **非法颜色参数处理不当**
   - 对无效颜色值未进行忽略或明确提示。
   - 存在抛出Python内部错误的风险。

3. **XSS输入未完全过滤**
   - 虽未执行脚本，但允许构造带脚本标签的搜索词。
   - 可能导致存储型XSS攻击路径存在。

4. **最大每页数量限制未明确**
   - `per_page=30` 抛出SSL错误而非参数上限提示。

### 改进建议

- 引入更稳定的HTTPS客户端配置，优化连接超时机制。
- 加强参数验证逻辑，尤其针对颜色、排序等可选参数。
- 对用户输入进行HTML实体编码或黑名单过滤，防止XSS注入。
- 统一错误格式，增加原始请求信息输出以辅助定位问题。

---

## 结论

`deepseek-v3-mcp_unsplash_photo_search` 服务器实现了基本的Unsplash照片搜索功能，具备良好的参数验证与部分错误反馈能力。然而，SSL连接稳定性不足以及对XSS输入的容忍度较高，是当前主要短板。建议优先修复SSL握手问题并加强输入校验机制。

---

```
<SCORES>
功能性: 21/30
健壮性: 18/20
安全性: 16/20
性能: 16/20
透明性: 8/10
总分: 79/100
</SCORES>
```