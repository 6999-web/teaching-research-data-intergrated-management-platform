<template>
  <div class="management-result-page">
    <div class="page-header">
      <h1>考评结果汇总</h1>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">
          首页
        </el-breadcrumb-item>
        <el-breadcrumb-item>管理端</el-breadcrumb-item>
        <el-breadcrumb-item>结果汇总</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="page-content">
      <!-- Filter Card -->
      <el-card class="filter-card">
        <el-form
          :inline="true"
          :model="filters"
          class="filter-form"
        >
          <el-form-item label="考评年度">
            <el-select
              v-model="filters.year"
              placeholder="选择年度"
              clearable
              @change="loadResults"
            >
              <el-option
                v-for="year in availableYears"
                :key="year"
                :label="`${year}年`"
                :value="year"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select
              v-model="filters.status"
              placeholder="选择状态"
              clearable
              @change="loadResults"
            >
              <el-option
                label="已公示"
                value="published"
              />
              <el-option
                label="已审定"
                value="approved"
              />
              <el-option
                label="已确定最终得分"
                value="finalized"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              :icon="Search"
              @click="loadResults"
            >
              查询
            </el-button>
            <el-button
              :icon="Refresh"
              @click="resetFilters"
            >
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Results Summary Card -->
      <el-card
        v-loading="loading"
        class="summary-card"
      >
        <template #header>
          <div class="card-header">
            <h2>教研室考评结果汇总</h2>
            <div class="header-actions">
              <el-button
                type="success"
                :icon="Download"
                size="small"
                @click="exportResults"
              >
                导出结果
              </el-button>
            </div>
          </div>
        </template>

        <!-- Statistics Overview -->
        <div
          v-if="results.length > 0"
          class="statistics-overview"
        >
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div
                  class="stat-icon"
                  style="background-color: #409eff;"
                >
                  <el-icon><School /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">
                    {{ results.length }}
                  </div>
                  <div class="stat-label">
                    教研室总数
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div
                  class="stat-icon"
                  style="background-color: #67c23a;"
                >
                  <el-icon><CircleCheck /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">
                    {{ publishedCount }}
                  </div>
                  <div class="stat-label">
                    已公示
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div
                  class="stat-icon"
                  style="background-color: #e6a23c;"
                >
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">
                    {{ averageScore.toFixed(1) }}
                  </div>
                  <div class="stat-label">
                    平均得分
                  </div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div
                  class="stat-icon"
                  style="background-color: #f56c6c;"
                >
                  <el-icon><Trophy /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">
                    {{ highestScore.toFixed(1) }}
                  </div>
                  <div class="stat-label">
                    最高得分
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- Results Table -->
        <el-table
          :data="paginatedResults"
          stripe
          style="width: 100%; margin-top: 20px;"
          :default-sort="{ prop: 'final_score', order: 'descending' }"
          @sort-change="handleSortChange"
        >
          <el-table-column
            type="index"
            label="排名"
            width="80"
            align="center"
          />
          <el-table-column
            prop="teaching_office_name"
            label="教研室名称"
            width="200"
            sortable="custom"
          />
          <el-table-column
            prop="evaluation_year"
            label="考评年度"
            width="120"
            align="center"
            sortable="custom"
          />
          <el-table-column
            prop="final_score"
            label="最终得分"
            width="120"
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              <el-tag
                :type="getScoreTagType(row.final_score)"
                size="large"
                effect="dark"
              >
                {{ row.final_score?.toFixed(1) || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="ai_score"
            label="AI评分"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              {{ row.ai_score?.toFixed(1) || '-' }}
            </template>
          </el-table-column>
          <el-table-column
            prop="manual_score_avg"
            label="人工评分均值"
            width="130"
            align="center"
          >
            <template #default="{ row }">
              {{ row.manual_score_avg?.toFixed(1) || '-' }}
            </template>
          </el-table-column>
          <el-table-column
            prop="approval_status"
            label="审定结果"
            width="150"
            align="center"
          >
            <template #default="{ row }">
              <el-tag :type="getApprovalTagType(row.approval_status)">
                {{ getApprovalLabel(row.approval_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="status"
            label="状态"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="published_at"
            label="公示时间"
            width="180"
            align="center"
          >
            <template #default="{ row }">
              {{ row.published_at ? formatDate(row.published_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="180"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button
                type="primary"
                size="small"
                link
                @click="viewDetail(row)"
              >
                查看详情
              </el-button>
              <el-button
                v-if="row.approval_status === 'rejected'"
                type="warning"
                size="small"
                link
                @click="viewRejectReason(row)"
              >
                驳回原因
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Empty State -->
        <el-empty
          v-if="results.length === 0 && !loading"
          description="暂无考评结果数据"
        />

        <!-- Pagination -->
        <div
          v-if="results.length > 0"
          class="pagination-container"
        >
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="results.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="考评结果详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <div
        v-if="selectedResult"
        class="detail-content"
      >
        <el-descriptions
          :column="2"
          border
        >
          <el-descriptions-item label="教研室名称">
            {{ selectedResult.teaching_office_name }}
          </el-descriptions-item>
          <el-descriptions-item label="考评年度">
            {{ selectedResult.evaluation_year }}
          </el-descriptions-item>
          <el-descriptions-item label="最终得分">
            <el-tag
              :type="getScoreTagType(selectedResult.final_score)"
              size="large"
            >
              {{ selectedResult.final_score?.toFixed(1) || '-' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="AI评分">
            {{ selectedResult.ai_score?.toFixed(1) || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="审定结果">
            <el-tag :type="getApprovalTagType(selectedResult.approval_status)">
              {{ getApprovalLabel(selectedResult.approval_status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(selectedResult.status)">
              {{ getStatusLabel(selectedResult.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item
            v-if="selectedResult.approved_at"
            label="审定时间"
          >
            {{ formatDate(selectedResult.approved_at) }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="selectedResult.published_at"
            label="公示时间"
          >
            {{ formatDate(selectedResult.published_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h3>评分汇总说明</h3>
        <div class="summary-text">
          {{ selectedResult.summary || '暂无汇总说明' }}
        </div>

        <el-divider v-if="selectedResult.reject_reason" />

        <div v-if="selectedResult.reject_reason">
          <h3>驳回原因</h3>
          <el-alert
            :title="selectedResult.reject_reason"
            type="error"
            :closable="false"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>

    <!-- Reject Reason Dialog -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="驳回原因"
      width="600px"
    >
      <el-alert
        v-if="selectedResult"
        :title="selectedResult.reject_reason || '无驳回原因'"
        type="error"
        :closable="false"
        show-icon
      />
      <template #footer>
        <el-button @click="rejectDialogVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search,
  Refresh,
  Download,
  School,
  CircleCheck,
  TrendCharts,
  Trophy
} from '@element-plus/icons-vue'
import { managementResultApi } from '@/api/client'

// Types
interface ManagementResult {
  id: string;
  teaching_office_id: string;
  teaching_office_name: string;
  evaluation_year: number;
  final_score?: number;
  ai_score?: number;
  manual_score_avg?: number;
  approval_status: 'approved' | 'rejected' | 'pending';
  status: string;
  summary?: string;
  approved_at?: string;
  published_at?: string;
  reject_reason?: string;
}

// Router
const router = useRouter()

// State
const loading = ref(false)
const results = ref<ManagementResult[]>([])
const detailDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const selectedResult = ref<ManagementResult | null>(null)

// Filters
const filters = ref({
  year: new Date().getFullYear(),
  status: ''
})

const availableYears = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
})

// Pagination
const pagination = ref({
  currentPage: 1,
  pageSize: 20
})

// Sorting
const sortConfig = ref({
  prop: 'final_score',
  order: 'descending'
})

// Computed: Statistics
const publishedCount = computed(() => {
  return results.value.filter(r => r.status === 'published').length
})

const averageScore = computed(() => {
  const scores = results.value
    .filter(r => r.final_score !== undefined)
    .map(r => r.final_score!)
  if (scores.length === 0) return 0
  return scores.reduce((sum, score) => sum + score, 0) / scores.length
})

const highestScore = computed(() => {
  const scores = results.value
    .filter(r => r.final_score !== undefined)
    .map(r => r.final_score!)
  if (scores.length === 0) return 0
  return Math.max(...scores)
})

// Computed: Sorted results
const sortedResults = computed(() => {
  const sorted = [...results.value]
  
  if (sortConfig.value.prop && sortConfig.value.order) {
    sorted.sort((a, b) => {
      const aVal = a[sortConfig.value.prop as keyof ManagementResult]
      const bVal = b[sortConfig.value.prop as keyof ManagementResult]
      
      if (aVal === undefined || aVal === null) return 1
      if (bVal === undefined || bVal === null) return -1
      
      const comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
      return sortConfig.value.order === 'ascending' ? comparison : -comparison
    })
  }
  
  return sorted
})

// Computed: Paginated results
const paginatedResults = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return sortedResults.value.slice(start, end)
})

// Load results on mount
onMounted(async () => {
  await loadResults()
})

// Load results
const loadResults = async () => {
  loading.value = true
  try {
    // 需求 14.7: 管理端显示所有教研室最终得分
    // 需求 14.8: 管理端显示审定结果
    const response = await managementResultApi.getAllResults({
      year: filters.value.year,
      status: filters.value.status || undefined
    })
    results.value = response.data
  } catch (error: any) {
    console.error('Failed to load results:', error)
    ElMessage.error('加载考评结果失败')
    
    // Fallback to mock data for development
    results.value = [
      {
        id: '1',
        teaching_office_id: 'to1',
        teaching_office_name: '计算机科学教研室',
        evaluation_year: 2024,
        final_score: 92.5,
        ai_score: 90.0,
        manual_score_avg: 93.5,
        approval_status: 'approved',
        status: 'published',
        summary: '该教研室在教学改革、课程建设等方面表现突出，综合评分优秀。',
        approved_at: '2024-01-25T10:30:00',
        published_at: '2024-01-26T09:00:00'
      },
      {
        id: '2',
        teaching_office_id: 'to2',
        teaching_office_name: '数学教研室',
        evaluation_year: 2024,
        final_score: 88.3,
        ai_score: 87.5,
        manual_score_avg: 89.0,
        approval_status: 'approved',
        status: 'published',
        summary: '该教研室整体表现良好，建议加强教学改革项目申报。',
        approved_at: '2024-01-25T14:20:00',
        published_at: '2024-01-26T09:00:00'
      },
      {
        id: '3',
        teaching_office_id: 'to3',
        teaching_office_name: '物理教研室',
        evaluation_year: 2024,
        final_score: 90.1,
        ai_score: 89.0,
        manual_score_avg: 91.0,
        approval_status: 'approved',
        status: 'published',
        summary: '该教研室在实验教学和科研方面成绩显著。',
        approved_at: '2024-01-24T09:15:00',
        published_at: '2024-01-26T09:00:00'
      },
      {
        id: '4',
        teaching_office_id: 'to4',
        teaching_office_name: '化学教研室',
        evaluation_year: 2024,
        final_score: 85.7,
        ai_score: 84.0,
        manual_score_avg: 87.0,
        approval_status: 'approved',
        status: 'finalized',
        summary: '该教研室需要在教学质量监控方面加强工作。',
        approved_at: '2024-01-25T16:45:00'
      },
      {
        id: '5',
        teaching_office_id: 'to5',
        teaching_office_name: '英语教研室',
        evaluation_year: 2024,
        final_score: 78.5,
        ai_score: 80.0,
        manual_score_avg: 77.5,
        approval_status: 'rejected',
        status: 'finalized',
        summary: '该教研室在多个考核指标上未达标。',
        approved_at: '2024-01-25T11:20:00',
        reject_reason: '教学改革项目数量不足，荣誉表彰材料存在疑问，需要补充完善相关材料后重新提交审核。'
      }
    ]
  } finally {
    loading.value = false
  }
}

// Reset filters
const resetFilters = () => {
  filters.value = {
    year: new Date().getFullYear(),
    status: ''
  }
  loadResults()
}

// Handle sort change
const handleSortChange = ({ prop, order }: any) => {
  sortConfig.value = { prop, order }
}

// Handle page size change
const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.currentPage = 1
}

// Handle current page change
const handleCurrentChange = (page: number) => {
  pagination.value.currentPage = page
}

// View detail
const viewDetail = (result: ManagementResult) => {
  selectedResult.value = result
  detailDialogVisible.value = true
}

// View reject reason
const viewRejectReason = (result: ManagementResult) => {
  selectedResult.value = result
  rejectDialogVisible.value = true
}

// Export results
const exportResults = () => {
  ElMessage.info('导出功能开发中...')
  // TODO: Implement export functionality
}

// Get score tag type
const getScoreTagType = (score?: number): string => {
  if (!score) return 'info'
  if (score >= 90) return 'success'
  if (score >= 80) return 'warning'
  return 'danger'
}

// Get approval tag type
const getApprovalTagType = (status: string): string => {
  const types: Record<string, string> = {
    'approved': 'success',
    'rejected': 'danger',
    'pending': 'warning'
  }
  return types[status] || 'info'
}

// Get approval label
const getApprovalLabel = (status: string): string => {
  const labels: Record<string, string> = {
    'approved': '已同意',
    'rejected': '已驳回',
    'pending': '待审定'
  }
  return labels[status] || status
}

// Get status tag type
const getStatusTagType = (status: string): string => {
  const types: Record<string, string> = {
    'published': 'success',
    'finalized': 'primary',
    'approved': 'success',
    'manually_scored': 'warning'
  }
  return types[status] || 'info'
}

// Get status label
const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    'published': '已公示',
    'finalized': '已确定最终得分',
    'approved': '已审定',
    'manually_scored': '已手动评分'
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
.management-result-page {
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
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-card,
.summary-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-form {
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Statistics Overview */
.statistics-overview {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  margin-right: 15px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

/* Detail Dialog */
.detail-content {
  padding: 10px 0;
}

.summary-text {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.8;
  color: #606266;
  margin-top: 10px;
}

.detail-content h3 {
  margin: 20px 0 10px 0;
  font-size: 16px;
  color: #303133;
}
</style>
