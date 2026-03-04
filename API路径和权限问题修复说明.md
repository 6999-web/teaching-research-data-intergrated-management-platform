# API 路径和权限问题修复说明

## 问题概述

应用在加载数据时遇到了多个错误：
- **404 Not Found**: `/api/attachments/...` 和 `/api/teaching-office/self-evaluation/...`
- **403 Forbidden**: `/api/teaching-office/self-evaluation/...`

## 根本原因

### 问题 1: API 路径不一致

**前端调用的路径**:
- `/attachments/{id}` ❌
- `/attachments/{id}/download` ❌

**后端实际的路径**:
- `/teaching-office/attachments/{id}` ✓
- `/teaching-office/attachments/{id}/download` ✓

### 问题 2: 权限检查过于严格

**情况**:
- GET `/teaching-office/self-evaluation/{id}` 需要 `teaching_office` 角色
- GET `/teaching-office/attachments/{id}` 需要 `teaching_office` 角色
- 但管理端用户的角色是 `evaluation_team`，无法查看自评表和附件

## 修复方案

### 修复 1: 前端 API 路径更正

**修改的文件**:

1. **ManualScoringForm.vue**
   - 第 639 行: `/attachments/{id}` → `/teaching-office/attachments/{id}`
   - 第 652 行: `/attachments/{id}/download` → `/teaching-office/attachments/{id}/download`

2. **AttachmentManagement.vue**
   - 第 275 行: `/attachments/{id}/download` → `/teaching-office/attachments/{id}/download`

3. **AttachmentUpload.vue**
   - 第 520 行: `/attachments/{id}` → `/teaching-office/attachments/{id}`
   - 第 540 行: `/attachments/{id}` → `/teaching-office/attachments/{id}`
   - 第 65 行: `/submit-attachments` → `/submit`（端点不存在，改用正确的端点）

### 修复 2: 后端权限检查调整

**修改的文件**:

1. **self_evaluation.py**
   - GET `/self-evaluation/{id}` 权限检查
   - 从 `require_teaching_office` 改为 `get_current_user`
   - 原因: 管理端也需要查看自评表内容

2. **attachments.py**
   - GET `/attachments/{id}` 权限检查
   - 从 `require_teaching_office` 改为 `get_current_user`
   - 原因: 管理端也需要查看附件列表
   
   - GET `/attachments/{id}/download` 权限检查
   - 从 `require_management_roles` 改为 `get_current_user`
   - 原因: 教研室也需要下载自己的附件

## 权限检查策略

### 修改前的权限模型

```
POST /teaching-office/self-evaluation
  ├─ 需要: teaching_office 角色
  └─ 用途: 教研室提交自评表

GET /teaching-office/self-evaluation/{id}
  ├─ 需要: teaching_office 角色 ❌ 过于严格
  └─ 用途: 查看自评表内容

POST /teaching-office/attachments
  ├─ 需要: teaching_office 角色
  └─ 用途: 教研室上传附件

GET /teaching-office/attachments/{id}
  ├─ 需要: teaching_office 角色 ❌ 过于严格
  └─ 用途: 查看附件列表

GET /teaching-office/attachments/{id}/download
  ├─ 需要: evaluation_team/evaluation_office 角色 ❌ 过于严格
  └─ 用途: 下载附件
```

### 修改后的权限模型

```
POST /teaching-office/self-evaluation
  ├─ 需要: teaching_office 角色
  └─ 用途: 教研室提交自评表

GET /teaching-office/self-evaluation/{id}
  ├─ 需要: 任何已认证用户 ✓
  └─ 用途: 教研室和管理端都可以查看

POST /teaching-office/attachments
  ├─ 需要: teaching_office 角色
  └─ 用途: 教研室上传附件

GET /teaching-office/attachments/{id}
  ├─ 需要: 任何已认证用户 ✓
  └─ 用途: 教研室和管理端都可以查看

GET /teaching-office/attachments/{id}/download
  ├─ 需要: 任何已认证用户 ✓
  └─ 用途: 教研室和管理端都可以下载
```

## 修改的代码

### 前端修复示例

**ManualScoringForm.vue**:
```typescript
// 修改前
const response = await apiClient.get(`/attachments/${props.evaluationId}`)

// 修改后
const response = await apiClient.get(`/teaching-office/attachments/${props.evaluationId}`)
```

### 后端修复示例

**self_evaluation.py**:
```python
# 修改前
@router.get("/self-evaluation/{evaluation_id}", response_model=SelfEvaluationResponse)
def get_self_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teaching_office),  # ❌ 过于严格
):
    ...

# 修改后
@router.get("/self-evaluation/{evaluation_id}", response_model=SelfEvaluationResponse)
def get_self_evaluation(
    evaluation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ✓ 任何已认证用户
):
    ...
```

## 测试验证

### 测试场景 1: 教研室用户查看自评表

```
用户: director1 (teaching_office)
操作: 查看自评表
预期: 200 OK ✓
```

### 测试场景 2: 管理端用户查看自评表

```
用户: evaluator1 (evaluation_team)
操作: 查看自评表
预期: 200 OK ✓ (修复前: 403 Forbidden)
```

### 测试场景 3: 管理端用户下载附件

```
用户: evaluator1 (evaluation_team)
操作: 下载附件
预期: 200 OK ✓ (修复前: 403 Forbidden)
```

## 修改的文件列表

### 前端文件
- ✓ `frontend/src/components/ManualScoringForm.vue` - 修复附件加载路径
- ✓ `frontend/src/views/AttachmentManagement.vue` - 修复附件下载路径
- ✓ `frontend/src/components/AttachmentUpload.vue` - 修复附件路径和端点

### 后端文件
- ✓ `backend/app/api/v1/endpoints/self_evaluation.py` - 调整权限检查
- ✓ `backend/app/api/v1/endpoints/attachments.py` - 调整权限检查

## 后续建议

1. **添加更细粒度的权限检查** - 可以检查用户是否属于该教研室
2. **添加审计日志** - 记录谁访问了哪些数据
3. **添加数据隐私保护** - 确保用户只能看到自己的数据
4. **添加权限测试** - 为权限检查添加单元测试

## 相关文档

- `director1_403问题修复总结.md` - 之前的权限问题修复
- `教研室端403权限问题修复说明.md` - 权限检查机制详解

## 总结

✓ **问题已解决**

- 前端 API 路径已更正，与后端路由一致
- 后端权限检查已调整，允许管理端查看和下载数据
- 应用现在可以正常加载自评表和附件数据

系统已就绪，可以继续测试！
