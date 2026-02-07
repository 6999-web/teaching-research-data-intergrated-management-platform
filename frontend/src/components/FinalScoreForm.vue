<template>
  <div class="final-score-form">
    <el-card class="final-score-card">
      <template #header>
        <div class="card-header">
          <h2>确定最终得分</h2>
          <el-tag
            v-if="hasFinalScore"
            type="danger"
          >
            已确定
          </el-tag>
        </div>
      </template>

      <!-- All Scores Summary Section -->
      <div class="scores-summary-section">
        <h3 class="section-title">
          所有评审人打分汇总
        </h3>

        <!-- Loading State -->
        <div
          v-if="loading"
          class="loading-container"
        >
          <el-icon class="is-loading">
            <Loading />
          </el-icon>
          <span>加载评分数据中...</span>
        </div>

        <!-- Scores Display -->
        <div
          v-else-if="allScoresData"
          class="scores-display"
        >
          <!-- AI Score -->
          <el-card
            v-if="allScoresData.ai_score"
            class="score-summary-card ai-score"
          >
            <div class="score-summary-header">
              <div class="score-info">
                <span class="score-label">AI自动评分</span>
                <el-tag
                  type="success"
                  size="small"
                >
                  AI
                </el-tag>
              </div>
              <div class="score-value">
                {{ allScoresData.ai_score.total_score.toFixed(1) }}分
              </div>
            </div>
            <div class="score-time">
              评分时间: {{ formatDateTime(allScoresData.ai_score.scored_at) }}
            </div>
          </el-card>

          <!-- Manual Scores -->
          <el-card
            v-for="manualScore in sortedManualScores"
            :key="manualScore.id"
            class="score-summary-card manual-score"
            :class="{ 'evaluation-team': manualScore.reviewer_role === 'evaluation_team' }"
          >
            <div class="score-summary-header">
              <div class="score-info">
                <span class="score-label">{{ manualScore.reviewer_name }}</span>
                <el-tag
                  :type="manualScore.reviewer_role === 'evaluation_team' ? 'danger' : 'warning'"
                  size="small"
                >
                  {{ getRoleLabel(manualScore.reviewer_role) }}
                </el-tag>
                <el-tag
                  type="info"
                  size="small"
                >
                  权重: {{ (manualScore.weight * 100).toFixed(0) }}%
                </el-tag>
              </div>
              <div class="score-value">
                {{ calculateManualTotalScore(manualScore.scores) }}分
              </div>
            </div>
            <div class="score-time">
              提交时间: {{ formatDateTime(manualScore.submitted_at) }}
            </div>
          </el-card>

          <!-- Empty State -->
          <el-empty
            v-if="!allScoresData.ai_score && allScoresData.manual_scores.length === 0"
            description="暂无评分记录"
          />
        </div>
      </div>

      <el-divider />

      <!-- Final Score Calculation Section -->
      <div class="final-score-section">
        <h3 class="section-title">
          最终得分计算
        </h3>

        <!-- Calculated Score Display -->
        <div
          v-if="calculatedScore !== null"
          class="calculated-score-display"
        >
          <el-alert
            title="综合计算得分"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <div class="calculation-info">
                <p>根据所有评审人打分和权重计算得出的综合得分：</p>
                <div class="calculated-value">
                  {{ calculatedScore.toFixed(1) }}分
                </div>
                <p class="calculation-note">
                  注：考评小组权重为70%，考评办公室权重为50%
                </p>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- Final Score Form -->
        <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-width="120px"
          label-position="left"
          class="final-score-form-content"
          :disabled="hasFinalScore"
        >
          <el-form-item
            label="最终得分"
            prop="finalScore"
          >
            <el-input-number
              v-model="formData.finalScore"
              :min="0"
              :max="100"
              :step="0.1"
              :precision="1"
              placeholder="请输入最终得分"
              class="final-score-input"
            />
            <span class="score-unit">分</span>
            <el-button
              v-if="calculatedScore !== null && !hasFinalScore"
              type="text"
              class="use-calculated-btn"
              @click="useCalculatedScore"
            >
              使用计算得分
            </el-button>
          </el-form-item>

          <el-form-item
            label="汇总说明"
            prop="summary"
          >
            <el-input
              v-model="formData.summary"
              type="textarea"
              :rows="6"
              placeholder="请填写最终得分的汇总说明，包括综合评审意见、得分依据等"
              maxlength="1000"
              show-word-limit
            />
          </el-form-item>

          <!-- Action Buttons -->
          <el-form-item class="form-actions">
            <el-button
              type="primary"
              :loading="submitting"
              :disabled="hasFinalScore"
              size="large"
              @click="handleSubmit"
            >
              {{ hasFinalScore ? '已确定最终得分' : '确定最终得分' }}
            </el-button>
            <el-button
              :disabled="hasFinalScore"
              size="large"
              @click="handleReset"
            >
              重置
            </el-button>
            <el-button
              type="info"
              size="large"
              @click="handleViewDetails"
            >
              查看详细评分
            </el-button>
          </el-form-item>
        </el-form>

        <!-- Final Score Display (if already determined) -->
        <div
          v-if="hasFinalScore && allScoresData?.final_score"
          class="final-score-display"
        >
          <el-alert
            title="最终得分已确定"
            type="success"
            :closable="false"
            show-icon
          >
            <template #default>
              <div class="final-score-info">
                <div class="final-score-value">
                  <span class="label">最终得分：</span>
                  <span class="value">{{ allScoresData.final_score.final_score.toFixed(1) }}分</span>
                </div>
                <div class="final-score-time">
                  确定时间：{{ formatDateTime(allScoresData.final_score.determined_at) }}
                </div>
                <div
                  v-if="allScoresData.final_score.summary"
                  class="final-score-summary"
                >
                  <div class="summary-label">
                    汇总说明：
                  </div>
                  <div class="summary-content">
                    {{ allScoresData.final_score.summary }}
                  </div>
                </div>
              </div>
            </template>
          </el-alert>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { scoringApi } from '@/api/client'
