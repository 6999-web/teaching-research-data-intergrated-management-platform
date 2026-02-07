<template>
  <div class="user-feedback-example">
    <div class="page-header">
      <h1>用户交互反馈示例</h1>
      <p>展示各种用户反馈组件和工具的使用方法</p>
    </div>

    <div class="examples-grid">
      <!-- Button Loading States -->
      <el-card class="example-card">
        <template #header>
          <h3>按钮加载状态</h3>
        </template>

        <div class="button-group">
          <ActionButton
            type="primary"
            label="保存数据"
            :on-click="handleSave"
            success-message="数据保存成功！"
            error-message="保存失败，请重试"
          />

          <ActionButton
            type="danger"
            label="删除数据"
            :on-click="handleDelete"
            confirm-message="确定要删除这条数据吗？此操作不可恢复。"
            confirm-title="确认删除"
            success-message="删除成功"
          />

          <el-button
            type="success"
            :loading="uploadButton.loading.value"
            @click="handleUpload"
          >
            上传文件
          </el-button>
        </div>
      </el-card>

      <!-- Form Validation -->
      <el-card class="example-card">
        <template #header>
          <h3>表单验证反馈</h3>
        </template>

        <el-form
          ref="demoFormRef"
          :model="demoForm"
          :rules="demoRules"
          label-width="120px"
        >
          <el-form-item
            label="用户名"
            prop="username"
          >
            <el-input
              v-model="demoForm.username"
              placeholder="请输入用户名"
              @blur="validateUsername"
            />
          </el-form-item>

          <el-form-item
            label="邮箱"
            prop="email"
          >
            <el-input
              v-model="demoForm.email"
              placeholder="请输入邮箱"
              @blur="validateEmail"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="formSubmission.submitting.value"
              @click="submitForm"
            >
              提交表单
            </el-button>
            <el-button @click="resetForm">
              重置
            </el-button>
          </el-form-item>
        </el-form>

        <div
          v-if="formSubmission.validation.hasErrors()"
          class="validation-errors"
        >
          <el-alert
            title="表单验证错误"
            type="error"
            :closable="false"
          >
            <ul>
              <li
                v-for="(error, field) in formSubmission.validation.errors.value"
                :key="field"
              >
                {{ field }}: {{ error }}
              </li>
            </ul>
          </el-alert>
        </div>
      </el-card>

      <!-- Progress Indicators -->
      <el-card class="example-card">
        <template #header>
          <h3>进度指示器</h3>
        </template>

        <div class="progress-examples">
          <ProgressIndicator
            :percentage="uploadProgress"
            title="文件上传进度"
            :description="`正在上传文件... ${uploadProgress}%`"
            :show-time="true"
            :estimated-time="estimatedTime"
          />

          <el-divider />

          <ProgressIndicator
            :percentage="stepProgress"
            title="多步骤流程"
            :show-steps="true"
            :steps="processSteps"
            :current-step="currentProcessStep"
          />

          <div class="button-group">
            <el-button
              type="primary"
              @click="startUpload"
            >
              开始上传
            </el-button>
            <el-button
              type="success"
              @click="startProcess"
            >
              开始流程
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- Loading Overlay -->
      <el-card class="example-card">
        <template #header>
          <h3>加载遮罩层</h3>
        </template>

        <div class="loading-examples">
          <div
            class="loading-demo-area"
            style="position: relative; height: 200px"
          >
            <LoadingOverlay
              :visible="showLocalLoading"
              text="正在加载数据..."
              description="请稍候，这可能需要几秒钟"
            />

            <div class="demo-content">
              <p>这是一些内容区域</p>
              <p>当加载时会被遮罩层覆盖</p>
            </div>
          </div>

          <div class="button-group">
            <el-button
              type="primary"
              @click="showLocalLoading = !showLocalLoading"
            >
              切换局部加载
            </el-button>
            <el-button
              type="warning"
              @click="showFullscreenLoading"
            >
              显示全屏加载
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- Message Feedback -->
      <el-card class="example-card">
        <template #header>
          <h3>消息反馈</h3>
        </template>

        <div class="button-group">
          <el-button
            type="success"
            @click="showSuccessMessage"
          >
            成功消息
          </el-button>
          <el-button
            type="danger"
            @click="showErrorMessage"
          >
            错误消息
          </el-button>
          <el-button
            type="warning"
            @click="showWarningMessage"
          >
            警告消息
          </el-button>
          <el-button
            type="info"
            @click="showInfoMessage"
          >
            信息消息
          </el-button>
          <el-button
            type="primary"
            @click="showNotificationMessage"
          >
            通知消息
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- Operation Feedback Component -->
    <OperationFeedback ref="operationFeedbackRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import ActionButton from '@/components/ActionButton.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import ProgressIndicator from '@/components/ProgressIndicator.vue'
