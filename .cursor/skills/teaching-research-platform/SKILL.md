---
name: teaching-research-platform
description: >-
  Context and conventions for the 教研室工作考评系统 (teaching research evaluation platform).
  Use when starting services, fixing uploads, or ensuring 评教小组端 (evaluation team) pages
  display real data from 教研室端 (teaching office). Includes common errors and fixes (upload
  TypeError, file_size 0, 403, home link). Covers frontend Vue/Vite, backend FastAPI, roles,
  key routes, and data flow.
---

# 教研室工作考评系统 - 项目 Skill

## 项目结构

- **前端**: `frontend/` — Vue 3 + Vite + Element Plus，开发端口 **5173**
- **后端**: `backend/` — FastAPI + Uvicorn，API 端口 **8000**，前缀 `/api`
- **角色**: 教研室端 `teaching_office` / 评教小组端 `evaluation_team`、`evaluation_office`

## 启动前后端

在项目根目录（含 `frontend`、`backend` 的目录）下：

**后端**（PowerShell）:
```powershell
Set-Location "backend"; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**（PowerShell）:
```powershell
Set-Location "frontend"; npm run dev
```

前端访问 `http://localhost:5173`，API 代理到 `http://localhost:8000`（vite proxy `/api` → 8000）。

## 核心原则：评教小组端必须显示真实数据

- 评教小组端（管理端）所有列表、统计、详情**必须来自后端接口**，不得使用纯前端假数据或静态占位。
- 数据来源：教研室端上传的自评表、附件、AI 评分与手动评分、异常处理记录等，均存于后端（MySQL + MinIO/本地存储）。
- 实现方式：页面挂载时调用对应 API（如 `scoringApi.getScoringAudit()`、`reviewApi.getAnomalies()`、`scoringApi.getEvaluationsForScoring()`），用返回结果驱动表格、统计卡片和详情抽屉。

## 关键 API 与页面对应

| 功能           | 前端路由/页面           | 后端接口（真实数据） |
|----------------|------------------------|----------------------|
| 评分进度       | `/scoring-progress`    | `GET /scoring/evaluations-for-scoring` |
| 我的评分记录   | `/my-scoring-records` | `GET /scoring/audit?reviewer_id=当前用户` |
| 全部评分/对比  | `/all-scoring-records`| `GET /scoring/audit`、`GET /scoring/all-scores/:id` |
| 异常数据/分析  | `/anomaly-handling`   | `GET /review/anomalies` |
| 处理记录/统计  | `/anomaly-records`    | `GET /review/anomalies`（已处理列表 + 前端统计） |
| 附件上传       | 自评表内 / 附件上传页  | `POST /teaching-office/attachments` |

## 教研室端附件上传（易错点）

- **前端**: 使用**预绑定的 change 处理函数**（如 `onTeachingProcessChange`），避免模板内联 `(file, fileList) => handleInlineFileChange(...)` 导致 `TypeError: ... is not a function`。
- **后端**: 上传前先 `await file.read()` 取 `file_size` 再 `await file.seek(0)`，再调用 `minio_service.upload_file_object()`，避免 `file_size` 为 0。
- **字段名映射**: 在组件外定义常量 `FIELD_NAME_MAP`，不要在 `handleInlineFileChange` 内创建大对象字面量，避免部分环境下“(intermediate value) is not a function”。
- 删除附件：后端提供 `DELETE /teaching-office/attachments/{id}`，MinIO 层实现 `delete_file(object_name)`。

## 首页与面包屑

- 评教小组端内所有「首页」链接（面包屑、PageHeader 首页按钮、侧栏顶部点击）应回到 **评教小组端首页**：`/management-home`。
- 实现：`PageHeader` 中根据 `route.path` 判断是否管理端路径，是则 `homePath = '/management-home'`；`ManagementHome` 的 `goToHome` 执行 `router.push('/management-home')`；各管理端子页面面包屑「首页」指向 `/management-home`。

## 评分规则

- 评分规则内容来自《教研室工作考核评分表》md，已整理进 `ScoringRules.vue`（常规教学工作、特色与亮点、负面清单三张表），路由 `/scoring-rules`。

## 常见报错与修复（今日处理总结）

遇到以下报错或现象时，按对应项排查与修复。

### 1. 附件上传：`TypeError: (intermediate value) ... is not a function`（NewSelfEvaluationForm.vue）

