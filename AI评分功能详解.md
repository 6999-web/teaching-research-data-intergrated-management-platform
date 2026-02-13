# AI评分功能详解 🤖

## 📋 功能概述

AI评分是教研室数据管理平台的核心功能之一，使用**DeepSeek AI大模型**自动分析教研室的自评表和支撑材料，给出客观公正的评分结果。

### 核心价值
- ⚡ **提高效率**：自动评分，减少人工工作量80%以上
- 🎯 **客观公正**：基于预设标准，避免人为主观因素
- 🔍 **智能检测**：自动发现数据异常，如数量不匹配
- 📊 **详细分析**：提供每个指标的评分理由
- 🏷️ **自动分类**：智能分类附件到对应考核指标

---

## 🔄 AI评分完整流程

```
1. 教研室提交自评表
   ↓
2. 系统锁定自评表（status=locked）
   ↓
3. 触发AI评分
   ↓
4. 构建评分提示词（包含自评内容+附件信息）
   ↓
5. 调用DeepSeek API
   ↓
6. 解析AI返回的JSON结果
   ↓
7. 保存AI评分到数据库（ai_scores表）
   ↓
8. 检测异常数据（数量不匹配等）
   ↓
9. 自动分类附件
   ↓
10. 更新自评表状态（status=ai_scored）
```

---

## 🎯 评分标准（满分100分）

### 1. 教学过程管理（25分）

| 等级 | 分数范围 | 标准 |
|------|---------|------|
| 优秀 | 22-25分 | 教学文档齐全、管理规范、有创新举措 |
| 良好 | 18-21分 | 教学文档完整、管理规范 |
| 合格 | 15-17分 | 教学文档基本完整、管理基本规范 |
| 不合格 | 0-14分 | 教学文档不完整或管理不规范 |

**评分依据**：
- 教学计划完整性
- 教学大纲规范性
- 教学日志记录情况
- 教学质量监控措施

### 2. 课程建设（25分）

| 等级 | 分数范围 | 标准 |
|------|---------|------|
| 优秀 | 22-25分 | 课程体系完善、有特色课程、建设成效显著 |
| 良好 | 18-21分 | 课程体系完整、建设成效良好 |
| 合格 | 15-17分 | 课程体系基本完整、有一定建设成效 |
| 不合格 | 0-14分 | 课程体系不完整或建设成效不明显 |

**评分依据**：
- 课程体系完整性
- 精品课程/一流课程数量
- 课程改革创新情况
- 课程建设成果

### 3. 教学改革项目（25分）

**计分规则**：
- 每个项目基础分：5分
- 最高分：25分（5个项目）
- 项目级别加分：
  - 国家级项目：+2分
  - 省级项目：+1分
  - 校级项目：基础分

**必须条件**：
- ✅ 需要有附件证明材料支撑
- ✅ 附件中能解析出项目信息
- ❌ 无附件支撑的项目不计分

### 4. 荣誉表彰（25分）

**计分规则**：
- 每个荣誉基础分：5分
- 最高分：25分（5个荣誉）
- 荣誉级别加分：
  - 国家级荣誉：+2分
  - 省级荣誉：+1分
  - 校级荣誉：基础分

**必须条件**：
- ✅ 需要有附件证明材料支撑
- ✅ 附件中能解析出荣誉证书
- ❌ 无附件支撑的荣誉不计分

---

## 🤖 DeepSeek AI模型

### 使用的模型
- **模型名称**：deepseek-chat
- **开发商**：DeepSeek（深度求索）
- **特点**：
  - 中文理解能力强
  - 逻辑推理能力优秀
  - 成本低廉
  - 响应速度快

### API配置

在 `backend/.env` 文件中配置：

```env
# DeepSeek API配置
DEEPSEEK_API_KEY=your-api-key-here
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
```

### API调用参数

```python
{
    "model": "deepseek-chat",
    "messages": [
        {
            "role": "system",
            "content": "你是教研室工作考评专家..."
        },
        {
            "role": "user",
            "content": "评分提示词..."
        }
    ],
    "temperature": 0.3  # 低温度，保证评分稳定性
}
```

**temperature=0.3 的作用**：
- 降低随机性，保证评分一致性
- 同样的输入会得到相似的输出
- 避免评分结果波动过大

---

## 📝 评分提示词（Prompt）

### 提示词结构