import OperationFeedback from '@/components/OperationFeedback.vue'
import { useButtonLoading } from '@/composables/useButtonLoading'
import { useFormSubmission } from '@/composables/useFormValidation'
import {
  showSuccess,
  showError,
  showWarning,
  showInfo,
  showNotification,
  showLoading,
  hideLoading
} from '@/utils/feedback'

// Button loading states
const uploadButton = useButtonLoading()

// Form
const demoFormRef = ref<FormInstance>()
const demoForm = reactive({
  username: '',
  email: ''
})

const demoRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

const formSubmission = useFormSubmission(
  demoFormRef,
  async (data) => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))
    console.log('Form submitted:', data)
  },
  {
    successMessage: '表单提交成功！',
    errorMessage: '表单提交失败，请重试'
  }
)

// Progress
const uploadProgress = ref(0)
const estimatedTime = computed(() => {
  const remaining = 100 - uploadProgress.value
  return Math.ceil((remaining / 100) * 30) // Estimate 30 seconds total
})

const processSteps = ['初始化', '数据验证', '处理数据', '保存结果', '完成']
const currentProcessStep = ref(0)
const stepProgress = computed(() => {
  return (currentProcessStep.value / (processSteps.length - 1)) * 100
})

// Loading
const showLocalLoading = ref(false)
const operationFeedbackRef = ref()

// Handlers
const handleSave = async () => {
  await new Promise((resolve) => setTimeout(resolve, 1500))
  // Simulate success
}

const handleDelete = async () => {
  await new Promise((resolve) => setTimeout(resolve, 1000))
  // Simulate success
}

const handleUpload = async () => {
  await uploadButton.execute(
    async () => {
      await new Promise((resolve) => setTimeout(resolve, 2000))
      showSuccess('文件上传成功！')
    },
    {
      errorMessage: '文件上传失败'
    }
  )
}

const validateUsername = () => {
  formSubmission.validation.validateField(demoFormRef.value, 'username')
}

const validateEmail = () => {
  formSubmission.validation.validateField(demoFormRef.value, 'email')
}

const submitForm = async () => {
  await formSubmission.submit(demoForm)
}

const resetForm = () => {
  demoFormRef.value?.resetFields()
  formSubmission.validation.clearValidation(demoFormRef.value)
}

const startUpload = () => {
  uploadProgress.value = 0
  const interval = setInterval(() => {
    uploadProgress.value += 10
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
      showSuccess('上传完成！')
    }
  }, 500)
}

const startProcess = () => {
  currentProcessStep.value = 0
  const interval = setInterval(() => {
    currentProcessStep.value++
    if (currentProcessStep.value >= processSteps.length) {
      clearInterval(interval)
      showSuccess('流程完成！')
      currentProcessStep.value = 0
    }
  }, 1500)
}

const showFullscreenLoading = () => {
  const loading = showLoading('正在处理，请稍候...')
  setTimeout(() => {
    hideLoading(loading)
    showSuccess('处理完成！')
  }, 3000)
}

const showSuccessMessage = () => {
  showSuccess('这是一条成功消息！')
  if (operationFeedbackRef.value) {
    operationFeedbackRef.value.addFeedback('success', '操作成功完成', {
      title: '成功'
    })
  }
}

const showErrorMessage = () => {
  showError('这是一条错误消息！')
  if (operationFeedbackRef.value) {
    operationFeedbackRef.value.addFeedback('error', '操作失败，请重试', {
      title: '错误'
    })
  }
}

const showWarningMessage = () => {
  showWarning('这是一条警告消息！')
  if (operationFeedbackRef.value) {
    operationFeedbackRef.value.addFeedback('warning', '请注意检查输入', {
      title: '警告'
    })
  }
}

const showInfoMessage = () => {
  showInfo('这是一条信息消息！')
  if (operationFeedbackRef.value) {
    operationFeedbackRef.value.addFeedback('info', '这是一些提示信息', {
      title: '提示'
    })
  }
}

const showNotificationMessage = () => {
  showNotification('系统通知', '您有一条新消息', 'info')
}
</script>

<style scoped>
.user-feedback-example {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #303133;
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.examples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
}

.example-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.example-card h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.validation-errors {
  margin-top: 20px;
}

.validation-errors ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.validation-errors li {
  margin: 5px 0;
  color: #f56c6c;
}

.progress-examples {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-examples {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading-demo-area {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  background-color: #f5f7fa;
}

.demo-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.demo-content p {
  margin: 10px 0;
  color: #606266;
}
</style>