import type { AllScoresResponse, IndicatorScore } from '@/types/scoring'

// Props
interface Props {
  evaluationId: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  submitted: [finalScoreId: string]
  viewDetails: []
}>()

// Form reference
const formRef = ref<FormInstance>()

// State
const loading = ref(false)
const submitting = ref(false)
const allScoresData = ref<AllScoresResponse | null>(null)

// Form data
const formData = reactive({
  finalScore: 0,
  summary: ''
})

// Validation rules
const rules = reactive<FormRules>({
  finalScore: [
    { required: true, message: '请输入最终得分', trigger: 'blur' },
    { type: 'number', message: '得分必须是数字', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value < 0) {
          callback(new Error('得分不能为负数'))
        } else if (value > 100) {
          callback(new Error('得分不能超过100分'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  summary: [
    { required: true, message: '请填写汇总说明', trigger: 'blur' },
    { min: 10, max: 1000, message: '汇总说明长度应在10-1000个字符之间', trigger: 'blur' }
  ]
})

// Computed: Has final score
const hasFinalScore = computed(() => {
  return allScoresData.value?.final_score !== undefined && allScoresData.value?.final_score !== null
})

// Computed: Sorted manual scores (evaluation_team first)
const sortedManualScores = computed(() => {
  if (!allScoresData.value) return []
  
  return [...allScoresData.value.manual_scores].sort((a, b) => {
    // Sort by role first (evaluation_team first), then by submitted time
    if (a.reviewer_role === 'evaluation_team' && b.reviewer_role !== 'evaluation_team') {
      return -1
    }
    if (a.reviewer_role !== 'evaluation_team' && b.reviewer_role === 'evaluation_team') {
      return 1
    }
    return new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
  })
})

// Computed: Calculated score based on all reviewer scores
const calculatedScore = computed(() => {
  if (!allScoresData.value || allScoresData.value.manual_scores.length === 0) {
    return null
  }

  // Calculate weighted average of manual scores
  let totalWeightedScore = 0
  let totalWeight = 0

  allScoresData.value.manual_scores.forEach(manualScore => {
    const score = calculateManualTotalScore(manualScore.scores)
    totalWeightedScore += score * manualScore.weight
    totalWeight += manualScore.weight
  })

  if (totalWeight === 0) return null

  return totalWeightedScore / totalWeight
})

// Get role label
function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    'evaluation_team': '考评小组',
    'evaluation_office': '考评办公室'
  }
  return labels[role] || role
}

// Calculate manual total score
function calculateManualTotalScore(scores: IndicatorScore[]): number {
  return scores.reduce((sum, score) => sum + score.score, 0)
}

// Format date time
function formatDateTime(dateStr: string): string {
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

// Use calculated score
function useCalculatedScore() {
  if (calculatedScore.value !== null) {
    formData.finalScore = Math.round(calculatedScore.value * 10) / 10
    ElMessage.success('已使用计算得分')
  }
}

// Load all scores
const loadAllScores = async () => {
  loading.value = true

  try {
    const response = await scoringApi.getAllScores(props.evaluationId)
    allScoresData.value = response.data

    // If final score exists, populate form
    if (allScoresData.value.final_score) {
      formData.finalScore = allScoresData.value.final_score.final_score
      formData.summary = allScoresData.value.final_score.summary || ''
    } else if (calculatedScore.value !== null) {
      // Pre-fill with calculated score
      formData.finalScore = Math.round(calculatedScore.value * 10) / 10
    }

  } catch (error: any) {
    console.error('Failed to load all scores:', error)

    const errorMessage = error.response?.data?.detail || '加载评分数据失败'

    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  } finally {
    loading.value = false
  }
}

// Handle submit
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // Confirm submission
    await ElMessageBox.confirm(
      '最终得分确定后将无法修改，请确认得分和汇总说明准确无误。确定要提交吗？',
      '确认提交最终得分',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    submitting.value = true

    // Submit to API
    const response = await scoringApi.submitFinalScore({
      evaluation_id: props.evaluationId,
      final_score: formData.finalScore,
      summary: formData.summary
    })

    ElMessage.success({
      message: '最终得分已确定！',
      duration: 5000,
      showClose: true
    })

    // Reload data
    await loadAllScores()

    emit('submitted', response.data.final_score_id)

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Submit final score failed:', error)

      const errorMessage = error.response?.data?.detail || '提交最终得分失败，请重试'

      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    submitting.value = false
  }
}

// Handle reset
const handleReset = () => {
  if (!formRef.value) return

  ElMessageBox.confirm(
    '确定要重置表单吗？所有填写的内容将被清空。',
    '确认重置',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    formRef.value?.resetFields()
    
    // Reset to calculated score if available
    if (calculatedScore.value !== null) {
      formData.finalScore = Math.round(calculatedScore.value * 10) / 10
    } else {
      formData.finalScore = 0
    }
    formData.summary = ''
    
    ElMessage.info('表单已重置')
  }).catch(() => {
    // User cancelled
  })
}

// Handle view details
const handleViewDetails = () => {
  emit('viewDetails')
}

// Load data on mount
onMounted(async () => {
  await loadAllScores()
})

// Expose methods
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  getFormData: () => ({ ...formData }),
  reload: loadAllScores
})
</script>

