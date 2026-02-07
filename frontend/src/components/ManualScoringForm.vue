<template>
  <div class="manual-scoring-form">
    <el-card class="scoring-card">
      <template #header>
        <div class="card-header">
          <h2>手动评分</h2>
          <el-tag
            v-if="currentUserRole"
            :type="roleTagType"
          >
            {{ roleLabel }}
          </el-tag>
        </div>
      </template>

      <!-- Weight Information -->
      <el-alert
        v-if="currentUserRole"
        :title="weightInfo"
        type="info"
        :closable="false"
        show-icon
        class="weight-alert"
      />

      <!-- Scoring Form -->
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="150px"
        label-position="left"
        class="scoring-form"
      >
        <div
          v-for="indicator in indicators"
          :key="indicator.key"
          class="indicator-section"
        >
          <div class="indicator-header">
            <h3>{{ indicator.label }}</h3>
            <span class="max-score">满分: {{ indicator.maxScore }}分</span>
          </div>

          <el-form-item
            :label="`${indicator.label}得分`"
            :prop="`scores.${indicator.key}.score`"
          >
            <el-input-number
              v-model="formData.scores[indicator.key].score"
              :min="0"
              :max="indicator.maxScore"
              :step="0.5"
              :precision="1"
              placeholder="请输入得分"
              class="score-input"
            />
            <span class="score-hint">/ {{ indicator.maxScore }}分</span>
          </el-form-item>

          <el-form-item
            :label="`${indicator.label}评语`"
            :prop="`scores.${indicator.key}.comment`"
          >
            <el-input
              v-model="formData.scores[indicator.key].comment"
              type="textarea"
              :rows="3"
              placeholder="请填写评分说明和理由"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </div>

        <!-- Total Score Display -->
        <div class="total-score-section">
          <el-divider />
          <div class="total-score">
            <span class="label">总分：</span>
            <span class="value">{{ totalScore.toFixed(1) }}</span>
            <span class="max">/ {{ maxTotalScore }}分</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <el-form-item class="form-actions">
          <el-button
            type="primary"
            :loading="submitting"
            :disabled="hasSubmitted"
            @click="handleSubmit"
          >
            {{ hasSubmitted ? '已提交评分' : '提交评分' }}
          </el-button>
          <el-button
            :disabled="hasSubmitted"
            @click="handleReset"
          >
            重置
          </el-button>
          <el-button
            type="info"
            @click="handleViewAllScores"
          >
            查看所有评审人打分
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- All Scores Dialog -->
    <el-dialog
      v-model="allScoresVisible"
      title="所有评审人打分记录"
      width="90%"
      :close-on-click-modal="false"
      class="all-scores-dialog"
    >
      <div
        v-if="allScoresLoading"
        class="loading-container"
      >
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
        <span>加载中...</span>
      </div>

      <div
        v-else-if="allScoresData"
        class="all-scores-content"
      >
        <!-- AI Score Section -->
        <el-card
          v-if="allScoresData.ai_score"
          class="score-card ai-score-card"
        >
          <template #header>
            <div class="score-card-header">
              <h3>AI自动评分</h3>
              <el-tag type="success">
                AI评分
              </el-tag>
            </div>
          </template>
          <div class="score-details">
            <div class="score-item">
              <span class="label">总分：</span>
              <span class="value highlight">{{ allScoresData.ai_score.total_score.toFixed(1) }}分</span>
            </div>
            <div class="score-item">
              <span class="label">评分时间：</span>
              <span class="value">{{ formatDateTime(allScoresData.ai_score.scored_at) }}</span>
            </div>
            <div class="score-item">
              <span class="label">解析教学改革项目：</span>
              <span class="value">{{ allScoresData.ai_score.parsed_reform_projects }}个</span>
            </div>
            <div class="score-item">
              <span class="label">解析荣誉表彰：</span>
              <span class="value">{{ allScoresData.ai_score.parsed_honorary_awards }}个</span>
            </div>
          </div>
          <el-divider />
          <div class="indicator-scores">
            <h4>各指标得分：</h4>
            <div
              v-for="(indicatorScore, index) in allScoresData.ai_score.indicator_scores"
              :key="index"
              class="indicator-score-item"
            >
              <div class="indicator-name">
                {{ indicatorScore.indicator }}
              </div>
              <div class="indicator-score">
                {{ indicatorScore.score }}分
              </div>
              <div class="indicator-reasoning">
                {{ indicatorScore.reasoning }}
              </div>
            </div>
          </div>
        </el-card>

        <!-- Manual Scores Section -->
        <div
          v-if="allScoresData.manual_scores.length > 0"
          class="manual-scores-section"
        >
          <h3 class="section-title">
            评审人打分记录
          </h3>
          <el-card
            v-for="manualScore in sortedManualScores"
            :key="manualScore.id"
            class="score-card manual-score-card"
            :class="{ 'evaluation-team-card': manualScore.reviewer_role === 'evaluation_team' }"
          >
            <template #header>
              <div class="score-card-header">
                <div class="reviewer-info">
                  <h3>{{ manualScore.reviewer_name }}</h3>
                  <el-tag
                    :type="manualScore.reviewer_role === 'evaluation_team' ? 'danger' : 'warning'"
                    class="role-tag"
                  >
                    {{ getRoleLabel(manualScore.reviewer_role) }}
                  </el-tag>
                  <el-tag
                    type="info"
                    class="weight-tag"
                  >
                    权重: {{ (manualScore.weight * 100).toFixed(0) }}%
                  </el-tag>
                </div>
                <div class="submit-time">
                  {{ formatDateTime(manualScore.submitted_at) }}
                </div>
              </div>
            </template>
            <div class="manual-score-details">
              <div
                v-for="score in manualScore.scores"
                :key="score.indicator"
                class="indicator-score-item"
              >
                <div class="indicator-header-row">
                  <span class="indicator-name">{{ score.indicator }}</span>
                  <span class="indicator-score">{{ score.score }}分</span>
                </div>
                <div class="indicator-comment">
                  {{ score.comment }}
                </div>
              </div>
              <el-divider />
              <div class="total-score-row">
                <span class="label">总分：</span>
                <span class="value">{{ calculateManualTotalScore(manualScore.scores) }}分</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Final Score Section -->
        <el-card
          v-if="allScoresData.final_score"
          class="score-card final-score-card"
        >
          <template #header>
            <div class="score-card-header">
              <h3>最终得分</h3>
              <el-tag type="danger">
                最终确定
              </el-tag>
            </div>
          </template>
          <div class="score-details">
            <div class="score-item">
              <span class="label">最终得分：</span>
              <span class="value highlight large">{{ allScoresData.final_score.final_score.toFixed(1) }}分</span>
            </div>
            <div class="score-item">
              <span class="label">确定时间：</span>
              <span class="value">{{ formatDateTime(allScoresData.final_score.determined_at) }}</span>
            </div>
            <div
              v-if="allScoresData.final_score.summary"
              class="score-item full-width"
            >
              <span class="label">汇总说明：</span>
              <div class="summary-text">
                {{ allScoresData.final_score.summary }}
              </div>
            </div>
          </div>
        </el-card>

        <!-- Empty State -->
        <el-empty
          v-if="!allScoresData.ai_score && allScoresData.manual_scores.length === 0 && !allScoresData.final_score"
          description="暂无评分记录"
        />
      </div>

      <template #footer>
        <el-button @click="allScoresVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { scoringApi } from '@/api/client'