- **现象**: 点击「附件上传」选文件后控制台报错，堆栈在 `handleInlineFileChange`（约 1835/1886 行）。
- **原因**: 模板内联箭头函数或回调内创建大对象字面量，在部分编译/运行环境下被误当作可调用对象；或 Element Plus 对返回值做链式调用。
- **修复**:
  - 不在模板写 `:on-change="(file, fileList) => handleInlineFileChange(...)"`，改为**预绑定常量**（如 `onTeachingProcessChange`）并在模板用 `:on-change="onTeachingProcessChange"`。
  - 将 `fieldNameMap` 提到组件**模块级**常量 `FIELD_NAME_MAP`，不在 `handleInlineFileChange` 内创建对象。
  - change 处理函数用**块体**且不返回值：`() => { handleInlineFileChange(...) }`。
  - 兼容 `fileList` 为空或未传：`const list = Array.isArray(fileList) && fileList.length > 0 ? fileList : (file ? [file] : [])`，用 `list` 更新 ref 和做校验。

### 2. 附件上传后数据库 `file_size` 为 0

- **原因**: 先调用 `minio_service.upload_file_object(file, path)`（内部会 `read()`），再在接口里 `await file.read()` 取大小，流已消费。
- **修复**: 在 `backend/app/api/v1/endpoints/attachments.py` 中先 `file_content = await file.read()`、`file_size = len(file_content)`、`await file.seek(0)`，再调用 `upload_file_object`。

### 3. 附件删除 404 或接口不存在

- **原因**: 前端调 `DELETE /teaching-office/attachments/:id`，后端未实现。
- **修复**: 后端新增 `DELETE /attachments/{attachment_id}`（需教研室角色、自评表未锁定），并在 `minio_service` 中实现 `delete_file(object_name)`（MinIO 或本地存储删除）。

### 4. 附件上传页「已上传列表」为空或接口错

- **原因**: 视图用 `GET /teaching-office/attachments?evaluationId=xxx`，后端按自评表查的是 `GET /teaching-office/attachments/{evaluation_id}`（路径参数）。
- **修复**: 前端改为 `GET /teaching-office/attachments/${evaluationId}`，并对返回的 snake_case（如 `file_name`、`uploaded_at`）做兼容映射供表格使用。

### 5. 评教小组端「首页」没有回到管理端首页

- **现象**: 面包屑或 PageHeader 的「首页」跳到 `/` 或登录页。
- **修复**: 管理端相关页面的「首页」统一指向 `/management-home`：PageHeader 用 `homePath` 根据 `route.path` 判断；ManagementHome 的 `goToHome` 里 `router.push('/management-home')`；ManagementResultView、Publication、DataSync、ResultView 等面包屑「首页」改为 `:to="{ path: '/management-home' }"`。

### 6. 异常列表/处理记录 403（评教小组无法查看）

- **原因**: 后端 `GET /review/anomalies` 仅允许 `require_evaluation_office`。
- **修复**: 改为 `require_management_roles`（允许 `evaluation_team`、`evaluation_office`），评教小组可查看异常数据与处理记录。

### 7. PowerShell 下 `&&` 报错

- **现象**: 在 Windows PowerShell 中执行 `cd backend && python -m uvicorn ...` 报「不是有效的语句分隔符」。
- **修复**: 用分号或分开执行，例如 `Set-Location "backend"; python -m uvicorn ...`，或先 `cd backend` 再单独执行 uvicorn。

---

**排查顺序建议**: 先看控制台/网络（前端报错 vs 接口 4xx/5xx），再对号入座上面 1～6；涉及上传与存储时同时检查后端日志和 MinIO/本地目录。

## 术语对应

- **教研室端** = teaching office 端 = 填写自评表、上传附件的角色
- **评教小组端** = 管理端 = evaluation team / evaluation office = 手动评分、异常处理、查看全部评分与处理记录
- **真实数据流通** = 列表/统计/详情均通过调用后端接口获取并展示，无纯前端假数据

---

## 本次会话补充（管理端数据、导出、首页链接与账号）

以下内容为与用户对话的总结，仅作追加，不替代上文。

### 1. 管理端结果与异常接口（解决 404/500）

- **问题**: `GET /api/management/results?year=xxx` 返回 404；`GET /api/review/anomalies` 返回 500。
- **处理**:
  - 新增后端 **管理端结果汇总**：`backend/app/api/v1/endpoints/management.py`，实现 `GET /api/management/results`（支持 `year`、`status` 查询），在 `api.py` 中挂载 `prefix="/management"`。返回字段含：`id`、`teaching_office_name`、`evaluation_year`、`final_score`、`ai_score`、`manual_score_avg`、`manual_reviewer_count`、`approval_status`、`status`、`summary`、`submitted_at` 等，数据来自 DB。
  - **异常接口**：`get_anomalies` 的 `evaluation_id`/`status` 改为 `Optional[...] = Query(None)`；去掉 `order_by(..., nullsfirst())`（避免 SQLite 等不兼容）；`AnomalyResponse` 的 `description` 改为可选；构造响应时对 `type`/`indicator`/`description`/`status` 做 `or ""` / `or "pending"` 防止 None；列表与详情均做异常捕获，失败时返回空列表或 200 空数据，避免 500。
