<template>
  <div class="president-office-dashboard">
    <h1>校长办公会 - 实时数据监控</h1>
    
    <!-- Filters -->
    <el-card class="filter-card">
      <el-form
        :inline="true"
        :model="filters"
      >
        <el-form-item label="考核年度">
          <el-select
            v-model="filters.year"
            placeholder="选择年度"
            clearable
            @change="loadData"
          >
            <el-option
              v-for="year in availableYears"
              :key="year"
              :label="year"
              :value="year"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="考核指标">
          <el-select
            v-model="filters.indicator"
            placeholder="选择指标"
            clearable
            @change="loadData"
          >
            <el-option
              v-for="indicator in indicators"
              :key="indicator.key"
              :label="indicator.label"
              :value="indicator.key"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="排序方式">
          <el-select
            v-model="filters.sortBy"
            placeholder="排序字段"
            @change="applySorting"
          >
            <el-option
              label="教研室名称"
              value="teaching_office_name"
            />
            <el-option
              label="AI评分"
              value="ai_score"
            />
            <el-option
              label="最终得分"
              value="final_score"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="排序顺序">
          <el-select
            v-model="filters.sortOrder"
            placeholder="排序顺序"
            @change="applySorting"
          >
            <el-option
              label="升序"
              value="asc"
            />
            <el-option
              label="降序"
              value="desc"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="loadData"
          >
            刷新数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Loading State -->
    <div
      v-if="loading"
      class="loading-container"
    >
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <p>加载数据中...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Summary Cards -->
      <el-row
        :gutter="20"
        class="summary-cards"
      >
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-label">
                教研室总数
              </div>
              <div class="stat-value">
                {{ dashboardData.teaching_office_scores.length }}
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-label">
                平均AI评分
              </div>
              <div class="stat-value">
                {{ averageAIScore.toFixed(2) }}
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-label">
                平均最终得分
              </div>
              <div class="stat-value">
                {{ averageFinalScore.toFixed(2) }}
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-card">
              <div class="stat-label">
                已完成评分
              </div>
              <div class="stat-value">
                {{ completedCount }}
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Scores Table -->
      <el-card class="scores-table-card">
        <template #header>
          <div class="card-header">
            <span>教研室评分详情</span>
          </div>
        </template>
        
        <el-table
          :data="sortedScores"
          stripe
          style="width: 100%"
          :default-sort="{ prop: filters.sortBy, order: filters.sortOrder === 'asc' ? 'ascending' : 'descending' }"
        >
          <el-table-column
            prop="teaching_office_name"
            label="教研室名称"
            width="200"
            sortable
          />
          <el-table-column
            prop="ai_score"
            label="AI评分"
            width="120"
            sortable
          >
            <template #default="scope">
              <el-tag
                v-if="scope.row.ai_score"
                type="info"
              >
                {{ scope.row.ai_score.toFixed(2) }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column
            label="评审人评分"
            min-width="300"
          >
            <template #default="scope">
              <div
                v-if="scope.row.manual_scores.length > 0"
                class="reviewer-scores"
              >
                <el-tag
                  v-for="(score, index) in scope.row.manual_scores"
                  :key="index"
                  :type="score.reviewer_role === 'evaluation_team' ? 'success' : 'warning'"
                  class="reviewer-tag"
                >
                  {{ score.reviewer_name }}: {{ score.total_score.toFixed(2) }}
                </el-tag>
              </div>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="final_score"
            label="最终得分"
            width="120"
            sortable
          >
            <template #default="scope">
              <el-tag
                v-if="scope.row.final_score"
                type="success"
                effect="dark"
              >
                {{ scope.row.final_score.toFixed(2) }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="status"
            label="状态"
            width="120"
          >
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusLabel(scope.row.status) }}
              </el-tag>
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
                @click="viewDetails(scope.row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- Batch Approval Actions -->
      <el-card class="approval-actions-card">
        <template #header>
          <div class="card-header">
            <span>批量审定操作</span>
          </div>
        </template>
        
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        >
          请选择需要审定的教研室，然后点击"同意公示"或"驳回重新审核"按钮
        </el-alert>
        
        <div class="approval-actions">
          <el-checkbox-group v-model="selectedEvaluationIds">
            <div
              v-for="office in finalizableOffices"
              :key="office.teaching_office_id"
              class="approval-checkbox-item"
            >
              <el-checkbox :label="office.teaching_office_id">
                {{ office.teaching_office_name }} - 最终得分: {{ office.final_score?.toFixed(2) || '-' }}
              </el-checkbox>
            </div>
          </el-checkbox-group>
          
          <div class="approval-buttons">
            <el-button
              type="success"
              :disabled="selectedEvaluationIds.length === 0"
              @click="openApprovalDialog('approve')"
            >
              同意公示
            </el-button>
            <el-button
              type="danger"
              :disabled="selectedEvaluationIds.length === 0"
              @click="openApprovalDialog('reject')"
            >
              驳回重新审核
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- Charts Section -->
      <el-row
        :gutter="20"
        class="charts-section"
      >
        <!-- Score Comparison Chart -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>评分对比图</span>
              </div>
            </template>
            <div class="chart-container">
              <div class="chart-placeholder">
                <div
                  v-for="(score, index) in sortedScores.slice(0, 10)"
                  :key="index"
                  class="bar-chart-item"
                >
                  <div class="bar-label">
                    {{ score.teaching_office_name }}
                  </div>
                  <div class="bar-container">
                    <div
                      class="bar ai-bar"
                      :style="{ width: `${(score.ai_score || 0) / 100 * 100}%` }"
                    >
                      <span v-if="score.ai_score">{{ score.ai_score.toFixed(1) }}</span>
                    </div>
                  </div>
                  <div class="bar-container">
                    <div
                      class="bar final-bar"
                      :style="{ width: `${(score.final_score || 0) / 100 * 100}%` }"
                    >
                      <span v-if="score.final_score">{{ score.final_score.toFixed(1) }}</span>
                    </div>
                  </div>
                </div>
                <div class="chart-legend">
                  <span class="legend-item"><span class="legend-color ai-color" /> AI评分</span>
                  <span class="legend-item"><span class="legend-color final-color" /> 最终得分</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Ranking Chart -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>横向对比排名</span>
              </div>
            </template>
            <div class="chart-container">
              <el-table
                :data="rankedScores"
                stripe
                style="width: 100%"
                max-height="400"
              >
                <el-table-column
                  label="排名"
                  width="80"
                >
                  <template #default="scope">
                    <el-tag
                      :type="scope.$index < 3 ? 'danger' : 'info'"
                      effect="dark"
                    >
                      {{ scope.$index + 1 }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="teaching_office_name"
                  label="教研室"
                />
                <el-table-column
                  prop="final_score"
                  label="最终得分"
                  width="120"
                >
                  <template #default="scope">
                    {{ scope.row.final_score ? scope.row.final_score.toFixed(2) : '-' }}
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Historical Trends -->
      <el-card class="historical-card">
        <template #header>
          <div class="card-header">
            <span>历史分数变化趋势</span>
            <el-select
              v-model="selectedOfficeForHistory"
              placeholder="选择教研室"
              style="width: 200px"
              @change="loadHistoricalData"
            >
              <el-option
                v-for="office in dashboardData.teaching_office_scores"
                :key="office.teaching_office_id"
                :label="office.teaching_office_name"
                :value="office.teaching_office_id"
              />
            </el-select>
          </div>
        </template>
        <div
          v-if="historicalData.length > 0"
          class="historical-chart"
        >
          <div
            v-for="(data, index) in historicalData"
            :key="index"
            class="historical-item"
          >
            <div class="historical-year">
              {{ data.year }}
            </div>
            <div class="historical-bar-container">
              <div
                class="historical-bar"
                :style="{ width: `${(data.final_score / 100) * 100}%` }"
              >
                {{ data.final_score.toFixed(2) }}
              </div>
            </div>
          </div>
        </div>
        <el-empty
          v-else
          description="请选择教研室查看历史数据"
        />
      </el-card>
    </div>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="教研室评分详情"
      width="70%"
    >
      <div v-if="selectedOffice">
        <h3>{{ selectedOffice.teaching_office_name }}</h3>
        
        <el-descriptions
          :column="2"
          border
        >
          <el-descriptions-item label="AI评分">
            {{ selectedOffice.ai_score ? selectedOffice.ai_score.toFixed(2) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="最终得分">
            {{ selectedOffice.final_score ? selectedOffice.final_score.toFixed(2) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            {{ getStatusLabel(selectedOffice.status) }}
          </el-descriptions-item>
          <el-descriptions-item label="考核年度">
            {{ selectedOffice.evaluation_year }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px">
          评审人评分记录
        </h4>
        <el-table
          :data="selectedOffice.manual_scores"
          stripe
        >
          <el-table-column
            prop="reviewer_name"
            label="评审人"
          />
          <el-table-column label="角色">
            <template #default="scope">
              <el-tag :type="scope.row.reviewer_role === 'evaluation_team' ? 'success' : 'warning'">
                {{ scope.row.reviewer_role === 'evaluation_team' ? '考评小组' : '考评办公室' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="total_score"
            label="总分"
          >
            <template #default="scope">
              {{ scope.row.total_score.toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>

    <!-- Approval Dialog -->
    <el-dialog
      v-model="approvalDialogVisible"
      :title="approvalDecision === 'approve' ? '同意公示' : '驳回重新审核'"
      width="50%"
    >
      <div v-if="approvalDecision === 'approve'">
        <el-alert
          title="确认同意公示"
          type="success"
          :closable="false"
          style="margin-bottom: 15px"
        >
          您即将同意以下 {{ selectedEvaluationIds.length }} 个教研室的考评结果公示。
          同意后，管理端将可以发起公示流程。
        </el-alert>
        
        <div class="selected-offices-list">
          <div
            v-for="officeId in selectedEvaluationIds"
            :key="officeId"
            class="selected-office-item"
          >
            {{ getOfficeName(officeId) }}
          </div>
        </div>
      </div>
      
      <div v-else>
        <el-alert
          title="确认驳回重新审核"
          type="warning"
          :closable="false"
          style="margin-bottom: 15px"
        >
          您即将驳回以下 {{ selectedEvaluationIds.length }} 个教研室的考评结果。
          驳回后，管理端将收到驳回原因并需要重新审核。
        </el-alert>
        
        <div class="selected-offices-list">
          <div
            v-for="officeId in selectedEvaluationIds"
            :key="officeId"
            class="selected-office-item"
          >
            {{ getOfficeName(officeId) }}
          </div>
        </div>
        
        <el-form
          :model="approvalForm"
          style="margin-top: 20px"
        >
          <el-form-item
            label="驳回原因"
            required
          >
            <el-input
              v-model="approvalForm.rejectReason"
              type="textarea"
              :rows="4"
              placeholder="请填写驳回原因，将反馈至管理端"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="approvalDialogVisible = false">
          取消
        </el-button>
        <el-button
          :type="approvalDecision === 'approve' ? 'success' : 'danger'"
          :loading="approvalLoading"
          @click="submitApproval"
        >
          确认{{ approvalDecision === 'approve' ? '同意' : '驳回' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { presidentOfficeApi } from '@/api/client'
import type { TeachingOfficeScore, DashboardData, DashboardFilters, ApprovalRequest } from '@/types/presidentOffice'
import { EVALUATION_INDICATORS } from '@/types/scoring'

// Data
const loading = ref(false)
const dashboardData = ref<DashboardData>({
  teaching_office_scores: [],
  historical_scores: [],
  indicator_comparisons: []
})

const filters = ref<DashboardFilters>({
  year: new Date().getFullYear(),
  indicator: undefined,
  sortBy: 'final_score',
  sortOrder: 'desc'
})

const indicators = EVALUATION_INDICATORS
const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
})

const selectedOfficeForHistory = ref<string>('')
const historicalData = ref<Array<{ year: number; final_score: number }>>([])

const detailDialogVisible = ref(false)
const selectedOffice = ref<TeachingOfficeScore | null>(null)

// Approval data
const selectedEvaluationIds = ref<string[]>([])
const approvalDialogVisible = ref(false)
const approvalDecision = ref<'approve' | 'reject'>('approve')
const approvalLoading = ref(false)
const approvalForm = ref({
  rejectReason: ''
})

// Computed
const sortedScores = computed(() => {
  const scores = [...dashboardData.value.teaching_office_scores]
  const { sortBy, sortOrder } = filters.value
  
  if (!sortBy) return scores
  
  return scores.sort((a, b) => {
    let aValue: any = a[sortBy as keyof TeachingOfficeScore]
    let bValue: any = b[sortBy as keyof TeachingOfficeScore]
    
    // Handle undefined values
    if (aValue === undefined) aValue = 0
    if (bValue === undefined) bValue = 0
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
})

const rankedScores = computed(() => {
  return [...dashboardData.value.teaching_office_scores]
    .filter(score => score.final_score !== undefined)
    .sort((a, b) => (b.final_score || 0) - (a.final_score || 0))
})

const averageAIScore = computed(() => {
  const scores = dashboardData.value.teaching_office_scores
    .filter(s => s.ai_score !== undefined)
    .map(s => s.ai_score || 0)
  return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0
})

const averageFinalScore = computed(() => {
  const scores = dashboardData.value.teaching_office_scores
    .filter(s => s.final_score !== undefined)
    .map(s => s.final_score || 0)
  return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0
})

const completedCount = computed(() => {
  return dashboardData.value.teaching_office_scores.filter(
    s => s.final_score !== undefined
  ).length
})

const finalizableOffices = computed(() => {
  // Only show offices that have final scores and are in 'finalized' status
  return dashboardData.value.teaching_office_scores.filter(
    office => office.final_score !== undefined && office.status === 'finalized'
  )
})

// Methods
const loadData = async () => {
  loading.value = true
  try {
    const response = await presidentOfficeApi.getDashboardData({
      year: filters.value.year,
      indicator: filters.value.indicator
    })
    dashboardData.value = response.data
    ElMessage.success('数据加载成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载数据失败')
  } finally {
    loading.value = false
  }
}

const applySorting = () => {
  // Sorting is handled by computed property
}

const loadHistoricalData = async () => {
  if (!selectedOfficeForHistory.value) return
  
  try {
    const response = await presidentOfficeApi.getHistoricalScores(selectedOfficeForHistory.value)
    const officeData = response.data.find(
      (d: any) => d.teaching_office_id === selectedOfficeForHistory.value
    )
    historicalData.value = officeData?.scores || []
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载历史数据失败')
  }
}

const viewDetails = (office: TeachingOfficeScore) => {
  selectedOffice.value = office
  detailDialogVisible.value = true
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    'draft': 'info',
    'submitted': 'warning',
    'ai_scored': 'primary',
    'manually_scored': 'success',
    'finalized': 'success',
    'published': 'success'
  }
  return statusMap[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labelMap: Record<string, string> = {
    'draft': '草稿',
    'submitted': '已提交',
    'ai_scored': 'AI已评分',
    'manually_scored': '已手动评分',
    'finalized': '已确定最终得分',
    'approved': '已审定同意',
    'rejected_by_president': '已驳回',
    'published': '已公示'
  }
  return labelMap[status] || status
}

const openApprovalDialog = (decision: 'approve' | 'reject') => {
  approvalDecision.value = decision
  approvalForm.value.rejectReason = ''
  approvalDialogVisible.value = true
}

const getOfficeName = (officeId: string) => {
  const office = dashboardData.value.teaching_office_scores.find(
    o => o.teaching_office_id === officeId
  )
  return office ? office.teaching_office_name : officeId
}

const submitApproval = async () => {
  // Validate reject reason if decision is reject
  if (approvalDecision.value === 'reject' && !approvalForm.value.rejectReason.trim()) {
    ElMessage.error('请填写驳回原因')
    return
  }
  
  approvalLoading.value = true
  
  try {
    const request: ApprovalRequest = {
      evaluation_ids: selectedEvaluationIds.value,
      decision: approvalDecision.value,
      reject_reason: approvalDecision.value === 'reject' ? approvalForm.value.rejectReason : undefined
    }
    
    const response = await presidentOfficeApi.approveResults(request)
    
    ElMessage.success(response.data.message)
    
    // Close dialog and reset
    approvalDialogVisible.value = false
    selectedEvaluationIds.value = []
    approvalForm.value.rejectReason = ''
    
    // Reload data to reflect updated status
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '审定操作失败')
  } finally {
    approvalLoading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.president-office-dashboard {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.loading-container {
  text-align: center;
  padding: 50px;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.summary-cards {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.scores-table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reviewer-scores {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.reviewer-tag {
  margin: 2px;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-container {
  min-height: 400px;
  padding: 10px;
}

.chart-placeholder {
  width: 100%;
}

.bar-chart-item {
  margin-bottom: 15px;
}

.bar-label {
  font-size: 12px;
  margin-bottom: 5px;
  color: #606266;
}

.bar-container {
  height: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 3px;
  position: relative;
}

.bar {
  height: 100%;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 5px;
  color: white;
  font-size: 11px;
  transition: width 0.3s ease;
}

.ai-bar {
  background: linear-gradient(90deg, #409eff, #66b1ff);
}

.final-bar {
  background: linear-gradient(90deg, #67c23a, #85ce61);
}

.chart-legend {
  margin-top: 15px;
  display: flex;
  gap: 20px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 2px;
}

.ai-color {
  background: linear-gradient(90deg, #409eff, #66b1ff);
}

.final-color {
  background: linear-gradient(90deg, #67c23a, #85ce61);
}

.historical-card {
  margin-bottom: 20px;
}

.historical-chart {
  padding: 20px;
}

.historical-item {
  margin-bottom: 15px;
}

.historical-year {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.historical-bar-container {
  height: 30px;
  background-color: #f5f7fa;
  border-radius: 4px;
  position: relative;
}

.historical-bar {
  height: 100%;
  background: linear-gradient(90deg, #e6a23c, #f0c78a);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
  color: white;
  font-weight: bold;
  transition: width 0.3s ease;
}

.approval-actions-card {
  margin-bottom: 20px;
}

.approval-actions {
  padding: 10px 0;
}

.approval-checkbox-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.approval-checkbox-item:last-child {
  border-bottom: none;
}

.approval-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.selected-offices-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
}

.selected-office-item {
  padding: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.selected-office-item:last-child {
  margin-bottom: 0;
}
</style>