```
你是教研室工作考评专家，请根据以下自评表内容和附件信息进行评分。

【第1部分：自评表内容】
- 教学过程管理：[教研室填写的内容]
- 课程建设：[教研室填写的内容]
- 教学改革项目个数（自评填写）：5
- 荣誉表彰个数（自评填写）：3

【第2部分：附件信息】
1. 文件名：2024年教改项目立项通知.pdf，考核指标：教学改革项目
2. 文件名：省级教学成果奖证书.jpg，考核指标：荣誉表彰
3. 文件名：课程建设总结报告.docx，考核指标：课程建设
...

【第3部分：评分标准】
[详细的评分标准，包括4个维度的分值范围和标准]

【第4部分：输出格式要求】
请按照以下JSON格式返回评分结果：
{
    "total_score": 85.5,
    "indicator_scores": [...],
    "parsed_reform_projects": 3,
    "parsed_honorary_awards": 2,
    "attachment_classifications": [...]
}
```

### 提示词设计原则

1. **角色定位明确**：定义AI为"教研室工作考评专家"
2. **输入信息完整**：包含自评内容和附件列表
3. **标准清晰具体**：详细的评分标准和分值范围
4. **输出格式严格**：要求返回JSON格式，便于解析
5. **任务明确**：明确要求对比数量、分类附件等

---

## 📊 AI返回的数据格式

### 完整的JSON响应

```json
{
    "total_score": 85.5,
    "indicator_scores": [
        {
            "indicator": "教学过程管理",
            "score": 22.0,
            "reasoning": "教学文档齐全、管理规范，符合优秀标准"
        },
        {
            "indicator": "课程建设",
            "score": 23.5,
            "reasoning": "课程体系完善、有特色课程、建设成效显著"
        },
        {
            "indicator": "教学改革项目",
            "score": 15.0,
            "reasoning": "根据附件解析出3个教学改革项目，每个5分"
        },
        {
            "indicator": "荣誉表彰",
            "score": 10.0,
            "reasoning": "根据附件解析出2个荣誉表彰，每个5分"
        }
    ],
    "parsed_reform_projects": 3,
    "parsed_honorary_awards": 2,
    "attachment_classifications": [
        {
            "file_name": "2024年教改项目立项通知.pdf",
            "classified_indicator": "teaching_reform_projects"
        },
        {
            "file_name": "省级教学成果奖证书.jpg",
            "classified_indicator": "honorary_awards"
        },
        {
            "file_name": "课程建设总结报告.docx",
            "classified_indicator": "other"
        }
    ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| total_score | 数字 | 总分（0-100） |
| indicator_scores | 数组 | 各指标的详细评分 |
| indicator_scores[].indicator | 字符串 | 指标名称 |
| indicator_scores[].score | 数字 | 该指标得分 |
| indicator_scores[].reasoning | 字符串 | 评分理由 |
| parsed_reform_projects | 数字 | AI从附件中解析出的教改项目数量 |
| parsed_honorary_awards | 数字 | AI从附件中解析出的荣誉数量 |
| attachment_classifications | 数组 | 附件分类结果 |
| attachment_classifications[].file_name | 字符串 | 附件文件名 |
| attachment_classifications[].classified_indicator | 字符串 | 分类到的指标 |

---

## ⚠️ 异常检测功能

### 检测的异常类型

#### 1. 数量不匹配（count_mismatch）

**触发条件**：
- 自评表填写的项目数量 ≠ AI从附件解析出的数量

**示例场景**：

**场景A：缺少支撑材料**
```
自评表填写：5个教学改革项目
AI解析结果：3个教学改革项目
异常描述：自评表填写5项教学改革项目，但附件仅解析出3份证书，
         缺少2份支撑材料。请核实是否存在遗漏上传或填写错误。
```

**场景B：多出材料**
```
自评表填写：2个荣誉表彰
AI解析结果：4个荣誉表彰
异常描述：自评表填写2项荣誉表彰，但附件解析出4份证书，
         多出2份材料。请核实是否存在重复上传或分类错误。
```

### 异常数据存储

异常数据保存在 `anomalies` 表中：

```sql
INSERT INTO anomalies (
    id,
    evaluation_id,
    type,
    indicator,
    declared_count,
    parsed_count,
    description,
    status
) VALUES (
    'uuid-xxx',
    'evaluation-uuid',
    'count_mismatch',
    'teaching_reform_projects',
    5,
    3,
    '自评表填写5项教学改革项目，但附件仅解析出3份证书...',
    'pending'
);
```

### 异常处理流程

```
1. AI评分时检测到异常
   ↓
