# 感悟总结生成功能实现文档

## 概述

本文档描述了教研室工作考评系统中感悟总结自动生成功能的实现。该功能基于综合考核指标自动生成感悟总结，分析各教研室得分高低和指标达标情况。

## 需求映射

- **需求 15.1**: 基于综合考核指标自动生成感悟总结
- **需求 15.2**: 分析各教研室得分高低
- **需求 15.3**: 分析各教研室指标达标情况
- **需求 15.4**: 包含突出指标说明
- **需求 15.5**: 包含待提升指标说明
- **需求 15.6**: 禁止人工填写感悟总结

## 实现组件

### 1. 数据模型

**InsightSummary** (`backend/app/models/insight_summary.py`)
- 存储生成的感悟总结
- 与自评表一对一关联
- 包含生成时间戳

### 2. 核心服务

**InsightGenerationService** (`backend/app/services/insight_service.py`)

主要功能：
- `generate_insight_summary()`: 生成感悟总结文本
- `save_insight_summary()`: 保存感悟总结到数据库
- `generate_and_save()`: 生成并保存的便捷方法

#### 生成算法

1. **数据收集**
   - 获取AI评分结果
   - 获取所有手动评分记录
   - 获取最终得分

2. **指标分析**
   - 计算每个考核指标的平均得分
   - 综合AI评分和手动评分

3. **识别强弱项**
   - 突出指标：得分 >= 75分（良好阈值）
   - 待提升指标：得分 < 60分（及格阈值）

4. **总结生成**
   - 总体评价（优秀/良好/合格/待改进）
   - 突出指标说明
   - 待提升指标说明
   - 改进建议
   - 总结展望

#### 得分等级阈值

```python
EXCELLENT_THRESHOLD = 85.0  # 优秀
GOOD_THRESHOLD = 75.0       # 良好
AVERAGE_THRESHOLD = 60.0    # 及格
```

### 3. API端点

**感悟总结API** (`backend/app/api/v1/endpoints/insight.py`)

#### POST /api/insight/generate
生成感悟总结

请求体：
```json
{
  "evaluation_id": "uuid"
}
```

响应：
```json
{
  "insight_summary": {
    "id": "uuid",
    "evaluation_id": "uuid",
    "summary": "感悟总结文本...",
    "generated_at": "2024-01-01T00:00:00"
  },
  "message": "Insight summary generated successfully"
}
```

#### GET /api/insight/{evaluation_id}
查询感悟总结

响应：
```json
{
  "id": "uuid",
  "evaluation_id": "uuid",
  "summary": "感悟总结文本...",
  "generated_at": "2024-01-01T00:00:00"
}
```

### 4. 自动生成集成

感悟总结在结果分发时自动生成（`backend/app/api/v1/endpoints/publication.py`）：

```python
# POST /api/publication/distribute
# 在分发结果时自动为所有评估生成感悟总结
for evaluation in evaluations:
    try:
        generate_insight_for_evaluation(db, evaluation.id)
    except Exception as e:
        # 记录错误但不影响分发流程
        print(f"Warning: Failed to generate insight for evaluation {evaluation.id}")
```

## 感悟总结示例

### 优秀等级示例（85分以上）

```
本教研室在本年度工作考评中获得优秀等级（90.00分），在本次考评中表现突出，各项工作成效显著。
在教学改革项目、荣誉表彰和教学质量等方面表现突出，分别获得95.00分、92.00分和88.00分，
体现了教研室在这些领域的扎实工作和显著成效。但在课程建设方面有待提升，得分为70.00分，
建议在今后工作中加强该方面的建设和投入。具体建议：推进课程改革和建设，提升课程质量和特色。
希望教研室继续保持优势，不断创新发展，为学院教学工作做出更大贡献。
```

### 合格等级示例（60-75分）

```
本教研室在本年度工作考评中获得合格等级（65.00分），在本次考评中达到基本要求，但仍有较大提升空间。
在教学改革项目方面表现突出，得分为80.00分，体现了教研室在该领域的扎实工作和显著成效。
但在荣誉表彰和课程建设等方面有待提升，分别获得55.00分和50.00分，建议在今后工作中加强这些方面的建设和投入。
具体建议：鼓励教师参加各类教学竞赛，争取更多荣誉；推进课程改革和建设，提升课程质量和特色。
希望教研室认真总结经验教训，针对薄弱环节制定改进措施，不断提升教学质量和管理水平。
```

## 测试覆盖

### 单元测试 (`backend/tests/test_insight_generation.py`)

1. **test_generate_insight_summary_service**: 测试服务生成功能
2. **test_save_insight_summary**: 测试保存功能
3. **test_insight_summary_update**: 测试更新已存在的总结
4. **test_generate_insight_api**: 测试API生成接口
5. **test_get_insight_summary_api**: 测试API查询接口
6. **test_generate_insight_without_final_score**: 测试无最终得分时的错误处理
7. **test_get_nonexistent_insight**: 测试查询不存在的总结
8. **test_insight_identifies_strong_indicators**: 测试识别突出指标
9. **test_insight_identifies_weak_indicators**: 测试识别待提升指标
10. **test_distribute_generates_insight_summary**: 测试分发时自动生成

所有测试通过率：100%

## 使用流程

### 自动生成（推荐）

1. 教研室完成自评并提交
2. AI评分完成
3. 管理端完成手动评分和最终得分确定
4. 校长办公会审定通过
5. 考评办公室发起公示
6. **系统在分发结果时自动生成感悟总结**
7. 教研室端和管理端可查看感悟总结

### 手动生成（可选）

如需重新生成或单独生成感悟总结：

```bash
POST /api/insight/generate
{
  "evaluation_id": "评估ID"
}
```

## 注意事项

1. **前置条件**：必须存在最终得分才能生成感悟总结
2. **自动生成**：在结果分发时自动触发，无需人工干预
3. **可重复生成**：如果已存在感悟总结，重新生成会更新现有记录
4. **错误处理**：生成失败不会影响分发流程，会记录警告日志
5. **禁止人工编辑**：感悟总结完全由系统自动生成，不支持人工编辑

## 扩展性

### 自定义指标权重

可在 `InsightGenerationService` 中修改 `INDICATOR_WEIGHTS` 配置：

```python
INDICATOR_WEIGHTS = {
    "teaching_process_management": 0.20,
    "course_construction": 0.15,
    "teaching_reform_projects": 0.25,
    "honorary_awards": 0.20,
    "teaching_quality": 0.20,
}
```

### 自定义得分阈值

可修改等级阈值：

```python
EXCELLENT_THRESHOLD = 85.0  # 优秀
GOOD_THRESHOLD = 75.0       # 良好
AVERAGE_THRESHOLD = 60.0    # 及格
```

### 自定义改进建议

可在 `_generate_suggestions()` 方法中添加更多指标的改进建议。

## 相关文件

- 服务实现：`backend/app/services/insight_service.py`
- API端点：`backend/app/api/v1/endpoints/insight.py`
- 数据模型：`backend/app/models/insight_summary.py`
- Schema定义：`backend/app/schemas/insight.py`
- 单元测试：`backend/tests/test_insight_generation.py`
- 分发集成：`backend/app/api/v1/endpoints/publication.py`
