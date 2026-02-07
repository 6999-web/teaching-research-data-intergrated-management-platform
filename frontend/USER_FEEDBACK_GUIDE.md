# 用户交互反馈系统使用指南

本指南介绍如何在教研室工作考评系统中使用统一的用户交互反馈机制。

## 概述

用户交互反馈系统提供了一套完整的工具和组件，用于在用户操作时提供即时、清晰的反馈，包括：

- ✅ 按钮加载状态
- ✅ 操作成功/失败提示
- ✅ 表单实时验证反馈
- ✅ 进度指示器
- ✅ 加载遮罩层
- ✅ 消息通知

## 核心工具

### 1. 反馈工具函数 (`utils/feedback.ts`)

提供标准化的消息反馈函数：

```typescript
import {
  showSuccess,
  showError,
  showWarning,
  showInfo,
  showNotification,
  showLoading,
  hideLoading,
  handleApiError,
  FEEDBACK_MESSAGES
} from '@/utils/feedback'

// 显示成功消息
showSuccess('保存成功')

// 显示错误消息
showError('保存失败，请重试')

// 显示警告消息
showWarning('请先完成必填项')

// 显示信息消息
showInfo('数据已更新')

// 显示通知（更显眼）
showNotification('系统通知', '您有新消息', 'info')

// 显示全屏加载
const loading = showLoading('正在处理...')
// ... 执行操作
hideLoading(loading)

// 处理API错误（自动显示友好错误消息）
try {
  await api.saveData(data)
} catch (error) {
  handleApiError(error, '保存失败')
}

// 使用预定义消息
showSuccess(FEEDBACK_MESSAGES.SAVE_SUCCESS)
showError(FEEDBACK_MESSAGES.SAVE_ERROR)
```

### 2. 按钮加载状态 (`composables/useButtonLoading.ts`)

管理按钮的加载状态：

```typescript
import { useButtonLoading } from '@/composables/useButtonLoading'

const saveButton = useButtonLoading()

const handleSave = async () => {
  await saveButton.execute(
    async () => {
      // 执行保存操作
      await api.saveData(data)
    },
    {
      onSuccess: () => {
        showSuccess('保存成功')
      },
      errorMessage: '保存失败，请重试'
    }
  )
}

// 在模板中使用
<el-button
  type="primary"
  :loading="saveButton.loading.value"
  @click="handleSave"
>
  保存
</el-button>
```

### 3. 表单验证反馈 (`composables/useFormValidation.ts`)

增强表单验证体验：

```typescript
import { useFormValidation, useFormSubmission } from '@/composables/useFormValidation'

const formRef = ref<FormInstance>()
const validation = useFormValidation()

// 验证整个表单
const isValid = await validation.validate(formRef.value)

// 验证单个字段
await validation.validateField(formRef.value, 'username')

// 清除验证错误
validation.clearValidation(formRef.value)

// 或使用表单提交助手
const formSubmission = useFormSubmission(
  formRef,
  async (data) => {
    await api.submitForm(data)
  },
  {
    successMessage: '提交成功',
    errorMessage: '提交失败'
  }
)

// 提交表单（自动验证）
await formSubmission.submit(formData)
```

## 核心组件

### 1. ActionButton 组件

带有内置加载状态和确认对话框的按钮：

```vue
<ActionButton
  type="primary"
  label="保存数据"
  :on-click="handleSave"
  success-message="保存成功！"
  error-message="保存失败，请重试"
/>

<ActionButton
  type="danger"
  label="删除"
  :on-click="handleDelete"
  confirm-message="确定要删除吗？"
  confirm-title="确认删除"
  success-message="删除成功"
/>
```

**Props:**
- `type`: 按钮类型 (primary, success, warning, danger, info)
- `label`: 按钮文本
- `onClick`: 异步点击处理函数
- `confirmMessage`: 确认对话框消息（可选）
- `confirmTitle`: 确认对话框标题（可选）
- `successMessage`: 成功提示消息（可选）
- `errorMessage`: 错误提示消息（可选）
- `disabled`: 是否禁用

### 2. LoadingOverlay 组件

加载遮罩层：