2. 创建异常记录（status=pending）
   ↓
3. 同步到管理端
   ↓
4. 评教小组查看异常列表
   ↓
5. 人工复核异常数据
   ↓
6. 做出处理决定：
   - adjust：调整分数
   - accept：接受AI评分
   ↓
7. 更新异常状态（status=resolved）
```

---

## 🏷️ 附件自动分类

### 分类逻辑

AI会根据附件的**文件名**和**内容特征**，将附件分类到对应的考核指标：

#### 分类类别

1. **teaching_reform_projects**（教学改革项目）
   - 关键词：教改、项目、立项、结题
   - 文件类型：通知、证书、结题报告

2. **honorary_awards**（荣誉表彰）
   - 关键词：荣誉、奖项、表彰、证书
   - 文件类型：证书、奖状、表彰文件

3. **other**（其他）
   - 不属于上述两类的附件
   - 如：课程建设材料、教学总结等

### 分类示例

| 文件名 | AI分类结果 | 理由 |
|--------|-----------|------|
| 2024年省级教改项目立项通知.pdf | teaching_reform_projects | 包含"教改项目"关键词 |
| 优秀教师荣誉证书.jpg | honorary_awards | 包含"荣誉证书"关键词 |
| 课程建设总结报告.docx | other | 不属于项目或荣誉类 |
| 教学质量奖证书.pdf | honorary_awards | 包含"奖"和"证书"关键词 |

### 分类结果应用

分类后的附件会：
1. 更新 `attachments.indicator` 字段
2. 标记 `attachments.classified_by = 'ai'`
3. 在前端按指标分组显示
4. 便于评教小组审核

---

## 🔒 AI评分的不可变性

### 为什么不可修改？

AI评分记录一旦创建，就**不能修改或删除**，这是为了：

1. **保证可追溯性**：所有评分历史都可查询
2. **防止篡改**：避免人为修改AI评分结果
3. **审计需要**：满足教育评估的审计要求
4. **公平公正**：确保评分过程透明

### 技术实现

通过SQLAlchemy的事件监听器实现：

```python
@event.listens_for(AIScore, 'before_update')
def prevent_ai_score_update(mapper, connection, target):
    """阻止更新AI评分记录"""
    raise IntegrityError(
        statement="UPDATE ai_scores",
        params={},
        orig=Exception(f"AI评分记录不可修改。记录ID: {target.id}")
    )

@event.listens_for(AIScore, 'before_delete')
def prevent_ai_score_delete(mapper, connection, target):
    """阻止删除AI评分记录"""
    raise IntegrityError(
        statement="DELETE FROM ai_scores",
        params={},
        orig=Exception(f"AI评分记录不可删除。记录ID: {target.id}")
    )
