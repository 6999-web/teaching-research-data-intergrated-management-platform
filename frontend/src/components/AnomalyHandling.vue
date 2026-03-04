<template>
  <div class="anomaly-handling">
    <el-card class="anomaly-card">
      <template #header>
        <div class="card-header">
          <h2>异常数据处理</h2>
          <div class="header-actions">
            <el-select
              v-model="statusFilter"
              placeholder="筛选状态"
              clearable
              style="width: 150px; margin-right: 10px"
              @change="loadAnomalies"
            >
              <el-option
                label="待处理"
                value="pending"
              />
              <el-option
                label="已处理"
                value="handled"
              />
            </el-select>
            <el-button
              type="primary"
              :icon="Refresh"
              :loading="loading"
              @click="loadAnomalies"
            >
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- Loading State -->
      <div
        v-if="loading"
        class="loading-container"
      >
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
        <span>加载中...</span>
      </div>

      <!-- Anomaly List -->
      <div
        v-else-if="anomalies.length > 0"
        class="anomaly-list"
      >
        <el-card
          v-for="anomaly in anomalies"
          :key="anomaly.id"
          class="anomaly-item"
          :class="{ 'handled-item': anomaly.status === 'handled' }"
          shadow="hover"
        >
          <div class="anomaly-header">
            <div class="anomaly-title">
              <el-tag
                :type="getAnomalyTypeTagType(anomaly.type)"
                size="large"
              >
                {{ getAnomalyTypeLabel(anomaly.type) }}
              </el-tag>
              <span class="indicator-name">{{ anomaly.indicator }}</span>
              <el-tag
                :type="anomaly.status === 'pending' ? 'warning' : 'success'"
                size="small"
              >
                {{ getAnomalyStatusLabel(anomaly.status) }}
              </el-tag>
            </div>
            <div class="anomaly-id">
              <span class="label">异常ID:</span>
              <span class="value">{{ anomaly.id.substring(0, 8) }}...</span>
            </div>
          </div>

          <!-- Detailed Comparison -->
          <div class="anomaly-details">
            <div class="comparison-section">
              <h4>详细对比说明</h4>
              <div class="description-box">
                {{ anomaly.description }}
              </div>

              <!-- Count Comparison for count_mismatch type -->
              <div
                v-if="anomaly.type === 'count_mismatch' && anomaly.declared_count !== undefined && anomaly.parsed_count !== undefined"
                class="count-comparison"
              >
                <div class="count-item declared">
                  <div class="count-label">
                    自评表填写数量
                  </div>
                  <div class="count-value">
                    {{ anomaly.declared_count }}
                  </div>
                </div>
                <div class="count-divider">
                  <el-icon><Right /></el-icon>
                </div>
                <div class="count-item parsed">
                  <div class="count-label">
                    AI解析附件数量
                  </div>
                  <div class="count-value">
                    {{ anomaly.parsed_count }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Handled Information -->
            <div
              v-if="anomaly.status === 'handled'"
              class="handled-info"
            >
              <el-divider />
              <div class="handled-details">
                <div class="handled-item">
                  <span class="label">处理动作:</span>
                  <el-tag :type="anomaly.handled_action === 'reject' ? 'danger' : 'success'">
                    {{ getAnomalyActionLabel(anomaly.handled_action || '') }}
                  </el-tag>
                </div>
                <div class="handled-item">
                  <span class="label">处理时间:</span>
                  <span class="value">{{ formatDateTime(anomaly.handled_at || '') }}</span>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div
              v-if="anomaly.status === 'pending'"
              class="action-buttons"
            >
              <el-divider />
              <div class="button-group">
                <el-button
                  type="danger"
                  :icon="CloseBold"
                  :loading="processingAnomalyId === anomaly.id"
                  @click="handleReject(anomaly)"
                >
                  打回教研室补充材料
                </el-button>
                <el-button
                  type="success"
                  :icon="Check"
                  :loading="processingAnomalyId === anomaly.id"
                  @click="handleCorrect(anomaly)"
                >
                  直接修正异常数据
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Empty State -->
      <el-empty
        v-else
        description="暂无异常数据"
        :image-size="120"
      />
    </el-card>

    <!-- Reject Dialog -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="打回教研室补充材料"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="rejectFormRef"
        :model="rejectForm"
        :rules="rejectRules"
        label-width="120px"
      >
        <el-alert
          title="打回后，教研室端将解锁表单和附件，允许教研室修改和补充材料。"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <el-form-item
          label="异常类型"
          prop="type"
        >
          <el-tag :type="getAnomalyTypeTagType(selectedAnomaly?.type || '')">
            {{ getAnomalyTypeLabel(selectedAnomaly?.type || '') }}
          </el-tag>
        </el-form-item>

        <el-form-item
          label="考核指标"
          prop="indicator"
        >
          <span>{{ selectedAnomaly?.indicator }}</span>
        </el-form-item>

        <el-form-item
          label="对比说明"
          prop="description"
        >
          <div class="description-display">
            {{ selectedAnomaly?.description }}
          </div>
        </el-form-item>

        <el-form-item
          label="打回原因"
          prop="reject_reason"
        >
          <el-input
            v-model="rejectForm.reject_reason"
            type="textarea"
            :rows="4"
            placeholder="请填写打回原因，说明需要教研室补充或修正的内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="rejectDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="danger"
          :loading="submitting"
          @click="confirmReject"
        >
          确认打回
        </el-button>
      </template>
    </el-dialog>

    <!-- Correct Dialog -->
    <el-dialog
      v-model="correctDialogVisible"
      title="直接修正异常数据"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="correctFormRef"
        :model="correctForm"
        :rules="correctRules"
        label-width="120px"
      >
        <el-alert
          title="直接修正后，异常数据将被更新，教研室端不会收到通知。"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        />

        <el-form-item
          label="异常类型"
          prop="type"
        >
          <el-tag :type="getAnomalyTypeTagType(selectedAnomaly?.type || '')">
            {{ getAnomalyTypeLabel(selectedAnomaly?.type || '') }}
          </el-tag>
        </el-form-item>

        <el-form-item
          label="考核指标"
          prop="indicator"
        >
          <span>{{ selectedAnomaly?.indicator }}</span>
        </el-form-item>

        <el-form-item
          label="对比说明"
          prop="description"
        >
          <div class="description-display">
            {{ selectedAnomaly?.description }}
          </div>
        </el-form-item>

        <!-- Corrected Data Input for count_mismatch -->
        <div v-if="selectedAnomaly?.type === 'count_mismatch'">
          <el-form-item
            label="修正后数量"
            prop="corrected_count"
          >
            <el-input-number
              v-model="correctForm.corrected_count"
              :min="0"
              :max="100"
              placeholder="请输入修正后的数量"
            />
            <div class="form-hint">
              原填写数量: {{ selectedAnomaly?.declared_count }}, 
              AI解析数量: {{ selectedAnomaly?.parsed_count }}
            </div>
          </el-form-item>
        </div>

        <el-form-item
          label="修正说明"
          prop="correction_note"
        >
          <el-input
            v-model="correctForm.correction_note"
            type="textarea"
            :rows="3"
            placeholder="请填写修正说明"
            maxlength="300"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="correctDialogVisible = false">
          取消
        </el-button>
        <el-button
          type="success"
          :loading="submitting"
          @click="confirmCorrect"
        >
          确认修正
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Loading, Refresh, CloseBold, Check, Right } from '@element-plus/icons-vue'
import { reviewApi } from '@/api/client'
import type {
  AnomalyDetail,
  HandleAnomalyRequest
} from '@/types/anomaly'
import {
  ANOMALY_TYPE_LABELS,
  ANOMALY_STATUS_LABELS,
  ANOMALY_ACTION_LABELS
} from '@/types/anomaly'