```vue
<!-- 局部加载 -->
<div style="position: relative; height: 300px">
  <LoadingOverlay
    :visible="loading"
    text="正在加载数据..."
    description="请稍候，这可能需要几秒钟"
  />
  <div>内容区域</div>
</div>

<!-- 全屏加载 -->
<LoadingOverlay
  :visible="loading"
  text="正在处理..."
  fullscreen
/>

<!-- 带进度条的加载 -->
<LoadingOverlay
  :visible="loading"
  text="上传中..."
  :show-progress="true"
  :progress="uploadProgress"
/>
```

**Props:**
- `visible`: 是否显示
- `text`: 加载文本
- `description`: 详细描述（可选）
- `fullscreen`: 是否全屏
- `showProgress`: 是否显示进度条
- `progress`: 进度百分比 (0-100)

### 3. ProgressIndicator 组件

进度指示器：

```vue
<!-- 简单进度条 -->
<ProgressIndicator
  :percentage="uploadProgress"
  title="文件上传进度"
  :description="`正在上传... ${uploadProgress}%`"
/>

<!-- 带步骤的进度 -->
<ProgressIndicator
  :percentage="stepProgress"
  title="处理流程"
  :show-steps="true"
  :steps="['初始化', '验证', '处理', '完成']"
  :current-step="currentStep"
/>

<!-- 带时间估算 -->
<ProgressIndicator
  :percentage="progress"
  :show-time="true"
  :estimated-time="estimatedSeconds"
/>
```

**Props:**
- `percentage`: 进度百分比 (0-100)
- `title`: 标题
- `description`: 描述
- `showSteps`: 是否显示步骤
- `steps`: 步骤数组
- `currentStep`: 当前步骤索引
- `showTime`: 是否显示预计时间
- `estimatedTime`: 预计剩余时间（秒）

### 4. OperationFeedback 组件

操作反馈通知（类似 Toast）：

```vue
<template>
  <OperationFeedback ref="feedbackRef" />
</template>

<script setup>
const feedbackRef = ref()

// 添加反馈
feedbackRef.value.addFeedback('success', '操作成功', {
  title: '成功',
  duration: 3000
})

feedbackRef.value.addFeedback('error', '操作失败', {
  title: '错误',
  dismissible: true
})
</script>
```

## 实际应用示例

### 示例 1: 自评表保存

```vue
<template>
  <el-form ref="formRef" :model="formData" :rules="rules">
    <!-- 表单字段 -->
    
    <el-button
      type="primary"
      :loading="saving"
      @click="handleSave"
    >
      保存
    </el-button>
  </el-form>
</template>

<script setup>
import { ref } from 'vue'
import { showSuccess, showError, handleApiError } from '@/utils/feedback'
import { selfEvaluationApi } from '@/api/client'

const formRef = ref()
const saving = ref(false)
const formData = reactive({ /* ... */ })

const handleSave = async () => {
  // 验证表单
  try {
    await formRef.value.validate()
  } catch (error) {
    showError('请检查表单填写是否完整')
    return
  }

  saving.value = true

  try {
    await selfEvaluationApi.save(formData)
    showSuccess('保存成功')
  } catch (error) {
    handleApiError(error, '保存失败，请重试')
  } finally {
    saving.value = false
  }
}
</script>
```

### 示例 2: 文件上传带进度

```vue
<template>
  <div>
    <el-upload
      :on-progress="handleProgress"
      :on-success="handleSuccess"
      :on-error="handleError"
    >
      <el-button type="primary" :loading="uploading">
        上传文件
      </el-button>
    </el-upload>

    <ProgressIndicator
      v-if="uploading"
      :percentage="uploadProgress"
      title="文件上传中"
      :description="`已上传 ${uploadProgress}%`"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { showSuccess, showError } from '@/utils/feedback'
import ProgressIndicator from '@/components/ProgressIndicator.vue'

const uploading = ref(false)
const uploadProgress = ref(0)

const handleProgress = (event) => {
  uploading.value = true
  uploadProgress.value = Math.floor(event.percent || 0)
}

const handleSuccess = () => {
  uploading.value = false
  uploadProgress.value = 100
  showSuccess('文件上传成功')
}

const handleError = (error) => {
  uploading.value = false
  uploadProgress.value = 0
  showError('文件上传失败，请重试')
}
</script>
```

### 示例 3: 异步操作带确认

