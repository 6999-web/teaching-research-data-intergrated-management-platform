<template>
  <div class="final-score-page">
    <PageHeader 
      title="确定最终得分" 
      :breadcrumbs="[
        { label: '管理端' },
        { label: '确定最终得分' }
      ]"
    />

    <div class="page-content">
      <!-- Evaluation Selection -->
      <el-card
        v-if="!selectedEvaluationId"
        class="selection-card"
      >
        <template #header>
          <h2>选择待确定最终得分的教研室</h2>
        </template>
        
        <el-table
          :data="evaluations"
          stripe
          style="width: 100%"
          class="evaluation-table"
          @row-click="handleSelectEvaluation"
        >
          <el-table-column
            prop="teachingOfficeName"
            label="教研室名称"
            width="200"
          />
          <el-table-column
            prop="evaluationYear"
            label="考评年度"
            width="120"
          />
          <el-table-column
            prop="status"
            label="状态"
            width="150"
          >
            <template #default="scope">
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ getStatusLabel(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="manualScoresCount"
            label="评审人打分数"
            width="150"
          >
            <template #default="scope">
              <el-tag type="info">
                {{ scope.row.manualScoresCount }}人
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="submittedAt"
            label="提交时间"
            width="180"
          >
            <template #default="scope">
              {{ scope.row.submittedAt ? formatDate(scope.row.submittedAt) : '-' }}
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="150"
          >
            <template #default="scope">
              <el-button
                type="primary"
                size="small"
                @click.stop="handleSelectEvaluation(scope.row)"
              >
                {{ scope.row.status === 'finalized' ? '查看详情' : '确定得分' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="evaluations.length === 0"
          description="暂无待确定最终得分的教研室"
        />
      </el-card>

      <!-- Final Score Form -->
      <div
        v-else
        class="final-score-section"
      >
        <el-card class="info-card">
          <div class="evaluation-info">
            <div class="info-item">
              <span class="label">教研室：</span>
              <span class="value">{{ selectedEvaluation?.teachingOfficeName }}</span>
            </div>
            <div class="info-item">
              <span class="label">考评年度：</span>
              <span class="value">{{ selectedEvaluation?.evaluationYear }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态：</span>
              <el-tag :type="getStatusTagType(selectedEvaluation?.status || '')">
                {{ getStatusLabel(selectedEvaluation?.status || '') }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">评审人打分数：</span>
              <el-tag type="info">
                {{ selectedEvaluation?.manualScoresCount }}人
              </el-tag>
            </div>
          </div>
          <el-button
            type="info"
            size="small"
            @click="handleBackToList"
          >
            返回列表
          </el-button>
        </el-card>

        <FinalScoreForm
          :evaluation-id="selectedEvaluationId"
          @submitted="handleFinalScoreSubmitted"
          @view-details="handleViewDetails"
        />
      </div>
    </div>

    <!-- Detailed Scores Dialog -->
    <el-dialog
      v-model="detailsDialogVisible"
      title="详细评分记录"
      width="90%"
      :close-on-click-modal="false"
      class="details-dialog"
    >
      <div
        v-if="detailsLoading"
        class="loading-container"
      >
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
        <span>加载中...</span>
      </div>

      <div
        v-else-if="detailsData"
        class="details-content"
      >
        <!-- AI Score Section -->
        <el-card
          v-if="detailsData.ai_score"
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
              <span class="value highlight">{{ detailsData.ai_score.total_score.toFixed(1) }}分</span>
            </div>
            <div class="score-item">
              <span class="label">评分时间：</span>
              <span class="value">{{ formatDateTime(detailsData.ai_score.scored_at) }}</span>
            </div>
          </div>
          <el-divider />
          <div class="indicator-scores">
            <h4>各指标得分：</h4>
            <div
              v-for="(indicatorScore, index) in detailsData.ai_score.indicator_scores"
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
          v-if="detailsData.manual_scores.length > 0"
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
      </div>

      <template #footer>
        <el-button @click="detailsDialogVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { Loading } from '@element-plus/icons-vue'
import FinalScoreForm from '@/components/FinalScoreForm.vue'
import { scoringApi } from '@/api/client'
import type { AllScoresResponse, IndicatorScore } from '@/types/scoring'

// Mock data - In real implementation, this would come from API
interface Evaluation {
  id: string
  teachingOfficeName: string
  evaluationYear: number
  status: string
  manualScoresCount: number
  submittedAt?: string
}

// State
const evaluations = ref<Evaluation[]>([])
const selectedEvaluationId = ref<string>('')
const selectedEvaluation = ref<Evaluation | null>(null)
const detailsDialogVisible = ref(false)
const detailsLoading = ref(false)
const detailsData = ref<AllScoresResponse | null>(null)

// Computed: Sorted manual scores (evaluation_team first)
const sortedManualScores = computed(() => {
  if (!detailsData.value) return []
  
  return [...detailsData.value.manual_scores].sort((a, b) => {
    if (a.reviewer_role === 'evaluation_team' && b.reviewer_role !== 'evaluation_team') {
      return -1
    }
    if (a.reviewer_role !== 'evaluation_team' && b.reviewer_role === 'evaluation_team') {
      return 1
    }
    return new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
  })
})

// Load evaluations on mount
onMounted(async () => {
  await loadEvaluations()
})

// Load evaluations
const loadEvaluations = async () => {
  // Mock data - Replace with actual API call
  evaluations.value = [
    {
      id: '1',
      teachingOfficeName: '计算机科学教研室',
      evaluationYear: 2024,
      status: 'manually_scored',
      manualScoresCount: 3,
      submittedAt: '2024-01-15T10:30:00'
    },
    {
      id: '2',
      teachingOfficeName: '数学教研室',
      evaluationYear: 2024,
      status: 'manually_scored',
      manualScoresCount: 2,
      submittedAt: '2024-01-16T14:20:00'
    },
    {
      id: '3',
      teachingOfficeName: '物理教研室',
      evaluationYear: 2024,
      status: 'finalized',
      manualScoresCount: 3,
      submittedAt: '2024-01-17T09:15:00'
    }
  ]
}

// Handle select evaluation
const handleSelectEvaluation = (evaluation: Evaluation) => {
  selectedEvaluationId.value = evaluation.id
  selectedEvaluation.value = evaluation
}

// Handle back to list
const handleBackToList = () => {
  selectedEvaluationId.value = ''
  selectedEvaluation.value = null
}

// Handle final score submitted
const handleFinalScoreSubmitted = (finalScoreId: string) => {
  console.log('Final score submitted:', finalScoreId)
  
  // Optionally reload evaluations or update status
  setTimeout(() => {
    loadEvaluations()
  }, 1000)
}

// Handle view details
const handleViewDetails = async () => {
  detailsDialogVisible.value = true
  detailsLoading.value = true

  try {
    const response = await scoringApi.getAllScores(selectedEvaluationId.value)
    detailsData.value = response.data

  } catch (error: any) {
    console.error('Failed to load details:', error)

    const errorMessage = error.response?.data?.detail || '加载详细评分记录失败'

    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  } finally {
    detailsLoading.value = false
  }
}

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

// Get status tag type
const getStatusTagType = (status: string): string => {
  const types: Record<string, string> = {
    'draft': 'info',
    'submitted': 'warning',
    'locked': 'warning',
    'ai_scored': 'success',
    'manually_scored': 'primary',
    'ready_for_final': 'warning',
    'finalized': 'danger',
    'published': 'success'
  }
  return types[status] || 'info'
}

// Get status label
const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    'draft': '草稿',
    'submitted': '已提交',
    'locked': '已锁定',
    'ai_scored': 'AI已评分',
    'manually_scored': '已手动评分',
    'ready_for_final': '待最终确定',
    'finalized': '已确定最终得分',
    'published': '已公示'
  }
  return labels[status] || status
}

// Format date
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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
</script>

<style scoped>
.final-score-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #303133;
}

.page-content {
  max-width: 1400px;
  margin: 0 auto;
}

.selection-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.selection-card h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.evaluation-table {
  margin-top: 20px;
}

.evaluation-table :deep(.el-table__row) {
  cursor: pointer;
}

.evaluation-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.final-score-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.evaluation-info {
  display: flex;
  gap: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item .label {
  font-weight: 600;
  color: #606266;
  margin-right: 8px;
}

.info-item .value {
  color: #303133;
  font-size: 16px;
}

/* Details Dialog Styles */
.details-dialog {
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

.details-content {
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
