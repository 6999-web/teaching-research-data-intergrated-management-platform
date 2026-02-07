<template>
  <div class="self-evaluation-form">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h2>教研室工作自评表</h2>
          <span class="evaluation-year">{{ formData.evaluationYear }}年度</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="180px"
        label-position="left"
        class="evaluation-form"
      >
        <!-- 教学过程管理 -->
        <el-form-item
          label="教学过程管理"
          prop="content.teachingProcessManagement"
        >
          <el-input
            v-model="formData.content.teachingProcessManagement"
            type="textarea"
            :rows="4"
            placeholder="请填写教学过程管理相关内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 课程建设 -->
        <el-form-item
          label="课程建设"
          prop="content.courseConstruction"
        >
          <el-input
            v-model="formData.content.courseConstruction"
            type="textarea"
            :rows="4"
            placeholder="请填写课程建设相关内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 教学改革项目个数 -->
        <el-form-item
          label="教学改革项目个数"
          prop="content.teachingReformProjects"
        >
          <div class="number-input-wrapper">
            <el-input-number
              v-model="formData.content.teachingReformProjects"
              :min="0"
              :max="100"
              :step="1"
              placeholder="请输入项目个数"
            />
            <span class="input-hint">个</span>
          </div>
          <div class="field-description">
            请填写本年度教学改革项目的总数量
          </div>
        </el-form-item>

        <!-- 荣誉表彰个数 -->
        <el-form-item
          label="荣誉表彰个数"
          prop="content.honoraryAwards"
        >
          <div class="number-input-wrapper">
            <el-input-number
              v-model="formData.content.honoraryAwards"
              :min="0"
              :max="100"
              :step="1"
              placeholder="请输入荣誉个数"
            />
            <span class="input-hint">个</span>
          </div>
          <div class="field-description">
            请填写本年度获得的荣誉表彰总数量
          </div>
        </el-form-item>

        <!-- 教学质量 -->
        <el-form-item
          label="教学质量"
          prop="content.teachingQuality"
        >
          <el-input
            v-model="formData.content.teachingQuality"
            type="textarea"
            :rows="4"
            placeholder="请填写教学质量相关内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 学生指导 -->
        <el-form-item
          label="学生指导"
          prop="content.studentGuidance"
        >
          <el-input
            v-model="formData.content.studentGuidance"
            type="textarea"
            :rows="4"
            placeholder="请填写学生指导相关内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 科研工作 -->
        <el-form-item
          label="科研工作"
          prop="content.scientificResearch"
        >
          <el-input
            v-model="formData.content.scientificResearch"
            type="textarea"
            :rows="4"
            placeholder="请填写科研工作相关内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 团队建设 -->
        <el-form-item
          label="团队建设"
          prop="content.teamBuilding"
        >
          <el-input
            v-model="formData.content.teamBuilding"
            type="textarea"
            :rows="4"
            placeholder="请填写团队建设相关内容"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item class="form-actions">
          <el-button
            type="primary"
            :loading="saving"
            @click="handleSave"
          >
            保存
          </el-button>
          <el-button @click="handlePreview">
            预览
          </el-button>
          <el-button
            type="success"
            :disabled="isSubmitted"
            @click="handleSubmit"
          >
            {{ isSubmitted ? '已提交' : '提交表单' }}
          </el-button>
          <el-button
            type="success"
            @click="handleAttachments"
          >
            上传附件
          </el-button>
          <el-button 
            v-if="showAIScoringButton" 
            type="warning" 
            :loading="aiScoringLoading"
            @click="handleTriggerAIScoring"
          >
            触发AI评分
          </el-button>
          <el-button @click="handleReset">
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      title="自评表预览"
      width="70%"
      :close-on-click-modal="false"
    >
      <div class="preview-content">
        <div class="preview-header">
          <h3>{{ formData.evaluationYear }}年度教研室工作自评表</h3>
        </div>
        
        <div class="preview-section">
          <div class="preview-item">
            <label>教学过程管理：</label>
            <p>{{ formData.content.teachingProcessManagement || '未填写' }}</p>
          </div>
          
          <div class="preview-item">
            <label>课程建设：</label>
            <p>{{ formData.content.courseConstruction || '未填写' }}</p>
          </div>
          
          <div class="preview-item">
            <label>教学改革项目个数：</label>
            <p>{{ formData.content.teachingReformProjects }} 个</p>
          </div>
          
          <div class="preview-item">
            <label>荣誉表彰个数：</label>
            <p>{{ formData.content.honoraryAwards }} 个</p>
          </div>
          
          <div class="preview-item">
            <label>教学质量：</label>
            <p>{{ formData.content.teachingQuality || '未填写' }}</p>
          </div>
          
          <div class="preview-item">
            <label>学生指导：</label>
            <p>{{ formData.content.studentGuidance || '未填写' }}</p>
          </div>
          
          <div class="preview-item">
            <label>科研工作：</label>
            <p>{{ formData.content.scientificResearch || '未填写' }}</p>
          </div>
          
          <div class="preview-item">
            <label>团队建设：</label>
            <p>{{ formData.content.teamBuilding || '未填写' }}</p>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="previewVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { SelfEvaluationFormData } from '@/types/selfEvaluation'
