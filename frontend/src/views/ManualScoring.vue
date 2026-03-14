<template>
  <div class="manual-scoring-page">
    <PageHeader 
      title="手动评分" 
      :breadcrumbs="[
        { label: '管理端' },
        { label: '手动评分' }
      ]"
    />

    <div class="page-content">
      <!-- Evaluation Selection -->
      <el-card
        v-if="!selectedEvaluationId"
        class="selection-card"
      >
        <template #header>
          <h2>选择待评分的教研室</h2>
        </template>
        
        <el-table
          :data="evaluations"
          stripe
          style="width: 100%"
          class="evaluation-table"
          v-loading="loading"
          @row-click="handleSelectEvaluation"
        >
          <el-table-column
            prop="teaching_office_name"
            label="教研室名称"
            width="200"
          />
          <el-table-column
            prop="evaluation_year"
            label="考评年度"
            width="120"
          />
          <el-table-column
            prop="status"
            label="状态"
            width="150"
          >
            <template #default="scope">
              <el-tag 
                :type="getStatusTagType(scope.row.status)"
                :class="getStatusClass(scope.row.status)"
              >
                {{ getStatusLabel(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="submitted_at"
            label="提交时间"
            width="180"
          >
            <template #default="scope">
              {{ scope.row.submitted_at ? formatDate(scope.row.submitted_at) : '-' }}
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
                开始评分
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="evaluations.length === 0"
          description="暂无待评分的教研室"
        />
      </el-card>

      <!-- Manual Scoring Form -->
      <div
        v-else
        class="scoring-section"
      >
        <el-card class="info-card">
          <div class="evaluation-info">
            <div class="info-item">
              <span class="label">教研室：</span>
              <span class="value">{{ selectedEvaluation?.teaching_office_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">考评年度：</span>
              <span class="value">{{ selectedEvaluation?.evaluation_year }}</span>
            </div>
            <div class="info-item">
              <span class="label">状态：</span>
              <el-tag 
                :type="getStatusTagType(selectedEvaluation?.status || '')"
                :class="getStatusClass(selectedEvaluation?.status || '')"
              >
                {{ getStatusLabel(selectedEvaluation?.status || '') }}
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

        <ManualScoringForm
          :evaluation-id="selectedEvaluationId"
          :current-user-role="currentUserRole"
          :evaluation-status="selectedEvaluation?.status"
          @submitted="handleScoreSubmitted"
          @submitted-to-office="handleSubmittedToOffice"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import ManualScoringForm from '@/components/ManualScoringForm.vue'
import { scoringApi } from '@/api/client'

const route = useRoute()

// Evaluation interface
interface Evaluation {
  id: string
  teaching_office_id: string
  teaching_office_name: string
  evaluation_year: number
  status: string
  submitted_at?: string
}

// State
const evaluations = ref<Evaluation[]>([])
const selectedEvaluationId = ref<string>('')
const selectedEvaluation = ref<Evaluation | null>(null)
const currentUserRole = ref<'evaluation_team' | 'evaluation_office'>('evaluation_team')
const loading = ref(false)

// Load evaluations on mount；若 URL 带 evaluationId 则自动选中该考评（数据流通、状态正确）
onMounted(async () => {
  await loadEvaluations()
  loadCurrentUserRole()
  const idFromQuery = route.query.evaluationId as string | undefined
  if (idFromQuery && evaluations.value.length) {
    const found = evaluations.value.find((e: Evaluation) => e.id === idFromQuery)
    if (found) {
      selectedEvaluationId.value = found.id
      selectedEvaluation.value = found
    }
  }
})

// 页面重新可见时刷新列表，保证状态为真实最新
const onVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    loadEvaluations().then(() => {
      if (selectedEvaluationId.value) {
        const updated = evaluations.value.find((e: Evaluation) => e.id === selectedEvaluationId.value)
        if (updated) selectedEvaluation.value = updated
      }
    })
  }
}
onMounted(() => document.addEventListener('visibilitychange', onVisibilityChange))
onUnmounted(() => document.removeEventListener('visibilitychange', onVisibilityChange))

// Load evaluations from API
const loadEvaluations = async () => {
  try {
    loading.value = true
    // 不传status参数，后端会默认返回 locked 和 ai_scored 状态的自评表
    const response = await scoringApi.getEvaluationsForScoring({})
    
    const raw = response.data
    evaluations.value = Array.isArray(raw) ? raw : (raw?.items ?? raw?.value ?? raw?.list ?? [])
    
    console.log('Loaded evaluations:', evaluations.value.length)
  } catch (error: any) {
    console.error('Failed to load evaluations:', error)
    ElMessage.error(error.response?.data?.detail || '加载待评分列表失败')
    evaluations.value = []
  } finally {
    loading.value = false
  }
}

// Load current user role（从本地存储恢复，与 auth store 一致）
const loadCurrentUserRole = () => {
  const role = localStorage.getItem('userRole')
  if (role === 'evaluation_team' || role === 'evaluation_office') {
    currentUserRole.value = role
  }
}

// Handle select evaluation
const handleSelectEvaluation = (evaluation: Evaluation) => {
  selectedEvaluationId.value = evaluation.id
  selectedEvaluation.value = evaluation
}

// Handle back to list：返回时刷新列表，保证状态为最新
const handleBackToList = async () => {
  selectedEvaluationId.value = ''
  selectedEvaluation.value = null
  await loadEvaluations()
}

// Handle score submitted：刷新列表并更新当前选中项状态，使状态立即显示「已评分」
const handleScoreSubmitted = async (scoreRecordId: string) => {
  console.log('Score submitted:', scoreRecordId)
  await new Promise(r => setTimeout(r, 600))
  await loadEvaluations()
  const id = String(selectedEvaluationId.value).trim()
  const updated = evaluations.value.find((e: Evaluation) => String(e.id).trim() === id)
  if (updated) selectedEvaluation.value = { ...updated }
}

// Handle submitted to office
const handleSubmittedToOffice = async (evaluationId: string) => {
  console.log('Submitted to office:', evaluationId)
  await loadEvaluations()
  // 用最新列表更新当前选中项状态，保证状态实时更新
  const updated = evaluations.value.find((e: Evaluation) => e.id === evaluationId)
  if (updated) selectedEvaluation.value = updated
  setTimeout(() => handleBackToList(), 1000)
}

// 手动评分列表状态规则（与产品一致）：
// - 评分前：还没有评分（无人提交过手动评分）
// - 已评分：已有人评分，未计算平均分/未提交到评教小组办公室
// - 已提交：已提交到评教小组办公室端
const getStatusTagType = (status: string): string => {
  const displayStatus = getManualScoringStatus(status)
  const map: Record<string, string> = { '评分前': 'warning', '已评分': 'success', '已提交': 'primary' }
  return map[displayStatus] || 'info'
}

const getStatusLabel = (status: string): string => {
  return getManualScoringStatus(status)
}

function getManualScoringStatus(status: string): '评分前' | '已评分' | '已提交' {
  if (!status) return '评分前'
  // 已评分：评分了、未提交到办公室（后端状态 manually_scored）
  if (status === 'manually_scored') return '已评分'
  // 已提交：已提交到评教小组办公室端
  if (['ready_for_final', 'finalized', 'published', 'distributed'].includes(status)) return '已提交'
  // 评分前：还没有评分（submitted, locked, ai_scored 等）
  return '评分前'
}

// Get custom status class for yellow color
const getStatusClass = (status: string): string => {
  return getManualScoringStatus(status) === '评分前' ? 'status-yellow' : ''
}

// Format date - 显示真实时间格式 YYYY-MM-DD HH:mm:ss
const formatDate = (date: string | number | Date): string => {
  if (!date) return '-'
  const d = new Date(date)
  
  // Check if date is valid
  if (isNaN(d.getTime())) {
    return String(date) || '-'
  }

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}
</script>

<style scoped>
.manual-scoring-page {
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

.scoring-section {
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

/* Custom yellow status tag */
.status-yellow {
  background-color: #fef0cd !important;
  border-color: #f7d794 !important;
  color: #d68910 !important;
}

.status-yellow.el-tag {
  background-color: #fef0cd !important;
  border-color: #f7d794 !important;
  color: #d68910 !important;
}
</style>