// Props
interface Props {
  evaluationId?: string
}

const props = defineProps<Props>()

// State
const loading = ref(false)
const anomalies = ref<AnomalyDetail[]>([])
const statusFilter = ref<string>('')
const processingAnomalyId = ref<string>('')

// Dialog state
const rejectDialogVisible = ref(false)
const correctDialogVisible = ref(false)
const submitting = ref(false)
const selectedAnomaly = ref<AnomalyDetail | null>(null)

// Form refs
const rejectFormRef = ref<FormInstance>()
const correctFormRef = ref<FormInstance>()

// Reject form
const rejectForm = reactive({
  reject_reason: ''
})

const rejectRules = reactive<FormRules>({
  reject_reason: [
    { required: true, message: '请填写打回原因', trigger: 'blur' },
    { min: 10, max: 500, message: '打回原因长度应在10-500个字符之间', trigger: 'blur' }
  ]
})

// Correct form
const correctForm = reactive({
  corrected_count: 0,
  correction_note: ''
})

const correctRules = reactive<FormRules>({
  corrected_count: [
    { required: true, message: '请输入修正后的数量', trigger: 'blur' },
    { type: 'number', message: '数量必须是数字', trigger: 'blur' }
  ],
  correction_note: [
    { required: true, message: '请填写修正说明', trigger: 'blur' },
    { min: 5, max: 300, message: '修正说明长度应在5-300个字符之间', trigger: 'blur' }
  ]
})