- **原则**: 管理端「确定最终得分」「得分统计」等均从上述接口取数；失败时仅清空列表并提示，**不再使用前端 mock**。

### 2. 管理端首页刷新空白

- **原因**: 刷新后 Pinia 状态清空，未从 localStorage 恢复，导致 `authStore.userRole` 为空，`menuItems`/`tabsConfig`/`functionsConfig` 为空数组，主内容区不渲染。
- **处理**:
  - 在 `ManagementHome.vue` 的 `onMounted` 中调用 `authStore.loadFromStorage()`。
  - 在 `router/index.ts` 的 `beforeEach` 中，对 `meta.requiresAuth` 的路由，若 localStorage 存在 `token` 和 `userRole`，则调用 `useAuthStore().loadFromStorage()`，保证任意需登录页刷新前先恢复登录状态。

### 3. 各页「返回评教小组端首页」链接

- **页面与文件**: 评分进度 `ScoringProgress.vue`、评分规则 `ScoringRules.vue`、异常数据处理/异常分析 `AnomalyHandling.vue`、我的评分记录 `MyScoringRecords.vue`。
- **实现**: 在标题或描述旁增加 `<router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>`，并统一样式 `.back-home-link { margin-left: 12px; color: #409eff; text-decoration: none; }`。

### 4. 确定最终得分与结果汇总使用真实数据

- **确定最终得分**（`FinalScore.vue`）：去掉本地 mock 列表，改为调用 `managementResultApi.getAllResults()`，仅展示状态为 `manually_scored`、`ready_for_final`、`finalized`、`published` 的记录，并映射为表格所需字段；请求失败时 `evaluations = []` 并提示。
- **结果汇总/得分统计**（`ManagementResultView.vue`）：已使用 `managementResultApi.getAllResults()`；**移除**加载失败时的 mock 回退，失败时仅 `results.value = []`，统计卡片（教研室总数、已公示、平均得分、最高得分）完全由接口返回的 `results` 计算，保证为真实数据。

### 5. 导出结果为 Word 文档

- **位置**: 考评结果汇总页（`ManagementResultView.vue`）的「导出结果」按钮。
- **实现**: 使用 Word 可打开的 HTML 格式，生成 `.doc` 文件下载。内容包含导出时间、考评年度、总条数，以及表格：排名、教研室名称、考评年度、最终得分、AI 评分、人工评分均值、审定结果、状态、汇总说明。导出当前筛选后的**全部**结果（与列表排序一致），文件名 `教研室考评结果汇总_年度.doc`。

### 6. 删除「评分详情」卡片

- **位置**: 管理端首页（`ManagementHome.vue`）— 评分记录 → 我的评分。
- **处理**: 从 `functionsConfig` 中移除「评分详情」卡片，仅保留「我的评分记录」；详情仍可在「我的评分记录」页内通过「详情」按钮和抽屉查看。

### 7. 评教小组端数据流通再次确认

- **原则**: 所有列表、统计、详情均来自后端接口；请求失败时清空列表并提示，不使用 mock。
- **关键页与接口**:
  - 评分进度：`scoringApi.getEvaluationsForScoring`，失败时 `allEvaluations = []`。
  - 手动评分：`scoringApi.getEvaluationsForScoring`，失败时 `evaluations = []`（已在 catch 中显式清空）。
  - 确定最终得分：`managementResultApi.getAllResults`，失败时 `evaluations = []`。
  - 结果汇总/得分统计：`managementResultApi.getAllResults`，失败时 `results = []`（无 mock）。
  - 异常数据处理/分析、异常处理记录：`reviewApi.getAnomalies`。
  - 我的评分记录、全部评分记录：`scoringApi.getScoringAudit`、`scoringApi.getAllScores`。
- **用户角色**: 从 localStorage（与 auth store 一致）读取，用于权限与展示，非 mock。

### 8. 各端账号数量（以项目 db_dump.sql / 文档为准）

| 端（角色） | 角色标识 | 账号数 | 示例用户名 |
|------------|----------|--------|------------|
| 教研室端 | teaching_office | 4 | director1, director2, director3, 123 |
| 评教小组端（考评小组） | evaluation_team | 3 | evaluator1, evaluator2, admin |
| 评教小组办公室端 | evaluation_office | 1 | office1 |
| 校长办公会端 | president_office | 1 | president1 |

合计 9 个账号。完整账号密码见 `系统账号密码清单.md`（如 director1/password123、evaluator1/password123 等）。

### 9. 启动前后端（再次强调）

