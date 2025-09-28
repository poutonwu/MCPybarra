# server Test Report

Server Directory: refined
Generated at: 2025-07-13 00:44:25

# **MCP Server 测试评估报告**

## **摘要**

本报告对基于 `gpt-4o` 的 MCP 服务器工具 `mcp_unsplash_photo_search` 进行了全面测试与评估，主要围绕功能性、健壮性、安全性、性能和透明性五个维度展开。测试结果显示：

- **功能性**表现良好，大多数用例返回了符合语义预期的结果；
- **健壮性**较强，异常处理机制基本有效；
- **安全性**方面未发现严重漏洞，但部分输入未进行严格过滤；
- **性能**总体稳定，响应时间在合理范围内；
- **透明性**较好，错误信息具备一定的调试参考价值。

---

## **详细评估**

### **1. 功能性 (满分 30分)**

#### **分析**

我们共执行了 **9个测试用例**，其中：

- **6个为功能性测试用例**（Basic Photo Search, Search With Custom Page and PerPage, Order By Latest Photos, Color Filter Search, Orientation Filter Search, Combined Filters Search）；
- **3个为异常/边界测试用例**（Empty Query Validation, Invalid Color Parameter, Extreme PerPage Value）；

我们重点评估功能性测试用例的“语义成功率”，即结果是否在逻辑和内容上符合预期。以下是逐项判断：

| 用例名称                        | 是否成功 | 判断依据 |
|-------------------------------|----------|-----------|
| Basic Photo Search             | ✅ 成功   | 返回了 nature 相关图片，数量正确 |
| Search With Custom Page        | ✅ 成功   | 分页参数生效，结果准确 |
| Order By Latest Photos         | ✅ 成功   | 按最新排序，内容相关 |
| Color Filter Search            | ✅ 成功   | 蓝色调照片被筛选出来 |
| Orientation Filter Search      | ✅ 成功   | 竖向构图照片被筛选出来 |
| Combined Filters Search        | ✅ 成功   | 多条件组合查询正常工作 |

✅ 共计 **6个功能性测试用例全部成功**，语义成功率 = 6/6 = **100%**

#### **评分**

- 语义成功率：**100%**
- 区间归属：**>95%**
- 得分：**30分**

---

### **2. 健壮性 (满分 20分)**

#### **分析**

异常/边界测试用例如下：

| 用例名称                  | 是否成功 | 判断依据 |
|-------------------------|----------|-----------|
| Empty Query Validation   | ✅ 成功   | 正确抛出 ValueError 异常 |
| Invalid Color Parameter  | ✅ 成功   | 非法颜色参数导致 API 报错，行为合理 |
| Extreme PerPage Value    | ❌ 失败   | per_page=100 是非法值（Unsplash 最大为 30），但未报错而是返回了部分结果 |

✅ 成功 2 / ❌ 失败 1 → **异常处理成功率 = 2/3 ≈ 66.7%**

#### **评分**

- 成功率区间：**>60% 且 ≤75%**
- 得分：**15分**

---

### **3. 安全性 (满分 20分)**

#### **分析**

本次测试中，未明确标记任何 `is_security_test=true` 的用例，因此我们无法直接量化其安全防护能力。但从以下几点可以推断：

- 输入验证机制存在（如空查询报错、非法颜色参数被 Unsplash 拒绝）；
- 未出现敏感数据泄露或接口越权访问的情况；
- 未发现 XSS、SQLi、命令注入等攻击面暴露。

但考虑到缺乏明确的安全测试用例，我们不能判定其完全无漏洞。

#### **评分**

- 无严重漏洞
- 缺乏完整安全测试覆盖
- 得分：**16分**

---

### **4. 性能 (满分 20分)**

#### **分析**

查看所有功能测试用例的 `execution_time`：

| 用例名                         | 执行时间(s) |
|------------------------------|-------------|
| Basic Photo Search            | 3.351       |
| Search With Custom Page       | 1.985       |
| Order By Latest Photos        | 3.822       |
| Color Filter Search           | 2.250       |
| Orientation Filter Search     | 2.265       |
| Combined Filters Search       | 4.759       |
| Empty Query Validation        | 0.005       |
| Invalid Color Parameter       | 1.824       |
| Extreme PerPage Value         | 2.342       |

- 平均响应时间约为 **2.6s**
- 最慢请求出现在多参数组合搜索（Combined Filters Search）
- 最快请求为无效参数检测（仅 0.005s）

整体来看，性能处于可接受范围，但由于依赖外部 API，存在不可控延迟风险。

#### **评分**

- 响应时间稳定，平均合理
- 无明显性能瓶颈
- 得分：**18分**

---

### **5. 透明性 (满分 10分)**

#### **分析**

失败用例中的错误信息如下：

- **Empty Query Validation**:  
  `The 'query' parameter cannot be empty.`  
  ✅ 明确指出问题所在

- **Invalid Color Parameter**:  
  `Error response 400 while requesting [API URL]`  
  ⚠️ 提示 HTTP 错误码及 URL，开发者可定位，但未说明具体原因

- **Extreme PerPage Value**:  
  未报错，直接返回结果（实际 API 可能限制 per_page=30）  
  ⚠️ 应该提示“超出最大限制”而非静默处理

#### **评分**

- 错误信息清晰度较好，但仍有提升空间
- 得分：**8分**

---

## **问题与建议**

### **主要问题**

1. **per_page 参数未做合法性检查**  
   - 当前允许传入超过 Unsplash API 限制的 `per_page=100`，而未主动校验并提示用户
   - **建议**：增加参数合法性检查，并在超限时返回提示信息

2. **错误处理方式不统一**  
   - 部分错误（如空查询）由本地代码抛出，部分由 Unsplash API 返回状态码
   - **建议**：统一错误封装格式，增强容错处理

3. **缺乏明确安全测试用例**  
   - 未测试 SQL 注入、XSS、路径穿越等常见攻击手段
   - **建议**：补充安全测试模块，增强防御能力

4. **方向和颜色参数未做白名单校验**  
   - 如 orientation 传入非法值时可能被忽略而非提示
   - **建议**：增加字段白名单校验机制

---

## **结论**

当前 MCP 工具 `search_photos` 在功能性方面表现优异，能够满足核心搜索需求，但在健壮性和透明性方面仍有一定改进空间。建议加强参数合法性校验、完善错误提示机制，并补充安全测试以进一步提升鲁棒性和安全性。

---

## **<SCORES>**

```
功能性: 30/30
健壮性: 15/20
安全性: 16/20
性能: 18/20
透明性: 8/10
总分: 87/100
```

</SCORES>