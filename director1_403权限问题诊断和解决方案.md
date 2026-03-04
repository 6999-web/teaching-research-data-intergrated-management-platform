# director1 用户 403 Forbidden 权限问题诊断和解决方案

## 问题现象

- **用户**: director1
- **操作**: 在教研室端提交自评表
- **错误**: 403 Forbidden
- **接口**: `POST /api/teaching-office/self-evaluation`
- **状态**: 登录成功，已获取 Token，但提交时被拦截

## 问题诊断

### 1. 用户角色验证

根据系统账号密码清单，`director1` 的配置如下：

```
用户名: director1
密码: password123
角色: teaching_office
姓名: 张主任
所属教研室: 计算机科学教研室
```

**结论**: director1 的角色确实是 `teaching_office`，这是正确的。

### 2. 接口权限检查

在我之前的修复中，已经为 `self_evaluation.py` 中的所有接口添加了权限检查：

```python
# 导入权限检查器
from app.core.deps import get_db, get_current_user, RoleChecker

# 创建教研室角色检查器
require_teaching_office = RoleChecker(["teaching_office"])

# 在接口中使用
@router.post("/self-evaluation", response_model=SelfEvaluationSaveResponse)
def create_self_evaluation(
    evaluation_data: SelfEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teaching_office),  # ← 权限检查
):
    ...
```

### 3. 权限检查流程

```
请求 → Token 验证 (401) → 角色权限检查 (403) → 业务逻辑
```

**流程说明**:
1. **Token 验证** (`get_current_user`)
   - 验证 JWT Token 的有效性
   - 如果 Token 无效或过期，返回 401 Unauthorized
   - 如果有效，提取用户信息（包括角色）

2. **角色权限检查** (`RoleChecker`)
   - 检查用户的角色是否在允许列表中
   - 对于 `/teaching-office/self-evaluation`，允许的角色是 `["teaching_office"]`
   - 如果角色不匹配，返回 403 Forbidden

### 4. 可能的 403 原因

#### 原因 A: Token 中的角色信息不正确
- **症状**: 登录时返回的 Token 中角色不是 `teaching_office`
- **检查方法**: 在浏览器控制台查看登录响应中的 `role` 字段

#### 原因 B: 前端没有正确保存角色信息
- **症状**: 登录成功但 localStorage 中的 `userRole` 不正确
- **检查方法**: 打开浏览器开发者工具 → Application → LocalStorage，查看 `userRole` 的值

#### 原因 C: 前端在发送请求时没有正确传递 Token
- **症状**: 请求头中没有 `Authorization: Bearer <token>`
- **检查方法**: 在浏览器开发者工具 → Network 中查看请求头

#### 原因 D: 后端的权限检查配置有误
- **症状**: 即使角色正确，仍然返回 403
- **检查方法**: 查看后端日志中的详细错误信息

## 解决方案

### 步骤 1: 验证登录响应

在浏览器控制台中执行以下代码，查看登录响应：

```javascript
// 打开浏览器开发者工具 (F12)
// 在 Console 标签页中执行：

// 查看 localStorage 中保存的用户信息
console.log('Token:', localStorage.getItem('token'))
console.log('User Role:', localStorage.getItem('userRole'))
console.log('User ID:', localStorage.getItem('userId'))
console.log('Teaching Office ID:', localStorage.getItem('teachingOfficeId'))
```

**预期结果**:
```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
User Role: teaching_office
User ID: <uuid>
Teaching Office ID: <uuid>
```

### 步骤 2: 验证 Token 内容

使用 JWT 解码工具查看 Token 中的内容：

1. 访问 https://jwt.io
2. 将 Token 粘贴到 "Encoded" 区域
3. 查看 "Decoded" 中的 payload 部分

**预期的 payload**:
```json
{
  "sub": "director1",
  "user_id": "<uuid>",
  "role": "teaching_office",
  "exp": <timestamp>
}
```

### 步骤 3: 检查网络请求

在浏览器开发者工具中查看提交请求：

1. 打开 DevTools (F12)
2. 切换到 Network 标签页
3. 提交自评表
4. 找到 `self-evaluation` 请求
5. 查看请求头中的 `Authorization` 字段

**预期的请求头**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### 步骤 4: 检查后端日志

查看后端服务的日志输出，找到相关的错误信息：