// Get anomaly type label
function getAnomalyTypeLabel(type: string): string {
  return ANOMALY_TYPE_LABELS[type] || type
}

// Get anomaly status label
function getAnomalyStatusLabel(status: string): string {
  return ANOMALY_STATUS_LABELS[status] || status
}

// Get anomaly action label
function getAnomalyActionLabel(action: string): string {
  return ANOMALY_ACTION_LABELS[action] || action
}

// Get anomaly type tag type
function getAnomalyTypeTagType(type: string): 'danger' | 'warning' | 'info' {
  const typeMap: Record<string, 'danger' | 'warning' | 'info'> = {
    'count_mismatch': 'danger',
    'missing_attachment': 'warning',
    'invalid_data': 'info'
  }
  return typeMap[type] || 'info'
}

// Format date time
function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Load anomalies
const loadAnomalies = async () => {
  loading.value = true

  try {
    const params: any = {}
    
    if (props.evaluationId) {
      params.evaluation_id = props.evaluationId
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const response = await reviewApi.getAnomalies(params)
    anomalies.value = response.data.anomalies

  } catch (error: any) {
    console.error('Failed to load anomalies:', error)

    const errorMessage = error.response?.data?.detail || '加载异常数据失败'

    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  } finally {
    loading.value = false
  }
}

// Handle reject
const handleReject = (anomaly: AnomalyDetail) => {
  selectedAnomaly.value = anomaly
  rejectForm.reject_reason = ''
  rejectDialogVisible.value = true
}

// Confirm reject
const confirmReject = async () => {
  if (!rejectFormRef.value || !selectedAnomaly.value) return

  try {
    await rejectFormRef.value.validate()

    await ElMessageBox.confirm(
      '确定要打回教研室补充材料吗？教研室端将解锁表单和附件。',
      '确认打回',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    submitting.value = true
    processingAnomalyId.value = selectedAnomaly.value.id

    const requestData: HandleAnomalyRequest = {
      anomaly_id: selectedAnomaly.value.id,
      action: 'reject',
      reject_reason: rejectForm.reject_reason
    }

    const response = await reviewApi.handleAnomaly(requestData)

    ElMessage.success({
      message: response.data.message || '异常数据已打回教研室',
      duration: 5000,
      showClose: true
    })

    rejectDialogVisible.value = false
    
    // Reload anomalies
    await loadAnomalies()

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to reject anomaly:', error)

      const errorMessage = error.response?.data?.detail || '打回操作失败，请重试'

      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    submitting.value = false
    processingAnomalyId.value = ''
  }
}

// Handle correct
const handleCorrect = (anomaly: AnomalyDetail) => {
  selectedAnomaly.value = anomaly
  
  // Initialize form with current values
  if (anomaly.type === 'count_mismatch') {
    correctForm.corrected_count = anomaly.parsed_count || 0
  }
  correctForm.correction_note = ''
  
  correctDialogVisible.value = true
}

// Confirm correct
const confirmCorrect = async () => {
  if (!correctFormRef.value || !selectedAnomaly.value) return

  try {
    await correctFormRef.value.validate()

    await ElMessageBox.confirm(
      '确定要直接修正异常数据吗？修正后教研室端不会收到通知。',
      '确认修正',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    submitting.value = true
    processingAnomalyId.value = selectedAnomaly.value.id

    // Build corrected data based on anomaly type
    const correctedData: Record<string, any> = {}
    
    if (selectedAnomaly.value.type === 'count_mismatch') {
      // Map indicator to field name
      const indicatorFieldMap: Record<string, string> = {
        '教学改革项目': 'teachingReformProjects',
        '荣誉表彰': 'honoraryAwards'
      }
      
      const fieldName = indicatorFieldMap[selectedAnomaly.value.indicator]
      if (fieldName) {
        correctedData[fieldName] = correctForm.corrected_count
      }
    }
    
    // Add correction note to corrected data
    correctedData['_correction_note'] = correctForm.correction_note

    const requestData: HandleAnomalyRequest = {
      anomaly_id: selectedAnomaly.value.id,
      action: 'correct',
      corrected_data: correctedData
    }

    const response = await reviewApi.handleAnomaly(requestData)

    ElMessage.success({
      message: response.data.message || '异常数据已修正',
      duration: 5000,
      showClose: true
    })

    correctDialogVisible.value = false
    
    // Reload anomalies
    await loadAnomalies()

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to correct anomaly:', error)

      const errorMessage = error.response?.data?.detail || '修正操作失败，请重试'

      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    submitting.value = false
    processingAnomalyId.value = ''
  }
}

// Load anomalies on mount
onMounted(() => {
  loadAnomalies()
})

// Expose methods
defineExpose({
  loadAnomalies
})
</script>

<style scoped>
.anomaly-handling {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.anomaly-card {
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

.header-actions {
  display: flex;
  align-items: center;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.anomaly-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.anomaly-item {
  border-left: 4px solid #f56c6c;
  transition: all 0.3s;
}

.anomaly-item.handled-item {
  border-left-color: #67c23a;
  opacity: 0.85;
}

.anomaly-item:hover {
  transform: translateY(-2px);
}

.anomaly-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.anomaly-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.indicator-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.anomaly-id {
  font-size: 13px;
  color: #909399;
}

.anomaly-id .label {
  margin-right: 5px;
}

.anomaly-id .value {
  font-family: monospace;
}

.anomaly-details {
  padding: 10px 0;
}

.comparison-section h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #606266;
  font-weight: 600;
}

.description-box {
  padding: 15px;
  background-color: #fef0f0;
  border-left: 3px solid #f56c6c;
  border-radius: 4px;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 15px;
}

.count-comparison {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.count-item {
  flex: 1;
  text-align: center;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.count-item.declared {
  border: 2px solid #409eff;
}

.count-item.parsed {
  border: 2px solid #f56c6c;
}

.count-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
}

.count-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.count-divider {
  font-size: 24px;
  color: #909399;
}

.handled-info {
  margin-top: 15px;
}

.handled-details {
  display: flex;
  gap: 30px;
  padding: 10px 0;
}

.handled-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.handled-item .label {
  font-weight: 600;
  color: #606266;
}

.handled-item .value {
  color: #303133;
}

.action-buttons {
  margin-top: 15px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.description-display {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.6;
  color: #606266;
  min-height: 60px;
}

.form-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}
</style>
