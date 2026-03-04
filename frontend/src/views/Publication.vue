<template>
  <div class="publication-page">
    <div class="page-header">
      <h1>发起公示</h1>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">
          首页
        </el-breadcrumb-item>
        <el-breadcrumb-item>管理端</el-breadcrumb-item>
        <el-breadcrumb-item>发起公示</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="page-content">
      <!-- Evaluation Selection Card -->
      <el-card class="selection-card">
        <template #header>
          <div class="card-header">
            <h2>选择待公示的教研室</h2>
            <el-button
              type="success"
              :disabled="selectedEvaluationIds.length === 0 || isPublishing"
              :loading="isPublishing"
              @click="handlePublish"
            >
              <el-icon v-if="!isPublishing">
                <Promotion />
              </el-icon>
              {{ isPublishing ? '发起中...' : '发起公示' }}
            </el-button>
          </div>
        </template>

        <el-alert
          title="提示"
          type="info"
          :closable="false"
          style="margin-bottom: 15px"
        >
          仅显示已通过校长办公会审定同意的教研室。选择需要公示的教研室后，点击"发起公示"按钮启动公示流程。
        </el-alert>

        <!-- Evaluation Table -->
        <el-table
          ref="evaluationTableRef"
          v-loading="loading"
          :data="evaluations"
          stripe
          style="width: 100%"
          class="evaluation-table"
          @selection-change="handleSelectionChange"
        >
          <el-table-column
            type="selection"
            width="55"
            :selectable="isRowSelectable"
          />
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
              <el-tag :type="getStatusTagType(scope.row.status)">
                {{ getStatusLabel(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="final_score"
            label="最终得分"
            width="120"
          >
            <template #default="scope">
              <span
                v-if="scope.row.final_score !== undefined"
                class="final-score"
              >
                {{ scope.row.final_score.toFixed(1) }}分
              </span>
              <span
                v-else
                class="no-score"
              >-</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="approved_at"
            label="审定时间"
            width="180"
          >
            <template #default="scope">
              {{ scope.row.approved_at ? formatDate(scope.row.approved_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column
            label="公示状态"
            width="150"
          >
            <template #default="scope">
              <el-tag
                v-if="scope.row.status === 'published'"
                type="success"
              >
                已公示
              </el-tag>
              <el-tag
                v-else
                type="info"
              >
                未公示
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="evaluations.length === 0 && !loading"
          description="暂无可公示的教研室"
        />

        <!-- Selection Summary -->
        <div
          v-if="selectedEvaluationIds.length > 0"
          class="selection-summary"
        >
          <el-alert
            :title="`已选择 ${selectedEvaluationIds.length} 个教研室`"
            type="info"
            :closable="false"
          >
            <template #default>
              <div class="selected-list">
                <span
                  v-for="evaluation in selectedEvaluations"
                  :key="evaluation.id"
                  class="selected-item"
                >
                  {{ evaluation.teaching_office_name }}
                </span>
              </div>
            </template>
          </el-alert>
        </div>
      </el-card>

      <!-- Publication History Card -->
      <el-card class="history-card">
        <template #header>
          <div class="card-header">
            <h2>公示历史</h2>
            <el-button
              type="default"
              size="small"
              :icon="Refresh"
              @click="loadPublicationHistory"
            >
              刷新
            </el-button>
          </div>
        </template>

        <el-timeline v-if="publicationHistory.length > 0">
          <el-timeline-item
            v-for="publication in publicationHistory"
            :key="publication.id"
            :timestamp="formatDateTime(publication.published_at)"
            placement="top"
            type="success"
            :icon="Check"
          >
            <el-card>
              <div class="history-item">
                <div class="history-header">
                  <el-tag type="success">
                    已公示
                  </el-tag>
                  <span class="publication-id">公示ID: {{ publication.id }}</span>
                </div>
                <div class="history-content">
                  <div class="history-detail">
                    <span class="label">公示教研室数量：</span>
                    <span class="value">{{ publication.evaluation_ids.length }}个</span>
                  </div>
                  <div
                    v-if="publication.distributed_at"
                    class="history-detail"
                  >
                    <span class="label">分发时间：</span>
                    <span class="value">{{ formatDateTime(publication.distributed_at) }}</span>
                  </div>
                  <div
                    v-else
                    class="history-detail"
                  >
                    <span class="label">分发状态：</span>
                    <el-tag
                      type="warning"
                      size="small"
                    >
                      待分发
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-empty
          v-else
          description="暂无公示历史"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Promotion, Refresh, Check } from '@element-plus/icons-vue'
import { publicationApi } from '@/api/client'
import type { EvaluationForPublication, PublicationDetail, PublishRequest } from '@/types/publication'

// State
const loading = ref(false)
const isPublishing = ref(false)
const evaluations = ref<EvaluationForPublication[]>([])
const selectedEvaluationIds = ref<string[]>([])
const evaluationTableRef = ref()

// Publication history
const publicationHistory = ref<PublicationDetail[]>([])

// Computed: Selected evaluations
const selectedEvaluations = computed(() => {
  return evaluations.value.filter(e => selectedEvaluationIds.value.includes(e.id))
})

// Load evaluations on mount
onMounted(async () => {
  await loadEvaluations()
  await loadPublicationHistory()
})

// Load evaluations
const loadEvaluations = async () => {
  loading.value = true
  try {
    // Mock data - Replace with actual API call when backend endpoint is ready
    // In real implementation: const response = await publicationApi.getEvaluationsForPublication()
    evaluations.value = [
      {
        id: '1',
        teaching_office_name: '计算机科学教研室',
        evaluation_year: 2024,
        status: 'approved',
        final_score: 92.5,
        approved_at: '2024-01-25T10:30:00'
      },
      {
        id: '2',
        teaching_office_name: '数学教研室',
        evaluation_year: 2024,
        status: 'approved',
        final_score: 88.3,
        approved_at: '2024-01-25T14:20:00'
      },
      {
        id: '3',
        teaching_office_name: '物理教研室',
        evaluation_year: 2024,
        status: 'published',
        final_score: 90.1,
        approved_at: '2024-01-24T09:15:00'
      }
    ]
  } catch (error: any) {
    console.error('Failed to load evaluations:', error)
    ElMessage.error('加载教研室列表失败')
  } finally {
    loading.value = false
  }
}

// Load publication history
const loadPublicationHistory = async () => {
  try {
    const response = await publicationApi.getPublications()
    publicationHistory.value = response.data
  } catch (error: any) {
    console.error('Failed to load publication history:', error)
    // Don't show error message for history loading failure
  }
}

// Handle selection change
const handleSelectionChange = (selection: EvaluationForPublication[]) => {
  selectedEvaluationIds.value = selection.map(e => e.id)
}

// Check if row is selectable
const isRowSelectable = (row: EvaluationForPublication) => {
  // Only approved and not published evaluations can be selected
  // 需求 13.1: 仅在校长办公会审定同意后显示"发起公示"按钮
  return row.status === 'approved'
}

// Handle publish
const handlePublish = async () => {
  if (selectedEvaluationIds.value.length === 0) {
    ElMessage.warning('请至少选择一个教研室')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要发起公示吗？选中的 ${selectedEvaluationIds.value.length} 个教研室的考评结果将向全体教研室公开。`,
      '确认发起公示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Start publishing
    // 需求 13.2: 考评办公室点击"发起公示"按钮时，系统启动公示流程
    isPublishing.value = true

    try {
      const request: PublishRequest = {
        evaluation_ids: selectedEvaluationIds.value
      }
      
      const response = await publicationApi.publish(request)

      // 需求 13.4: 公示启动时显示成功提示
      ElMessage.success({
        message: response.data.message || '公示已成功发起！',
        duration: 3000
      })

      // Clear selection
      selectedEvaluationIds.value = []
      if (evaluationTableRef.value) {
        evaluationTableRef.value.clearSelection()
      }

      // Reload data
      setTimeout(async () => {
        await loadEvaluations()
        await loadPublicationHistory()
      }, 1000)

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '发起公示失败，请稍后重试'

      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    }

  } catch (error) {
    // User cancelled
    console.log('User cancelled publication')
  } finally {
    isPublishing.value = false
  }
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
    'approved': 'success',
    'rejected_by_president': 'danger',
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
    'approved': '已审定同意',
    'rejected_by_president': '已驳回',
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
const formatDateTime = (dateStr: string): string => {
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
.publication-page {
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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.selection-card,
.history-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
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

.evaluation-table {
  margin-top: 20px;
}

.final-score {
  color: #f56c6c;
  font-weight: bold;
}

.no-score {
  color: #909399;
}

.selection-summary {
  margin-top: 20px;
}

.selected-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.selected-item {
  padding: 4px 12px;
  background-color: #f0f9ff;
  border: 1px solid #b3e19d;
  border-radius: 4px;
  color: #67c23a;
  font-size: 14px;
}

.history-card h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.history-item {
  padding: 10px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.publication-id {
  font-size: 12px;
  color: #909399;
}

.history-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-detail {
  display: flex;
  align-items: center;
}

.history-detail .label {
  font-weight: 600;
  color: #606266;
  margin-right: 8px;
}

.history-detail .value {
  color: #303133;
}
</style>