```vue
<template>
  <ActionButton
    type="danger"
    label="删除附件"
    :on-click="handleDelete"
    confirm-message="确定要删除这个附件吗？删除后无法恢复。"
    confirm-title="确认删除"
    success-message="附件已删除"
    error-message="删除失败，请重试"
  />
</template>

<script setup>
import ActionButton from '@/components/ActionButton.vue'
import { attachmentApi } from '@/api/client'

const handleDelete = async () => {
  await attachmentApi.delete(attachmentId)
  // 成功和错误消息由 ActionButton 自动处理
}
</script>
```

## 最佳实践

### 1. 按钮加载状态

✅ **推荐做法:**
```vue
<el-button
  type="primary"
  :loading="saving"
  @click="handleSave"
>
  {{ saving ? '保存中...' : '保存' }}
</el-button>
```

❌ **不推荐:**
```vue
<!-- 没有加载状态，用户不知道操作是否在进行 -->
<el-button type="primary" @click="handleSave">
  保存
</el-button>
```

### 2. 操作反馈

✅ **推荐做法:**
```typescript
try {
  await api.saveData(data)
  showSuccess('保存成功')  // 明确的成功反馈
} catch (error) {
  handleApiError(error, '保存失败')  // 友好的错误提示
}
```

❌ **不推荐:**
```typescript
try {
  await api.saveData(data)
  // 没有任何反馈，用户不知道是否成功
} catch (error) {
  console.error(error)  // 只在控制台输出，用户看不到
}
```

### 3. 表单验证

✅ **推荐做法:**
```vue
<el-form-item
  label="用户名"
  prop="username"
>
  <el-input
    v-model="form.username"
    @blur="validateField('username')"
  />
</el-form-item>
```

❌ **不推荐:**
```vue
<!-- 没有实时验证，用户提交时才发现错误 -->
<el-form-item label="用户名">
  <el-input v-model="form.username" />
</el-form-item>
```

### 4. 长时间操作

✅ **推荐做法:**
```vue
<LoadingOverlay
  :visible="processing"
  text="正在处理数据..."
  description="这可能需要几分钟，请耐心等待"
  :show-progress="true"
  :progress="progress"
/>
```

❌ **不推荐:**
```vue
<!-- 没有进度提示，用户不知道要等多久 -->
<div v-if="processing">处理中...</div>
```

## 消息持续时间建议

- **成功消息**: 2-3秒（短暂提示即可）
- **错误消息**: 5秒或更长（用户需要时间阅读错误信息）
- **警告消息**: 3-4秒
- **信息消息**: 3秒
- **重要通知**: 不自动关闭或10秒以上

## 可访问性考虑

1. **颜色不是唯一指示器**: 使用图标和文字配合颜色
2. **加载状态要明确**: 使用 loading 属性和文字提示
3. **错误消息要具体**: 告诉用户具体哪里出错，如何修复
4. **操作可撤销**: 重要操作前要确认，提供撤销选项

## 性能优化

1. **防抖和节流**: 对频繁触发的验证使用防抖
2. **避免过度反馈**: 不要每个小操作都显示消息
3. **合并相似消息**: 使用 grouping 选项合并相同消息
4. **及时清理**: 组件卸载时清理定时器和监听器

## 故障排查

### 问题: 消息不显示

**解决方案:**
1. 检查是否正确导入工具函数
2. 确认 Element Plus 已正确安装
3. 检查浏览器控制台是否有错误

### 问题: 加载状态不更新

**解决方案:**
1. 确保使用 ref 或 reactive 包装状态
2. 检查 finally 块是否正确设置 loading 为 false
3. 确认异步操作有正确的错误处理

### 问题: 表单验证不触发

**解决方案:**
1. 检查 rules 是否正确定义
2. 确认 prop 属性与 rules 键名匹配
3. 验证 trigger 设置是否正确（blur, change）

## 总结

用户交互反馈系统提供了完整的工具集，确保用户在使用系统时能够获得及时、清晰的反馈。遵循本指南的最佳实践，可以显著提升用户体验。

关键要点：
- ✅ 所有按钮操作都应有加载状态
- ✅ 所有异步操作都应有成功/失败反馈
- ✅ 表单应提供实时验证反馈
- ✅ 长时间操作应显示进度指示
- ✅ 错误消息应友好且具体
