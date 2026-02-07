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
          @submitted="handleScoreSubmitted"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import ManualScoringForm from '@/components/ManualScoringForm.vue'

// Mock data - In real implementation, this would come from API
interface Evaluation {
  id: string
  teachingOfficeName: string
  evaluationYear: number
  status: string
  submittedAt?: string
}

// State
const evaluations = ref<Evaluation[]>([])
const selectedEvaluationId = ref<string>('')
const selectedEvaluation = ref<Evaluation | null>(null)
const currentUserRole = ref<'evaluation_team' | 'evaluation_office'>('evaluation_team')

// Load evaluations on mount
onMounted(async () => {
  await loadEvaluations()
  loadCurrentUserRole()
})

// Load evaluations
const loadEvaluations = async () => {
  // Mock data - Replace with actual API call
  evaluations.value = [
    {
      id: '1',
      teachingOfficeName: '计算机科学教研室',
      evaluationYear: 2024,
      status: 'ai_scored',
      submittedAt: '2024-01-15T10:30:00'
    },
    {
      id: '2',
      teachingOfficeName: '数学教研室',
      evaluationYear: 2024,
      status: 'ai_scored',
      submittedAt: '2024-01-16T14:20:00'
    },
    {
      id: '3',
      teachingOfficeName: '物理教研室',
      evaluationYear: 2024,
      status: 'manually_scored',
      submittedAt: '2024-01-17T09:15:00'
    }
  ]
}

// Load current user role
const loadCurrentUserRole = () => {
  // Mock - Replace with actual user role from auth
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

// Handle back to list
const handleBackToList = () => {
  selectedEvaluationId.value = ''
  selectedEvaluation.value = null
}

// Handle score submitted
const handleScoreSubmitted = (scoreRecordId: string) => {
  console.log('Score submitted:', scoreRecordId)
  
  // Optionally reload evaluations or update status
  setTimeout(() => {
    loadEvaluations()
  }, 1000)
}

// Get status tag type
const getStatusTagType = (status: string): string => {
  const types: Record<string, string> = {
    'draft': 'info',
    'submitted': 'warning',
    'locked': 'warning',
    'ai_scored': 'success',
    'manually_scored': 'primary',
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
</style>