- **前端**: 在含 `frontend` 的目录执行 `npm run dev`，访问 `http://localhost:5173`。
- **后端**: 在含 `backend` 的目录执行 `python -m uvicorn app.main:app --reload --port 8000`，API 为 `http://127.0.0.1:8000`，文档 `http://localhost:8000/docs`。
- **Windows PowerShell**: 用 `Set-Location "path"; command` 或分号连接命令，不要用 `&&`。

---

## 开发经验与报错总结

### 一、报错总结（按类型速查）

| 现象 / 报错 | 可能原因 | 处理方向 |
|-------------|----------|----------|
| 附件上传选文件后 `TypeError: ... is not a function` | 模板内联箭头函数或大对象字面量被误用 | 预绑定 handler、模块级 `FIELD_NAME_MAP`、change 用块体不返回值 |
| 附件入库 `file_size` 为 0 | 先 `upload` 再 `read()`，流已消费 | 先 `read()` 取长度并 `seek(0)`，再上传 |
| 附件删除 404 | 后端未实现 DELETE | 实现 `DELETE /teaching-office/attachments/{id}` 与 MinIO `delete_file` |
| 已上传列表为空 / 接口错 | 前端用 query 后端用 path | 前端用 `GET .../attachments/${evaluationId}` |
| 首页/面包屑跳到登录页 | 管理端首页未统一 | 管理端「首页」统一 `to="/management-home"`，PageHeader 用 `homePath` 判断 |
| 异常列表 403 | 接口仅允许 evaluation_office | 改为 `require_management_roles`（含 evaluation_team） |
| `GET /api/management/results` 404 | 后端无该路由 | 新增 `management.py`、`GET /management/results` 并挂载 |
| `GET /api/review/anomalies` 500 | 可选参数/空值/排序兼容性 | `Query(None)`、响应字段 `or ""`、去掉 nullsfirst、顶层 try/except 返回空列表 |
| 管理端首页刷新空白 | Pinia 未从 localStorage 恢复 | `onMounted` 与 `router.beforeEach` 中 `authStore.loadFromStorage()` |
| PowerShell `&&` 报错 | 语法不支持 | 用 `;` 或分两条命令 |
| 列表/统计显示 0 或旧数据 | 接口失败后仍用 mock 或未清空 | 移除 mock 回退，catch 里 `xxx.value = []` 并提示 |

### 二、开发经验

**1. 前后端数据约定**

- 评教小组端所有列表、统计、详情**只从后端接口取数**；接口失败时清空列表并提示，**禁止**用前端 mock 兜底。
- 新增管理端功能时，先确认后端是否有对应路由（如 `/api/management/xxx`），再在前端 `client.ts` 中封装并调用。
- 后端返回字段建议统一 snake_case；前端若用 camelCase，在接口层或组件内做一次映射即可。

**2. 后端接口与兼容性**

- 可选查询参数用 `Optional[T] = Query(None)`，避免缺参时类型解析导致 500。
- Pydantic 响应模型里对可能为空的字段用 `Optional` 或默认值，构造响应时对 DB 取出的值做 `or ""` / `or "pending"` 等，避免 None 导致序列化错误。
- 使用 `order_by(..., nullsfirst())` / `nullslast()` 前确认数据库支持（SQLite 等可能不支持），否则只保留 `order_by(..., desc())`。
- 列表类接口可做**顶层 try/except**：查询或序列化异常时记录日志并返回 200 + 空列表，避免 500 导致整页报错。

**3. 前端状态与路由**

- 依赖登录态或角色的页面，在**进入前**恢复 auth：在 `router.beforeEach` 里对 `requiresAuth` 且 localStorage 有 token/role 时执行 `loadFromStorage()`，避免刷新后角色为空、菜单/内容不渲染。
- 管理端子页面需要「返回首页」时，统一指向 `/management-home`，并在页面内提供「← 返回评教小组端首页」链接，样式统一用 `.back-home-link`。

**4. 附件与文件**

- 上传：前端用预绑定的 change 函数，避免内联复杂表达式；后端先读再 seek 再上传，保证 `file_size` 正确。
- 字段映射、分类等用模块级常量，避免在回调里创建大对象触发异常。

**5. 调试顺序建议**

1. 看浏览器控制台：是前端报错（如 TypeError）还是请求发出后的 4xx/5xx。
2. 看网络面板：请求 URL 是否正确（含 baseURL、是否走了代理）、状态码与响应体。
3. 4xx/5xx：先确认路由存在、权限依赖（role）正确，再查后端日志和 DB/存储是否异常。
4. 页面空白或列表为空：先确认是否已登录、auth 是否恢复（localStorage + loadFromStorage），再确认接口是否返回数据、前端是否用 mock 覆盖了真实数据。