```bash
# 后端日志文件位置
backend/error.log

# 查看最近的错误
tail -f backend/error.log
```

**预期的错误信息**（如果有权限问题）:
```
Access denied. Required roles: teaching_office. Your role: <actual_role>
```

### 步骤 5: 重新登录

如果以上检查都没有发现问题，尝试重新登录：

1. 清除浏览器缓存和 localStorage
   ```javascript
   // 在浏览器控制台执行
   localStorage.clear()
   sessionStorage.clear()
   ```

2. 刷新页面并重新登录

3. 使用正确的凭证：
   - 用户名: `director1`
   - 密码: `password123`
   - 端口: 教研室端（自动选择 `teaching_office` 角色）

## 权限检查代码详解

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

### 接口权限配置

```python
# 教研室端接口 - 仅 teaching_office 角色可访问
require_teaching_office = RoleChecker(["teaching_office"])

@router.post("/self-evaluation")
def create_self_evaluation(
    ...,
    current_user: User = Depends(require_teaching_office),
):
    ...

# 管理端接口 - 仅管理角色可访问
require_management_roles = RoleChecker(["evaluation_team", "evaluation_office"])

@router.get("/evaluations-for-scoring")
def get_evaluations_for_scoring(
    ...,
    current_user: User = Depends(require_management_roles),
):
    ...
```

## 常见问题排查

### Q1: 登录时显示"用户角色不匹配"错误

**原因**: 前端发送的角色与数据库中的角色不一致

**解决方案**:
- 确保使用教研室端登录（自动选择 `teaching_office` 角色）
- 不要手动修改角色参数

### Q2: 登录成功但提交时仍然 403

**原因**: 可能是以下几种情况：
1. Token 过期
2. 浏览器缓存了旧的 Token
3. 后端权限配置有误

**解决方案**:
1. 清除浏览器缓存
2. 重新登录
3. 检查后端日志

### Q3: 其他用户（如 evaluation_team）也无法访问教研室接口

**原因**: 这是正常的，权限检查工作正常

**说明**: 只有 `teaching_office` 角色的用户才能访问教研室端接口

## 修改的文件

1. **backend/app/api/v1/endpoints/self_evaluation.py**
   - 添加了 `RoleChecker` 导入
   - 创建了 `require_teaching_office` 检查器
   - 在 5 个接口中添加了权限检查

2. **backend/app/api/v1/endpoints/attachments.py**
   - 添加了 `RoleChecker` 导入
   - 创建了 `require_teaching_office` 和 `require_management_roles` 检查器
   - 在 5 个接口中添加了权限检查

## 验证修复

### 测试场景 1: director1 提交自评表（应该成功）

```bash
# 1. 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "director1",
    "password": "password123",
    "role": "teaching_office"
  }'

# 响应应该包含 token 和 role: teaching_office

# 2. 提交自评表
curl -X POST http://localhost:8000/api/teaching-office/self-evaluation \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "teaching_office_id": "...",
    "evaluation_year": 2024,
    "content": {...}
  }'

# 预期结果: 201 Created ✓
```

### 测试场景 2: evaluator1 尝试提交自评表（应该失败）

```bash
# 1. 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "evaluator1",
    "password": "password123",
    "role": "evaluation_team"
  }'

# 响应应该包含 token 和 role: evaluation_team

# 2. 尝试提交自评表
curl -X POST http://localhost:8000/api/teaching-office/self-evaluation \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "teaching_office_id": "...",
    "evaluation_year": 2024,
    "content": {...}
  }'

# 预期结果: 403 Forbidden
# 错误信息: Access denied. Required roles: teaching_office. Your role: evaluation_team
```

## 后续建议

1. **添加权限检查测试** - 为权限检查添加单元测试
2. **权限文档** - 为每个接口添加权限要求的文档
3. **审计日志** - 记录权限拒绝事件用于审计
4. **权限管理界面** - 在管理端添加权限管理功能

## 相关文件

- `backend/app/core/deps.py` - 权限检查器定义
- `backend/app/core/security.py` - Token 验证逻辑
- `backend/app/models/user.py` - 用户模型和角色定义
- `backend/app/api/v1/endpoints/self_evaluation.py` - 自评表接口
- `backend/app/api/v1/endpoints/attachments.py` - 附件接口
- `frontend/src/stores/auth.ts` - 前端认证 store
- `frontend/src/api/client.ts` - 前端 API 客户端