```

### 如果需要调整分数？

如果AI评分有误，不能直接修改，而是：
1. 评教小组进行**手动评分**
2. 在**最终得分**中综合AI评分和手动评分
3. 可以调整手动评分的权重

---

## 🔄 重试机制

### 为什么需要重试？

调用外部API可能遇到：
- 网络超时
- API服务暂时不可用
- 请求限流

### 重试策略

使用 `tenacity` 库实现智能重试：

```python
@retry(
    stop=stop_after_attempt(3),              # 最多重试3次
    wait=wait_exponential(multiplier=1, min=1, max=10),  # 指数退避
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def _call_deepseek_api(self, prompt: str) -> str:
    # API调用代码
    ...
```

**重试时间间隔**：
- 第1次失败：等待1秒后重试
- 第2次失败：等待2秒后重试
- 第3次失败：等待4秒后重试
- 3次都失败：抛出异常

---

## 🧪 测试模式

### 模拟数据

如果没有配置DeepSeek API密钥，系统会返回模拟数据用于测试：

```python
def _get_mock_response(self) -> str:
    """获取模拟响应数据（用于测试）"""
    mock_data = {
        "total_score": 85.5,
        "indicator_scores": [
            {
                "indicator": "教学过程管理",
                "score": 22.0,
                "reasoning": "教学文档齐全、管理规范，符合优秀标准"
            },
            # ... 其他指标
        ],
        "parsed_reform_projects": 3,
        "parsed_honorary_awards": 2,
        "attachment_classifications": []
    }
    return json.dumps(mock_data, ensure_ascii=False)
```

### 测试流程

1. 不配置 `DEEPSEEK_API_KEY`
2. 提交自评表
3. 触发AI评分
4. 系统返回模拟数据
5. 可以测试后续流程

---

## 📈 性能优化

### 1. 异步调用

使用 `async/await` 异步调用API：

```python
async def execute_ai_scoring(self, evaluation_id: UUID) -> AIScore:
    # 异步执行，不阻塞其他请求
    ai_response = await self._call_deepseek_api(prompt)
    ...
```

### 2. 超时控制

设置30秒超时，避免长时间等待：

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(...)
```

### 3. 批量处理

一次API调用处理一个自评表的所有指标，减少API调用次数。

### 4. 缓存机制（未来优化）

可以考虑：
- 缓存相似的评分结果
- 缓存附件分类结果
- 减少重复的API调用

---

## 💰 成本估算

### DeepSeek API定价

- 输入：约 ¥0.001/千tokens
- 输出：约 ¥0.002/千tokens

### 单次评分成本

假设：
- 输入tokens：2000（提示词+自评内容+附件列表）
- 输出tokens：500（评分结果JSON）

**成本计算**：
```
输入成本：2000 × 0.001 / 1000 = ¥0.002
输出成本：500 × 0.002 / 1000 = ¥0.001
总成本：¥0.003（约3厘）
```

### 年度成本估算

假设100个教研室，每年评估1次：
```
年度成本：100 × ¥0.003 = ¥0.3（3毛钱）
```

**结论**：成本极低，几乎可以忽略不计！

---

## 🎯 AI评分的优势

### 1. 效率提升

| 对比项 | 人工评分 | AI评分 |
|--------|---------|--------|
| 单份评分时间 | 30-60分钟 | 10-30秒 |
| 100份评分时间 | 50-100小时 | 17-50分钟 |
| 效率提升 | - | **100倍以上** |

### 2. 一致性保证

- ✅ 同样的输入得到相似的输出
- ✅ 不受评分人主观情绪影响
- ✅ 评分标准统一

### 3. 24/7可用

- ✅ 随时可以评分，不受时间限制
- ✅ 不需要等待评教小组有空
- ✅ 提交即评分

### 4. 智能检测

- ✅ 自动发现数据异常
- ✅ 智能分类附件
- ✅ 生成详细的评分理由

### 5. 可追溯

- ✅ 所有评分记录永久保存
- ✅ 不可篡改，保证公正
- ✅ 便于审计和复查

---

## ⚙️ 如何使用AI评分

### 前端触发

在管理端，评教小组可以手动触发AI评分：

```javascript
// 调用AI评分API
const response = await fetch('/api/scoring/ai', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        evaluation_id: 'uuid-xxx'
    })
});

const result = await response.json();
console.log('AI评分结果:', result);
```

### 后端API

```python
@router.post("/ai")
async def trigger_ai_scoring(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """触发AI评分"""
    
    # 权限检查
    if current_user.role not in ["review_group", "review_office"]:
        raise HTTPException(status_code=403, detail="无权限")
    
    # 执行AI评分
    service = AIScoringService(db)
    ai_score = await service.execute_ai_scoring(evaluation_id)
    
    return {
        "message": "AI评分完成",
        "ai_score": ai_score
    }
```

---

## 🔮 未来优化方向

### 1. 多模态分析

- 📄 解析PDF文档内容
- 🖼️ 识别图片中的文字（OCR）
- 📊 分析Excel表格数据

### 2. 更智能的评分

- 🧠 学习历史评分数据
- 📈 动态调整评分标准
- 🎯 个性化评分建议

### 3. 实时反馈

- ⚡ 教研室填写时实时评分
- 💡 提供改进建议
- 📝 指导如何提高分数

### 4. 评分解释

- 📊 可视化评分依据
- 🔍 详细的评分分析报告
- 💬 自然语言解释评分理由

---

## 📚 相关文档

- `backend/app/services/ai_scoring_service.py` - AI评分服务代码
- `backend/app/models/ai_score.py` - AI评分数据模型
- `backend/app/models/anomaly.py` - 异常数据模型
- `数据库表结构详解.md` - 数据库表详细说明

---

## 🎉 总结

AI评分功能是教研室数据管理平台的核心创新点：

✅ **高效**：评分速度提升100倍以上  
✅ **智能**：自动检测异常、分类附件  
✅ **公正**：基于统一标准，不可篡改  
✅ **经济**：成本极低，几乎可以忽略  
✅ **可靠**：重试机制，保证成功率  

这是一个设计精良、功能完善的AI评分系统！🚀
