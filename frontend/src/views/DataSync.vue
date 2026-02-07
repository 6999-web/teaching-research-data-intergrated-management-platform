<template>
  <div class="data-sync-page">
    <div class="page-header">
      <h1>数据同步至校长办公会</h1>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">
          首页
        </el-breadcrumb-item>
        <el-breadcrumb-item>管理端</el-breadcrumb-item>
        <el-breadcrumb-item>数据同步</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="page-content">
      <!-- Evaluation Selection Card -->
      <el-card class="selection-card">
        <template #header>
          <div class="card-header">
            <h2>选择待上传的教研室</h2>
            <el-button
              type="primary"
              :disabled="selectedEvaluationIds.length === 0 || isSyncing"
              :loading="isSyncing"
              @click="handleSyncToPresidentOffice"
            >
              <el-icon v-if="!isSyncing">
                <Upload />
              </el-icon>
              {{ isSyncing ? '上传中...' : '上传至校长办公会' }}
            </el-button>
          </div>
        </template>

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
            prop="finalized_at"
            label="确定时间"
            width="180"
          >
            <template #default="scope">
              {{ scope.row.finalized_at ? formatDate(scope.row.finalized_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column
            label="同步状态"
            width="150"
          >
            <template #default="scope">
              <el-tag
                v-if="scope.row.synced"
                type="success"
              >
                已同步
              </el-tag>
              <el-tag
                v-else
                type="info"
              >
                未同步
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="evaluations.length === 0 && !loading"
          description="暂无可上传的教研室"
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

      <!-- Sync Progress Card -->
      <el-card
        v-if="syncProgress.visible"
        class="progress-card"
      >
        <template #header>
          <h2>同步进度</h2>
        </template>

        <div class="progress-content">
          <el-progress
            :percentage="syncProgress.percentage"
            :status="syncProgress.status"
            :stroke-width="20"
          />
          <div class="progress-text">
            {{ syncProgress.message }}
          </div>
        </div>
      </el-card>

      <!-- Sync History Card -->
      <el-card class="history-card">
        <template #header>
          <div class="card-header">
            <h2>同步历史</h2>
            <el-button
              type="default"
              size="small"
              :icon="Refresh"
              @click="loadSyncHistory"
            >
              刷新
            </el-button>
          </div>
        </template>

        <el-timeline v-if="syncHistory.length > 0">
          <el-timeline-item
            v-for="task in syncHistory"
            :key="task.id"
            :timestamp="formatDateTime(task.created_at)"
            placement="top"
            :type="getTimelineType(task.status)"
            :icon="getTimelineIcon(task.status)"
          >
            <el-card>
              <div class="history-item">
                <div class="history-header">
                  <el-tag :type="getSyncStatusTagType(task.status)">
                    {{ getSyncStatusLabel(task.status) }}
                  </el-tag>
                  <span class="task-id">任务ID: {{ task.id }}</span>
                </div>
                <div class="history-content">
                  <div class="history-detail">
                    <span class="label">同步教研室数量：</span>
                    <span class="value">{{ task.evaluation_ids.length }}个</span>
                  </div>
                  <div
                    v-if="task.completed_at"
                    class="history-detail"
                  >
                    <span class="label">完成时间：</span>
                    <span class="value">{{ formatDateTime(task.completed_at) }}</span>
                  </div>
                  <div
                    v-if="task.error_message"
                    class="history-detail error"
                  >
                    <span class="label">错误信息：</span>
                    <span class="value">{{ task.error_message }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-empty
          v-else
          description="暂无同步历史"
        />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh, Check, Close, Loading as LoadingIcon } from '@element-plus/icons-vue'
import { reviewApi } from '@/api/client'
import type { EvaluationForSync, SyncTask, SyncTaskStatus } from '@/types/sync'

// State
const loading = ref(false)
const isSyncing = ref(false)
const evaluations = ref<EvaluationForSync[]>([])
const selectedEvaluationIds = ref<string[]>([])
const evaluationTableRef = ref()

// Sync progress state
const syncProgress = ref({
  visible: false,
  percentage: 0,
  status: '' as 'success' | 'exception' | 'warning' | '',
  message: ''
})

// Sync history
const syncHistory = ref<SyncTask[]>([])

// Computed: Selected evaluations
const selectedEvaluations = computed(() => {
  return evaluations.value.filter(e => selectedEvaluationIds.value.includes(e.id))
})

// Load evaluations on mount
onMounted(async () => {
  await loadEvaluations()
  await loadSyncHistory()
})

// Load evaluations
const loadEvaluations = async () => {
  loading.value = true
  try {
    // Mock data - Replace with actual API call
    // In real implementation: const response = await reviewApi.getEvaluationsForSync()
    evaluations.value = [
      {
        id: '1',
        teaching_office_name: '计算机科学教研室',
        evaluation_year: 2024,
        status: 'finalized',
        final_score: 92.5,
        finalized_at: '2024-01-20T10:30:00',
        synced: false
      },
      {
        id: '2',
        teaching_office_name: '数学教研室',
        evaluation_year: 2024,
        status: 'finalized',
        final_score: 88.3,
        finalized_at: '2024-01-21T14:20:00',
        synced: false
      },
      {
        id: '3',
        teaching_office_name: '物理教研室',
        evaluation_year: 2024,
        status: 'finalized',
        final_score: 90.1,
        finalized_at: '2024-01-22T09:15:00',
        synced: true
      }
    ]
  } catch (error: any) {
    console.error('Failed to load evaluations:', error)
    ElMessage.error('加载教研室列表失败')
  } finally {
    loading.value = false
  }
}

// Load sync history
const loadSyncHistory = async () => {
  try {
    // Mock data - Replace with actual API call
    // In real implementation: const response = await reviewApi.getSyncHistory()
    syncHistory.value = [
      {
        id: 'sync-001',
        evaluation_ids: ['3'],
        status: 'completed',
        created_at: '2024-01-22T10:00:00',
        completed_at: '2024-01-22T10:02:30'
      },
      {
        id: 'sync-002',
        evaluation_ids: ['4', '5'],
        status: 'failed',
        created_at: '2024-01-21T15:30:00',
        error_message: '网络连接超时'
      }
    ]
  } catch (error: any) {
    console.error('Failed to load sync history:', error)
  }
}

// Handle selection change
const handleSelectionChange = (selection: EvaluationForSync[]) => {
  selectedEvaluationIds.value = selection.map(e => e.id)
}

// Check if row is selectable
const isRowSelectable = (row: EvaluationForSync) => {
  // Only finalized and not synced evaluations can be selected
  return row.status === 'finalized' && !row.synced
}

// Handle sync to president office
const handleSyncToPresidentOffice = async () => {
  if (selectedEvaluationIds.value.length === 0) {
    ElMessage.warning('请至少选择一个教研室')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要将选中的 ${selectedEvaluationIds.value.length} 个教研室的考评数据上传至校长办公会吗？`,
      '确认上传',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // Start syncing
    isSyncing.value = true
    syncProgress.value = {
      visible: true,
      percentage: 0,
      status: '',
      message: '正在准备上传数据...'
    }

    // Simulate progress
    const progressInterval = setInterval(() => {
      if (syncProgress.value.percentage < 90) {
        syncProgress.value.percentage += 10
        syncProgress.value.message = `正在上传数据... ${syncProgress.value.percentage}%`
      }
    }, 300)

    try {
      // Call API to sync
      const response = await reviewApi.syncToPresidentOffice(selectedEvaluationIds.value)

      // Clear progress interval
      clearInterval(progressInterval)

      // Update progress to 100%
      syncProgress.value.percentage = 100
      syncProgress.value.status = 'success'
      syncProgress.value.message = '数据上传成功！'

      ElMessage.success({
        message: '数据已成功上传至校长办公会',
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
        await loadSyncHistory()
        
        // Hide progress after reload
        setTimeout(() => {
          syncProgress.value.visible = false
        }, 2000)
      }, 1500)

    } catch (error: any) {
      // Clear progress interval
      clearInterval(progressInterval)

      // Update progress to error state
      syncProgress.value.percentage = 100
      syncProgress.value.status = 'exception'
      syncProgress.value.message = '数据上传失败'

      const errorMessage = error.response?.data?.detail || '上传数据失败，请稍后重试'

      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })

      // Hide progress after delay
      setTimeout(() => {
        syncProgress.value.visible = false
      }, 3000)
    }

  } catch (error) {
    // User cancelled
    console.log('User cancelled sync')
  } finally {
    isSyncing.value = false
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

// Get sync status tag type
const getSyncStatusTagType = (status: SyncTaskStatus): string => {
  const types: Record<SyncTaskStatus, string> = {
    'pending': 'info',
    'syncing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

// Get sync status label
const getSyncStatusLabel = (status: SyncTaskStatus): string => {
  const labels: Record<SyncTaskStatus, string> = {
    'pending': '等待中',
    'syncing': '同步中',
    'completed': '已完成',
    'failed': '失败'
  }
  return labels[status] || status
}

// Get timeline type
const getTimelineType = (status: SyncTaskStatus): string => {
  const types: Record<SyncTaskStatus, string> = {
    'pending': 'primary',
    'syncing': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'primary'
}

// Get timeline icon
const getTimelineIcon = (status: SyncTaskStatus) => {
  const icons: Record<SyncTaskStatus, any> = {
    'pending': LoadingIcon,
    'syncing': LoadingIcon,
    'completed': Check,
    'failed': Close
  }
  return icons[status] || LoadingIcon
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
.data-sync-page {
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
.progress-card,
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
  background-color: #ecf5ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  color: #409eff;
  font-size: 14px;
}

.progress-card {
  border: 2px solid #409eff;
}

.progress-content {
  padding: 20px;
}

.progress-text {
  margin-top: 15px;
  text-align: center;
  font-size: 16px;
  color: #606266;
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

.task-id {
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

.history-detail.error .value {
  color: #f56c6c;
}
</style>