import { selfEvaluationApi } from '@/api/client'

// Props
interface Props {
  teachingOfficeId: string
  evaluationYear?: number
  initialData?: SelfEvaluationFormData
  evaluationId?: string
}

const props = withDefaults(defineProps<Props>(), {
  evaluationYear: () => new Date().getFullYear()
})

// Emits
const emit = defineEmits<{
  save: [data: SelfEvaluationFormData]
  preview: [data: SelfEvaluationFormData]
  submit: [evaluationId: string]
  aiScoringTriggered: [evaluationId: string]
}>()

// Router
const router = useRouter()

// Form reference
const formRef = ref<FormInstance>()

// Form data
const formData = reactive<SelfEvaluationFormData>({
  teachingOfficeId: props.teachingOfficeId,
  evaluationYear: props.evaluationYear,
  content: {
    teachingProcessManagement: '',
    courseConstruction: '',
    teachingReformProjects: 0,
    honoraryAwards: 0,
    teachingQuality: '',
    studentGuidance: '',
    scientificResearch: '',
    teamBuilding: ''
  }
})

// Initialize with initial data if provided
if (props.initialData) {
  Object.assign(formData, props.initialData)
}

// State
const saving = ref(false)
const previewVisible = ref(false)
const isSubmitted = ref(false)
const hasAttachments = ref(false)
const aiScoringLoading = ref(false)
const evaluationStatus = ref<string>('draft')

// Computed: Show AI scoring button only when form and attachments are both submitted
const showAIScoringButton = computed(() => {
  return props.evaluationId && 
         evaluationStatus.value === 'locked' && 
         hasAttachments.value
})

// Load evaluation status on mount
onMounted(async () => {
  if (props.evaluationId) {
    await checkEvaluationStatus()
  }
})

// Watch evaluationId changes
watch(() => props.evaluationId, async (newId) => {
  if (newId) {
    await checkEvaluationStatus()
  }
})

// Check evaluation status
const checkEvaluationStatus = async () => {
  if (!props.evaluationId) return
  
  try {
    const response = await selfEvaluationApi.getStatus(props.evaluationId)
    const evaluation = response.data
    
    evaluationStatus.value = evaluation.status
    isSubmitted.value = evaluation.status === 'locked' || evaluation.status === 'submitted'
    
    // Check if has attachments (this would need to be implemented in the API)
    // For now, assume if status is locked, attachments exist
    hasAttachments.value = evaluation.status === 'locked'
  } catch (error) {
    console.error('Failed to check evaluation status:', error)
  }
}

