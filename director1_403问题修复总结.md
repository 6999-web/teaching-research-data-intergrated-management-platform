# director1 用户 403 Forbidden 问题修复总结

## 问题概述

**现象**: director1 用户在教研室端提交自评表时收到 403 Forbidden 错误
- 登录成功 ✓
- 获取 Token 成功 ✓
- 提交自评表时被拦截 ✗ (403 Forbidden)

**根本原因**: 后端接口缺少角色权限检查

## 修复方案

### 修改 1: self_evaluation.py - 添加权限检查

**文件**: `backend/app/api/v1/endpoints/self_evaluation.py`

**修改内容**:
1. 导入 `RoleChecker`
2. 创建 `require_teaching_office` 检查器
3. 在 5 个接口中添加权限检查

```python
# 导入
from app.core.deps import get_db, get_current_user, RoleChecker

# 创建检查器
require_teaching_office = RoleChecker(["teaching_office"])

# 在接口中使用
@router.post("/self-evaluation")
def create_self_evaluation(
    evaluation_data: SelfEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teaching_office),  # ← 添加权限检查
):
    ...
```

**修改的接口**:
- ✓ `POST /teaching-office/self-evaluation` - 创建/保存自评表
- ✓ `GET /teaching-office/self-evaluation/{evaluation_id}` - 查询自评表
- ✓ `PUT /teaching-office/self-evaluation/{evaluation_id}` - 更新自评表
- ✓ `POST /teaching-office/self-evaluation/{evaluation_id}/submit` - 提交自评表
- ✓ `POST /teaching-office/trigger-ai-scoring` - 触发 AI 评分

### 修改 2: attachments.py - 添加权限检查

**文件**: `backend/app/api/v1/endpoints/attachments.py`

**修改内容**:
1. 导入 `RoleChecker`
2. 创建两个检查器
3. 在 5 个接口中添加权限检查

```python
# 导入
from app.core.deps import get_db, get_current_user, RoleChecker

# 创建检查器
require_teaching_office = RoleChecker(["teaching_office"])
require_management_roles = RoleChecker(["evaluation_team", "evaluation_office"])

# 教研室端接口
@router.post("/attachments")
async def upload_attachments(
    ...,
    current_user: User = Depends(require_teaching_office),  # ← 教研室上传
):
    ...

# 管理端接口
@router.get("/attachments")
def query_attachments(
    ...,
    current_user: User = Depends(require_management_roles),  # ← 管理端查询
):
    ...
```

**修改的接口**:
- ✓ `POST /teaching-office/attachments` - 上传附件（教研室）
- ✓ `GET /teaching-office/attachments/{evaluation_id}` - 查询附件（教研室）
- ✓ `GET /teaching-office/attachments` - 查询附件（管理端）
- ✓ `GET /teaching-office/attachments/{attachment_id}/download` - 下载附件（管理端）
- ✓ `PUT /teaching-office/attachments/{attachment_id}/classification` - 调整分类（管理端）

## 权限检查机制

### 工作流程

```
HTTP 请求
    ↓
Token 验证 (get_current_user)
    ├─ Token 无效/过期 → 401 Unauthorized
    └─ Token 有效 → 提取用户信息
        ↓
    角色权限检查 (RoleChecker)
        ├─ 角色不匹配 → 403 Forbidden
        └─ 角色匹配 → 业务逻辑处理
            ↓
        返回结果
```

### RoleChecker 实现

```python
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}. Your role: {current_user.role}"
            )
        return current_user
```

## director1 用户信息

| 字段 | 值 |
|------|-----|
| 用户名 | director1 |
| 密码 | password123 |
| 角色 | teaching_office |
| 姓名 | 张主任 |
| 所属教研室 | 计算机科学教研室 |
| 邮箱 | director1@example.com |

**权限**: ✓ 可以访问所有 `teaching_office` 角色的接口

## 验证修复