import {
  EVALUATION_INDICATORS,
  TOTAL_MAX_SCORE,
  type IndicatorScore,
  type ManualScoreCreate,
  type AllScoresResponse,
  type ManualScoreDetail
} from '@/types/scoring'

// Props
interface Props {
  evaluationId: string
  currentUserRole?: 'evaluation_team' | 'evaluation_office'
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  submitted: [scoreRecordId: string]
}>()

// Form reference
const formRef = ref<FormInstance>()

// State
const submitting = ref(false)
const hasSubmitted = ref(false)
const allScoresVisible = ref(false)
const allScoresLoading = ref(false)
const allScoresData = ref<AllScoresResponse | null>(null)

// Indicators
const indicators = EVALUATION_INDICATORS
const maxTotalScore = TOTAL_MAX_SCORE

// Form data - initialize scores for all indicators
const formData = reactive<{
  scores: Record<string, { score: number; comment: string }>
}>({
  scores: {}
})

// Initialize form data
indicators.forEach(indicator => {
  formData.scores[indicator.key] = {
    score: 0,
    comment: ''
  }
})

// Computed: Total score
const totalScore = computed(() => {
  return Object.values(formData.scores).reduce((sum, item) => sum + item.score, 0)
})

// Computed: Role label
const roleLabel = computed(() => {
  return getRoleLabel(props.currentUserRole || '')
})

// Computed: Role tag type
const roleTagType = computed(() => {
  return props.currentUserRole === 'evaluation_team' ? 'danger' : 'warning'
})