// Validation rules with real-time validation
const rules = reactive<FormRules>({
  'content.teachingProcessManagement': [
    { required: true, message: '请填写教学过程管理内容', trigger: ['blur', 'change'] },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim().length === 0) {
          callback(new Error('内容不能只包含空格'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ],
  'content.courseConstruction': [
    { required: true, message: '请填写课程建设内容', trigger: ['blur', 'change'] },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim().length === 0) {
          callback(new Error('内容不能只包含空格'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ],
  'content.teachingReformProjects': [
    { required: true, message: '请填写教学改革项目个数', trigger: ['blur', 'change'] },
    { type: 'number', message: '必须是数字', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value === null || value === undefined) {
          callback(new Error('请填写教学改革项目个数'))
        } else if (!Number.isInteger(value)) {
          callback(new Error('必须是整数'))
        } else if (value < 0) {
          callback(new Error('个数不能为负数'))
        } else if (value > 100) {
          callback(new Error('个数不能超过100'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ],
  'content.honoraryAwards': [
    { required: true, message: '请填写荣誉表彰个数', trigger: ['blur', 'change'] },
    { type: 'number', message: '必须是数字', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value === null || value === undefined) {
          callback(new Error('请填写荣誉表彰个数'))
        } else if (!Number.isInteger(value)) {
          callback(new Error('必须是整数'))
        } else if (value < 0) {
          callback(new Error('个数不能为负数'))
        } else if (value > 100) {
          callback(new Error('个数不能超过100'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ],
  'content.teachingQuality': [
    { required: true, message: '请填写教学质量内容', trigger: ['blur', 'change'] },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim().length === 0) {
          callback(new Error('内容不能只包含空格'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ],
  'content.studentGuidance': [
    { required: true, message: '请填写学生指导内容', trigger: ['blur', 'change'] },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim().length === 0) {
          callback(new Error('内容不能只包含空格'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ],
  'content.scientificResearch': [
    { required: true, message: '请填写科研工作内容', trigger: ['blur', 'change'] },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim().length === 0) {
          callback(new Error('内容不能只包含空格'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ],
  'content.teamBuilding': [
    { required: true, message: '请填写团队建设内容', trigger: ['blur', 'change'] },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value && value.trim().length === 0) {
          callback(new Error('内容不能只包含空格'))
        } else {
          callback()
        }
      }, 
      trigger: ['blur', 'change'] 
    }
  ]
})

// Handle save
const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true
    
    // Emit save event
    emit('save', { ...formData })
    
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('请检查表单填写是否完整')
  } finally {
    saving.value = false
  }
}

// Handle submit
const handleSubmit = async () => {
  if (!formRef.value) return
  
  if (!props.evaluationId) {
    ElMessage.warning('请先保存表单后再提交')
    return
  }

  try {
    await formRef.value.validate()
    
    // Confirm submission
    await ElMessageBox.confirm(
      '提交后表单和附件将被锁定，无法修改。确定要提交吗？',
      '确认提交',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    // Call API to submit
    const response = await selfEvaluationApi.submit(props.evaluationId)
    
    isSubmitted.value = true
    evaluationStatus.value = 'locked'
    
    ElMessage.success(response.data.message || '提交成功，表单已锁定')
    emit('submit', props.evaluationId)
    
    // Refresh status
    await checkEvaluationStatus()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Submit failed:', error)
      ElMessage.error(error.response?.data?.detail || '提交失败，请重试')
    }
  }
}

// Handle trigger AI scoring
const handleTriggerAIScoring = async () => {
  if (!props.evaluationId) {
    ElMessage.warning('无法触发AI评分：缺少评估ID')
    return
  }

  try {
    // Confirm trigger
    await ElMessageBox.confirm(
      '确定要触发AI评分吗？AI将自动解析自评表和附件进行评分。',
      '确认触发AI评分',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    
    aiScoringLoading.value = true
    
    // Call API to trigger AI scoring
    const response = await selfEvaluationApi.triggerAIScoring(props.evaluationId)
    
    ElMessage.success({
      message: response.data.message || 'AI评分任务已启动，正在后台处理中...',
      duration: 5000,
      showClose: true
    })
    
    emit('aiScoringTriggered', props.evaluationId)
    
    // Optionally refresh status after a delay
    setTimeout(async () => {
      await checkEvaluationStatus()
    }, 2000)
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Trigger AI scoring failed:', error)
      
      const errorMessage = error.response?.data?.detail || 'AI评分触发失败，请重试'
      
      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    aiScoringLoading.value = false
  }
}

// Handle preview
const handlePreview = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    previewVisible.value = true
    emit('preview', { ...formData })
  } catch (error) {
    ElMessage.warning('请先完整填写表单后再预览')
  }
}

// Handle reset
const handleReset = () => {
  if (!formRef.value) return
  formRef.value.resetFields()
  ElMessage.info('表单已重置')
}

// Handle attachments
const handleAttachments = () => {
  if (!props.evaluationId) {
    ElMessage.warning('请先保存表单后再上传附件')
    return
  }
  
  // Navigate to attachment upload page
  router.push({
    name: 'attachment-upload',
    params: { id: props.evaluationId }
  })
}

// Expose methods for parent component
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  getFormData: () => ({ ...formData })
})
</script>

<style scoped>
.self-evaluation-form {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.form-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.evaluation-year {
  font-size: 14px;
  color: #909399;
}

.evaluation-form {
  padding: 20px 0;
}

.number-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.input-hint {
  color: #606266;
  font-size: 14px;
}

.field-description {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.form-actions :deep(.el-form-item__content) {
  justify-content: center;
}

/* Preview styles */
.preview-content {
  padding: 20px;
}

.preview-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e4e7ed;
}

.preview-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.preview-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-item {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.preview-item label {
  display: block;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8px;
  font-size: 14px;
}

.preview-item p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