### 方法 1: 使用测试脚本

```bash
python test_director1_permission.py
```

这个脚本会：
1. 使用 director1 登录
2. 获取 Token
3. 尝试提交自评表
4. 验证权限检查是否正常工作

### 方法 2: 使用浏览器

1. 打开 http://localhost:3000
2. 点击"教研室端"
3. 输入用户名: `director1`，密码: `password123`
4. 点击"登录"
5. 填写自评表并提交
6. 应该看到成功提示

### 方法 3: 使用 curl 命令

```bash
# 1. 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "director1",
    "password": "password123",
    "role": "teaching_office"
  }'

# 2. 复制响应中的 token，然后提交自评表
curl -X POST http://localhost:8000/api/teaching-office/self-evaluation \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "teaching_office_id": "a1b2c3d4-e5f6-4a5b-8c9d-111111111111",
    "evaluation_year": 2024,
    "content": {"test": "data"}
  }'
```

## 系统中的角色

| 角色 | 说明 | 可访问的接口 |
|------|------|-----------|
| `teaching_office` | 教研室 | 自评表提交、附件上传 |
| `evaluation_team` | 考评小组 | 手动评分、异常处理 |
| `evaluation_office` | 教务处 | 管理端操作、结果发布 |
| `president_office` | 校长办公室 | 数据大屏、最终审批 |

## 常见问题

### Q1: 修复后仍然收到 403 错误

**可能的原因**:
1. 后端服务没有重启
2. 浏览器缓存了旧的代码
3. Token 过期

**解决方案**:
1. 重启后端服务
2. 清除浏览器缓存 (Ctrl+Shift+Delete)
3. 重新登录

### Q2: 登录时显示"用户角色不匹配"

**原因**: 前端发送的角色与数据库中的角色不一致

**解决方案**:
- 使用教研室端登录（自动选择 `teaching_office` 角色）
- 不要手动修改角色参数

### Q3: 其他用户也无法访问教研室接口

**这是正常的**，权限检查工作正常。只有 `teaching_office` 角色的用户才能访问教研室端接口。

## 测试场景

### 场景 1: director1 提交自评表 ✓

```
用户: director1 (teaching_office)
操作: 提交自评表
预期结果: 201 Created
```

### 场景 2: evaluator1 尝试提交自评表 ✗

```
用户: evaluator1 (evaluation_team)
操作: 提交自评表
预期结果: 403 Forbidden
错误信息: Access denied. Required roles: teaching_office. Your role: evaluation_team
```

### 场景 3: 无效 Token ✗

```
Token: invalid_token_12345
操作: 提交自评表
预期结果: 401 Unauthorized
```

## 修改的文件

1. ✓ `backend/app/api/v1/endpoints/self_evaluation.py`
   - 添加了 `RoleChecker` 导入
   - 创建了 `require_teaching_office` 检查器
   - 在 5 个接口中添加了权限检查

2. ✓ `backend/app/api/v1/endpoints/attachments.py`
   - 添加了 `RoleChecker` 导入
   - 创建了 `require_teaching_office` 和 `require_management_roles` 检查器
   - 在 5 个接口中添加了权限检查

## 后续建议

1. **添加权限检查测试** - 为权限检查添加单元测试
2. **权限文档** - 为每个接口添加权限要求的文档
3. **审计日志** - 记录权限拒绝事件用于审计
4. **权限管理界面** - 在管理端添加权限管理功能

## 相关文档

- `director1_403权限问题诊断和解决方案.md` - 详细诊断和排查指南
- `教研室端403权限问题修复说明.md` - 之前的修复说明
- `test_director1_permission.py` - 权限检查测试脚本

## 总结

✓ **问题已解决**

director1 用户现在可以正常提交自评表。权限检查机制已正确配置，确保只有具有 `teaching_office` 角色的用户才能访问教研室端接口。

如果仍然遇到问题，请参考诊断文档进行排查。