// Computed: Weight info
const weightInfo = computed(() => {
  const weight = props.currentUserRole === 'evaluation_team' ? 70 : 50
  return `您的评分权重为 ${weight}%。${props.currentUserRole === 'evaluation_team' ? '考评小组的评分权重高于考评办公室。' : ''}`
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

// Validation rules
const rules = reactive<FormRules>({})

// Generate validation rules for each indicator
indicators.forEach(indicator => {
  rules[`scores.${indicator.key}.score`] = [
    { required: true, message: `请输入${indicator.label}得分`, trigger: 'blur' },
    { type: 'number', message: '得分必须是数字', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value < 0) {
          callback(new Error('得分不能为负数'))
        } else if (value > indicator.maxScore) {
          callback(new Error(`得分不能超过${indicator.maxScore}分`))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
  
  rules[`scores.${indicator.key}.comment`] = [
    { required: true, message: `请填写${indicator.label}评语`, trigger: 'blur' },
    { min: 5, max: 500, message: '评语长度应在5-500个字符之间', trigger: 'blur' }
  ]
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

// Handle submit
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // Confirm submission
    await ElMessageBox.confirm(
      '评分提交后将无法修改或删除，请确认评分内容准确无误。确定要提交吗？',
      '确认提交评分',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    submitting.value = true

    // Convert form data to API format
    const scores: IndicatorScore[] = indicators.map(indicator => ({
      indicator: indicator.label,
      score: formData.scores[indicator.key].score,
      comment: formData.scores[indicator.key].comment
    }))

    const requestData: ManualScoreCreate = {
      evaluation_id: props.evaluationId,
      scores
    }

    // Submit to API
    const response = await scoringApi.submitManualScore(requestData)

    hasSubmitted.value = true

    ElMessage.success({
      message: '评分提交成功！评分记录已保存，无法修改。',
      duration: 5000,
      showClose: true
    })

    emit('submitted', response.data.score_record_id)

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Submit manual score failed:', error)

      const errorMessage = error.response?.data?.detail || '评分提交失败，请重试'

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
    
    // Reset scores to 0
    indicators.forEach(indicator => {
      formData.scores[indicator.key] = {
        score: 0,
        comment: ''
      }
    })
    
    ElMessage.info('表单已重置')
  }).catch(() => {
    // User cancelled
  })
}

// Handle view all scores
const handleViewAllScores = async () => {
  allScoresVisible.value = true
  allScoresLoading.value = true

  try {
    const response = await scoringApi.getAllScores(props.evaluationId)
    allScoresData.value = response.data

    // Check if current user has already submitted
    if (props.currentUserRole && allScoresData.value.manual_scores.length > 0) {
      const currentUserId = localStorage.getItem('userId') // Assuming userId is stored
      const hasUserSubmitted = allScoresData.value.manual_scores.some(
        score => score.reviewer_id === currentUserId
      )
      if (hasUserSubmitted) {
        hasSubmitted.value = true
      }
    }

  } catch (error: any) {
    console.error('Failed to load all scores:', error)

    const errorMessage = error.response?.data?.detail || '加载评分记录失败'

    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  } finally {
    allScoresLoading.value = false
  }
}

// Check if user has already submitted on mount
onMounted(async () => {
  // Optionally load all scores to check if user has submitted
  // This can be done by calling handleViewAllScores silently
})

// Expose methods
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  getFormData: () => ({ ...formData })
})
</script>

<style scoped>
.manual-scoring-form {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.scoring-card {
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

.weight-alert {
  margin-bottom: 20px;
}

.scoring-form {
  padding: 20px 0;
}

.indicator-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.indicator-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.indicator-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.max-score {
  font-size: 14px;
  color: #909399;
  font-weight: normal;
}

.score-input {
  width: 150px;
}

.score-hint {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}

.total-score-section {
  margin: 30px 0;
}

.total-score {
  text-align: center;
  font-size: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.total-score .label {
  font-weight: normal;
}

.total-score .value {
  font-weight: bold;
  font-size: 32px;
  margin: 0 10px;
}

.total-score .max {
  font-size: 18px;
  opacity: 0.9;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.form-actions :deep(.el-form-item__content) {
  justify-content: center;
}

/* All Scores Dialog Styles */
.all-scores-dialog {
  max-height: 80vh;
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

.all-scores-content {
  max-height: 70vh;
  overflow-y: auto;
}

.score-card {
  margin-bottom: 20px;
}

.score-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.ai-score-card {
  border: 2px solid #67c23a;
}

.manual-score-card {
  border: 2px solid #e6a23c;
}

.evaluation-team-card {
  border: 2px solid #f56c6c;
  background-color: #fef0f0;
}

.final-score-card {
  border: 2px solid #f56c6c;
}

.reviewer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reviewer-info h3 {
  margin: 0;
}

.role-tag {
  font-weight: bold;
}

.weight-tag {
  font-size: 12px;
}

.submit-time {
  font-size: 14px;
  color: #909399;
}

.score-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.score-item {
  flex: 1;
  min-width: 200px;
}

.score-item.full-width {
  flex-basis: 100%;
}

.score-item .label {
  font-weight: 600;
  color: #606266;
  margin-right: 8px;
}

.score-item .value {
  color: #303133;
}

.score-item .value.highlight {
  color: #f56c6c;
  font-weight: bold;
  font-size: 20px;
}

.score-item .value.large {
  font-size: 28px;
}

.summary-text {
  margin-top: 8px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.6;
  color: #606266;
}

.indicator-scores {
  margin-top: 20px;
}

.indicator-scores h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.indicator-score-item {
  padding: 12px;
  margin-bottom: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.indicator-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.indicator-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.indicator-score {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}

.indicator-reasoning,
.indicator-comment {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  margin-top: 4px;
}

.manual-scores-section {
  margin-top: 30px;
}

.section-title {
  margin: 20px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.manual-score-details {
  padding: 10px 0;
}

.total-score-row {
  text-align: right;
  font-size: 18px;
  padding: 10px 0;
}

.total-score-row .label {
  font-weight: 600;
  color: #606266;
  margin-right: 10px;
}

.total-score-row .value {
  color: #f56c6c;
  font-weight: bold;
  font-size: 20px;
}
</style>
