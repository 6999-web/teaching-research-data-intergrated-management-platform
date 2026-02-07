<template>
  <div class="attachment-upload">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <h2>附件上传</h2>
          <el-tag type="info">
            {{ evaluationYear }}年度
          </el-tag>
        </div>
      </template>

      <!-- 考核指标说明表格 -->
      <div class="indicator-table-section">
        <h3>考核指标对应表</h3>
        <el-table
          :data="indicators"
          border
          stripe
          class="indicator-table"
        >
          <el-table-column
            prop="label"
            label="考核指标"
            width="150"
          />
          <el-table-column
            prop="description"
            label="说明"
          />
          <el-table-column
            prop="category"
            label="类型"
            width="100"
          >
            <template #default="{ row }">
              <el-tag
                :type="row.category === 'certificate' ? 'success' : 'primary'"
                size="small"
              >
                {{ row.category === 'certificate' ? '证书类' : '项目类' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            label="支持格式"
            width="200"
          >
            <template #default="{ row }">
              <span class="file-types">{{ row.fileTypes.join(', ') }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 上传区域 -->
      <div class="upload-section">
        <h3>上传附件</h3>
        
        <!-- 选择考核指标 -->
        <el-form
          :model="uploadForm"
          label-width="120px"
          class="upload-form"
        >
          <el-form-item
            label="选择考核指标"
            required
          >
            <el-select
              v-model="uploadForm.indicator"
              placeholder="请选择考核指标"
              style="width: 100%"
              @change="handleIndicatorChange"
            >
              <el-option
                v-for="indicator in indicators"
                :key="indicator.key"
                :label="indicator.label"
                :value="indicator.key"
              >
                <span>{{ indicator.label }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">
                  {{ indicator.category === 'certificate' ? '证书类' : '项目类' }}
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <!-- 文件上传组件 -->
          <el-form-item
            label="上传文件"
            required
          >
            <el-upload
              ref="uploadRef"
              :action="uploadAction"
              :headers="uploadHeaders"
              :data="uploadData"
              :multiple="true"
              :file-list="fileList"
              :on-preview="handlePreview"
              :on-remove="handleRemove"
              :on-success="handleSuccess"
              :on-error="handleError"
              :on-progress="handleProgress"
              :before-upload="beforeUpload"
              :disabled="!uploadForm.indicator"
              :accept="acceptedFileTypes"
              :limit="10"
              :on-exceed="handleExceed"
              drag
              class="upload-component"
            >
              <el-icon class="el-icon--upload">
                <upload-filled />
              </el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  <p v-if="uploadForm.indicator">
                    支持格式：{{ currentIndicatorFileTypes }}
                  </p>
                  <p
                    v-else
                    class="warning-text"
                  >
                    请先选择考核指标
                  </p>
                  <p>支持多文件上传，单个文件不超过50MB，最多上传10个文件</p>
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <!-- 上传进度显示 -->
          <el-form-item
            v-if="uploadingFiles.length > 0"
            label="上传进度"
          >
            <div class="progress-list">
              <div
                v-for="file in uploadingFiles"
                :key="file.fileName"
                class="progress-item"
              >
                <div class="progress-info">
                  <span class="file-name">{{ file.fileName }}</span>
                  <span class="progress-percentage">{{ file.percentage }}%</span>
                </div>
                <el-progress
                  :percentage="file.percentage"
                  :status="file.status === 'error' ? 'exception' : file.status === 'success' ? 'success' : undefined"
                />
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 已上传文件列表 -->
      <div
        v-if="uploadedAttachments.length > 0"
        class="uploaded-section"
      >
        <h3>已上传附件</h3>
        <el-table
          :data="uploadedAttachments"
          border
          stripe
        >
          <el-table-column
            prop="indicator"
            label="考核指标"
            width="150"
          >
            <template #default="{ row }">
              {{ getIndicatorLabel(row.indicator) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="fileName"
            label="文件名"
          />
          <el-table-column
            prop="fileSize"
            label="文件大小"
            width="120"
          >
            <template #default="{ row }">
              {{ formatFileSize(row.fileSize) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="uploadedAt"
            label="上传时间"
            width="180"
          >
            <template #default="{ row }">
              {{ formatDate(row.uploadedAt) }}
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="100"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                link
                :disabled="isLocked"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleBack">
          返回
        </el-button>
        <el-button
          type="primary"
          :disabled="uploadedAttachments.length === 0 || isLocked"
          @click="handleSubmit"
        >
          提交附件
        </el-button>
      </div>
    </el-card>

    <!-- 锁定提示 -->
    <el-alert
      v-if="isLocked"
      title="附件已锁定"
      type="warning"
      description="表单和附件已提交并锁定，如需修改请联系管理员打回"
      :closable="false"
      show-icon
      class="lock-alert"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox, type UploadInstance, type UploadProps, type UploadUserFile } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import type { Attachment, UploadProgress, IndicatorType } from '@/types/attachment'
import { INDICATORS } from '@/types/attachment'
import apiClient from '@/api/client'

// Props
interface Props {
  evaluationId: string
  evaluationYear?: number
  isLocked?: boolean
  initialAttachments?: Attachment[]
}

const props = withDefaults(defineProps<Props>(), {
  evaluationYear: () => new Date().getFullYear(),
  isLocked: false,
  initialAttachments: () => []
})

// Emits
const emit = defineEmits<{
  submit: []
  back: []
}>()

// Upload reference
const uploadRef = ref<UploadInstance>()

// Form data
const uploadForm = reactive({
  indicator: '' as IndicatorType | ''
})

// State
const fileList = ref<UploadUserFile[]>([])
const uploadingFiles = ref<UploadProgress[]>([])
const uploadedAttachments = ref<Attachment[]>([...props.initialAttachments])

// Indicators
const indicators = INDICATORS

// Computed
const uploadAction = computed(() => {
  return `/api/teaching-office/attachments`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    Authorization: token ? `Bearer ${token}` : ''
  }
})

const uploadData = computed(() => {
  return {
    evaluationId: props.evaluationId,
    indicator: uploadForm.indicator
  }
})

const currentIndicatorFileTypes = computed(() => {
  if (!uploadForm.indicator) return ''
  const indicator = indicators.find(i => i.key === uploadForm.indicator)
  return indicator ? indicator.fileTypes.join(', ') : ''
})

const acceptedFileTypes = computed(() => {
  if (!uploadForm.indicator) return ''
  const indicator = indicators.find(i => i.key === uploadForm.indicator)
  if (!indicator) return ''
  return indicator.fileTypes.map(type => `.${type}`).join(',')
})

// Methods
const handleIndicatorChange = () => {
  // Clear file list when indicator changes
  fileList.value = []
  uploadRef.value?.clearFiles()
}

const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  if (!uploadForm.indicator) {
    ElMessage.error('请先选择考核指标')
    return false
  }

  // Check file size (50MB)
  const maxSize = 50 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件 ${file.name} 大小超过50MB限制`)
    return false
  }

  // Check file type
  const indicator = indicators.find(i => i.key === uploadForm.indicator)
  if (indicator) {
    const fileExt = file.name.split('.').pop()?.toLowerCase()
    if (fileExt && !indicator.fileTypes.includes(fileExt)) {
      ElMessage.error(`文件 ${file.name} 格式不支持，请上传 ${indicator.fileTypes.join(', ')} 格式的文件`)
      return false
    }
  }

  // Add to uploading list
  uploadingFiles.value.push({
    fileName: file.name,
    percentage: 0,
    status: 'uploading'
  })

  return true
}

const handleProgress: UploadProps['onProgress'] = (event, file) => {
  const uploadingFile = uploadingFiles.value.find(f => f.fileName === file.name)
  if (uploadingFile) {
    uploadingFile.percentage = Math.floor(event.percent || 0)
  }
}

const handleSuccess: UploadProps['onSuccess'] = (response, file) => {
  const uploadingFile = uploadingFiles.value.find(f => f.fileName === file.name)
  if (uploadingFile) {
    uploadingFile.percentage = 100
    uploadingFile.status = 'success'
  }

  // Add to uploaded attachments
  if (response.attachmentIds && response.attachmentIds.length > 0) {
    // Fetch the uploaded attachment details
    fetchAttachmentDetails(response.attachmentIds[0])
  }

  ElMessage.success(`文件 ${file.name} 上传成功`)

  // Remove from uploading list after a delay
  setTimeout(() => {
    const index = uploadingFiles.value.findIndex(f => f.fileName === file.name)
    if (index > -1) {
      uploadingFiles.value.splice(index, 1)
    }
  }, 2000)
}

const handleError: UploadProps['onError'] = (error, file) => {
  const uploadingFile = uploadingFiles.value.find(f => f.fileName === file.name)
  if (uploadingFile) {
    uploadingFile.status = 'error'
  }

  ElMessage.error(`文件 ${file.name} 上传失败`)

  // Remove from uploading list after a delay
  setTimeout(() => {
    const index = uploadingFiles.value.findIndex(f => f.fileName === file.name)
    if (index > -1) {
      uploadingFiles.value.splice(index, 1)
    }
  }, 2000)
}

const handleRemove: UploadProps['onRemove'] = (file) => {
  ElMessage.info(`已移除文件 ${file.name}`)
}

const handlePreview: UploadProps['onPreview'] = (file) => {
  ElMessage.info(`预览文件 ${file.name}`)
}

const handleExceed: UploadProps['onExceed'] = (files) => {
  ElMessage.warning(`最多只能上传10个文件，当前选择了 ${files.length} 个文件`)
}

const fetchAttachmentDetails = async (attachmentId: string) => {
  try {
    const response = await apiClient.get(`/attachments/${attachmentId}`)
    uploadedAttachments.value.push(response.data)
  } catch (error) {
    console.error('Failed to fetch attachment details:', error)
  }
}

const handleDelete = async (attachment: Attachment) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 ${attachment.fileName} 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Call API to delete attachment
    await apiClient.delete(`/attachments/${attachment.id}`)

    // Remove from list
    const index = uploadedAttachments.value.findIndex(a => a.id === attachment.id)
    if (index > -1) {
      uploadedAttachments.value.splice(index, 1)
    }

    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = () => {
  if (uploadedAttachments.value.length === 0) {
    ElMessage.warning('请先上传附件')
    return
  }

  ElMessageBox.confirm(
    '确定要提交附件吗？提交后将无法修改',
    '确认提交',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('submit')
    ElMessage.success('附件提交成功')
  }).catch(() => {
    // User cancelled
  })
}

const handleBack = () => {
  emit('back')
}

const getIndicatorLabel = (key: string): string => {
  const indicator = indicators.find(i => i.key === key)
  return indicator ? indicator.label : key
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Expose methods
defineExpose({
  getUploadedAttachments: () => uploadedAttachments.value
})
</script>

<style scoped>
.attachment-upload {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.upload-card {
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

.indicator-table-section {
  margin-bottom: 30px;
}

.indicator-table-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.indicator-table {
  width: 100%;
}

.file-types {
  font-size: 12px;
  color: #606266;
}

.upload-section {
  margin-bottom: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.upload-section h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #303133;
}

.upload-form {
  max-width: 800px;
}

.upload-component {
  width: 100%;
}

.upload-component :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px;
}

.el-upload__tip {
  margin-top: 10px;
  line-height: 1.6;
}

.el-upload__tip p {
  margin: 5px 0;
  font-size: 13px;
  color: #606266;
}

.warning-text {
  color: #e6a23c;
  font-weight: 500;
}

.progress-list {
  width: 100%;
}

.progress-item {
  margin-bottom: 15px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.file-name {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 10px;
}

.progress-percentage {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.uploaded-section {
  margin-bottom: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.uploaded-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.lock-alert {
  margin-top: 20px;
}
</style>