<style scoped>
.final-score-form {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.final-score-card {
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

.section-title {
  margin: 20px 0 15px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

/* Scores Summary Section */
.scores-summary-section {
  padding: 20px 0;
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

.scores-display {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.score-summary-card {
  border-radius: 8px;
  transition: all 0.3s;
}

.score-summary-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.15);
}

.score-summary-card.ai-score {
  border-left: 4px solid #67c23a;
}

.score-summary-card.manual-score {
  border-left: 4px solid #e6a23c;
}

.score-summary-card.evaluation-team {
  border-left: 4px solid #f56c6c;
  background-color: #fef0f0;
}

.score-summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.score-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.score-label {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.score-value {
  font-size: 24px;
  font-weight: bold;
  color: #f56c6c;
}

.score-time {
  font-size: 13px;
  color: #909399;
  margin-top: 5px;
}

/* Final Score Section */
.final-score-section {
  padding: 20px 0;
}

.calculated-score-display {
  margin: 20px 0;
}

.calculation-info {
  padding: 10px 0;
}

.calculation-info p {
  margin: 5px 0;
  color: #606266;
}

.calculated-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin: 15px 0;
  text-align: center;
}

.calculation-note {
  font-size: 13px;
  color: #909399;
  font-style: italic;
}

.final-score-form-content {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.final-score-input {
  width: 200px;
}

.score-unit {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}

.use-calculated-btn {
  margin-left: 15px;
  color: #409eff;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.form-actions :deep(.el-form-item__content) {
  justify-content: center;
}

/* Final Score Display */
.final-score-display {
  margin-top: 30px;
}

.final-score-info {
  padding: 10px 0;
}

.final-score-value {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 15px 0;
}

.final-score-value .label {
  font-size: 18px;
  font-weight: 600;
  color: #606266;
  margin-right: 10px;
}

.final-score-value .value {
  font-size: 36px;
  font-weight: bold;
  color: #67c23a;
}

.final-score-time {
  text-align: center;
  font-size: 14px;
  color: #909399;
  margin: 10px 0;
}

.final-score-summary {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.summary-label {
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.summary-content {
  color: #303133;
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>
