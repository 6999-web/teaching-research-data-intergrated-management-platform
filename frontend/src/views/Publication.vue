<template>
  <div class="publication-page">
    <div class="page-header">
      <div class="header-row">
        <h1>🔔 发起公示</h1>
        <a href="#" @click.prevent="goBackToHome" class="back-home-link">← 返回主页</a>
      </div>
      <el-breadcrumb class="management-breadcrumb" separator="/">
        <el-breadcrumb-item :to="{ path: '/management-home' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>考评办公室</el-breadcrumb-item>
        <el-breadcrumb-item>发起公示</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="page-content">
      <!-- 操作工具栏 -->
      <el-card class="toolbar-card">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-tag type="info" size="large" round>
              共 {{ evaluations.length }} 条考评记录
            </el-tag>
            <el-tag v-if="selectedIds.length > 0" type="warning" size="large" round>
              已选 {{ selectedIds.length }} 条
            </el-tag>
          </div>
          <div class="toolbar-right">
            <el-button
              type="primary"
              :icon="Refresh"
              @click="loadEvaluations"
              :loading="loading"
            >刷新</el-button>
            <el-button
              type="warning"
              :icon="Upload"
              @click="handleSyncToPresident"
              :loading="isSyncing"
            >
              上传至校长办公会
            </el-button>
            <el-button
              type="success"
              :icon="Promotion"
              :disabled="selectedIds.length === 0 || isPublishing"
              :loading="isPublishing"
              @click="handlePublish"
            >
              {{ isPublishing ? '发布中...' : '确认公示并分发到教研室' }}
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 评估列表 -->
      <el-card class="main-card" v-loading="loading">
        <template #header>
          <div class="card-header">
            <h2>考评小组评分信息</h2>
            <span class="card-subtitle">选择需要公示的教研室，点击"确认公示并分发到教研室"</span>
          </div>
        </template>

        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        >
          <template #title>
            <span>📌 操作说明：</span>
          </template>
          <span>此页面显示考评小组已完成评分的教研室信息，包含手动评分明细和附件。勾选教研室后点击"确认公示并分发到教研室"，将把最终得分分发到各教研室，教研室可在"结果查看"中看到成绩。</span>
        </el-alert>

        <el-table
          ref="tableRef"
          :data="evaluations"
          stripe
          style="width: 100%"
          row-key="id"
          @selection-change="handleSelectionChange"
          :expand-row-keys="expandedRows"
          @expand-change="handleExpandChange"
        >
          <el-table-column type="selection" width="55" :selectable="isSelectable" />
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="expand-content">
                <!-- 手动评分明细 -->
                <div class="expand-section">
                  <h4 class="expand-title">📊 考评小组评分明细</h4>
                  <div v-if="row.manual_scores && row.manual_scores.length > 0">
                    <el-table :data="row.manual_scores" size="small" border>
                      <el-table-column label="评审人" prop="reviewer_name" width="140" />
                      <el-table-column label="评审角色" prop="reviewer_role" width="140">
                        <template #default="s">
                          <el-tag size="small">{{ getRoleLabel(s.row.reviewer_role) }}</el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column label="总分" width="100">
                        <template #default="s">
                          <span class="score-highlight">{{ s.row.total?.toFixed(1) ?? '-' }} 分</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="评分时间" prop="submitted_at">
                        <template #default="s">
                          {{ s.row.submitted_at ? formatDateTime(s.row.submitted_at) : '-' }}
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                  <el-empty v-else description="暂无手动评分记录" :image-size="40" />
                </div>

                <!-- 附件列表 -->
                <div class="expand-section" style="margin-top: 16px">
                  <h4 class="expand-title">📎 考评小组上传附件</h4>
                  <div v-if="row.attachments && row.attachments.length > 0">
                    <div
                      v-for="att in row.attachments"
                      :key="att.id"
                      class="attachment-item"
                    >
                      <el-icon><Document /></el-icon>
                      <a
                        href="#"
                        @click.prevent="downloadFile(att)"
                        class="att-link"
                      >{{ att.file_name }}</a>
                      <el-tag size="small" type="info" style="margin-left: 8px">
                        {{ att.indicator || '通用' }}
                      </el-tag>
                      <span class="att-date">{{ att.uploaded_at ? formatDateTime(att.uploaded_at) : '' }}</span>
                    </div>
                  </div>
                  <el-empty v-else description="暂无附件" :image-size="40" />
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="teaching_office_name" label="教研室名称" min-width="140" />
          <el-table-column prop="evaluation_year" label="考评年度" width="100" align="center" />
          <el-table-column label="当前状态" width="140" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="AI评分" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.ai_score != null" class="score-text">{{ row.ai_score.toFixed(1) }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column label="人工评分(均)" width="120" align="center">
            <template #default="{ row }">
              <span v-if="row.manual_scores && row.manual_scores.length > 0" class="score-text">
                {{ getManualAvg(row.manual_scores).toFixed(1) }}
                <small>({{ row.manual_scores.length }}人)</small>
              </span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column label="最终得分" width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.final_score != null" class="final-score">
                {{ row.final_score.toFixed(1) }} 分
              </span>
              <span v-else class="no-data">未确定</span>
            </template>
          </el-table-column>
          <el-table-column label="附件数" width="90" align="center">
            <template #default="{ row }">
              <el-badge :value="row.attachments?.length || 0" type="primary" :hidden="!row.attachments?.length">
                <el-icon size="20"><Paperclip /></el-icon>
              </el-badge>
            </template>
          </el-table-column>
          <el-table-column label="公示状态" width="140" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_distributed" type="success">已分发到教研室</el-tag>
              <el-tag v-else-if="row.is_published" type="warning">已公示(待分发)</el-tag>
              <el-tag v-else-if="row.status === 'ready_for_final'" type="primary">已提交到办公室</el-tag>
              <el-tag v-else-if="row.status === 'finalized'" type="warning">已定分(待公示)</el-tag>
              <el-tag v-else type="info">待公示</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="toggleExpand(row.id)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="evaluations.length === 0 && !loading"
          description="暂无可公示的考评记录，请等待考评小组完成评分"
          :image-size="120"
        />
      </el-card>

      <!-- 公示历史 -->
      <el-card class="history-card">
        <template #header>
          <div class="card-header">
            <h2>公示历史</h2>
            <el-button type="default" size="small" :icon="Refresh" @click="loadHistory">刷新</el-button>
          </div>
        </template>

        <el-timeline v-if="history.length > 0">
          <el-timeline-item
            v-for="pub in history"
            :key="pub.id"
            :timestamp="formatDateTime(pub.published_at)"
            placement="top"
            type="success"
            :icon="Check"
          >
            <el-card shadow="never" class="history-item-card">
              <div class="history-row">
                <el-tag type="success">已公示</el-tag>
                <span class="history-count">涉及 {{ pub.evaluation_ids?.length || 0 }} 个教研室</span>
                <el-tag v-if="pub.distributed_at" type="success" size="small">已分发到教研室</el-tag>
                <el-tag v-else type="warning" size="small">待分发</el-tag>
              </div>
              <div v-if="pub.distributed_at" class="history-detail">
                分发时间：{{ formatDateTime(pub.distributed_at) }}
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无公示历史" />
      </el-card>
    </div>

    <!-- 同步到校长端结果弹窗 -->
    <el-dialog
      v-model="syncResultVisible"
      title="已同步至校长办公会端"
      width="700px"
    >
      <div class="sync-result">
        <el-alert type="success" :closable="false" style="margin-bottom: 16px">
          {{ syncResult?.message }}
        </el-alert>
        <el-table :data="syncResult?.data || []" border size="small" max-height="400">
          <el-table-column prop="teaching_office_name" label="教研室" width="140" />
          <el-table-column prop="evaluation_year" label="年度" width="80" align="center" />
          <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="最终得分" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.final_score != null" class="final-score">{{ row.final_score.toFixed(1) }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column label="人工评分均" width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.manual_score_avg != null">{{ row.manual_score_avg.toFixed(1) }}</span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column label="评审人数" prop="manual_reviewer_count" width="90" align="center" />
          <el-table-column label="附件数" prop="attachment_count" width="80" align="center" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="syncResultVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Promotion, Refresh, Check, Document, Upload, Paperclip } from '@element-plus/icons-vue'
import { publicationApi } from '@/api/client'

const router = useRouter()
const loading = ref(false)
const isPublishing = ref(false)
const isSyncing = ref(false)
const tableRef = ref()

const evaluations = ref<any[]>([])
const selectedIds = ref<string[]>([])
const history = ref<any[]>([])
const expandedRows = ref<string[]>([])

const syncResultVisible = ref(false)
const syncResult = ref<any>(null)

const goBackToHome = () => {
  const mode = localStorage.getItem('viewMode')
  if (mode === 'role') {
    router.push('/home')
  } else {
    router.push('/management-home')
  }
}

onMounted(async () => {
  await Promise.all([loadEvaluations(), loadHistory()])
})

const loadEvaluations = async () => {
  loading.value = true
  try {
    const res = await publicationApi.getEvaluationsForPublication()
    evaluations.value = Array.isArray(res.data) ? res.data : []
  } catch (e: any) {
    console.error('Failed to load evaluations:', e)
    ElMessage.error('加载考评列表失败：' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

const loadHistory = async () => {
  try {
    const res = await publicationApi.getPublications()
    history.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('Failed to load history:', e)
  }
}

const handleSelectionChange = (rows: any[]) => {
  selectedIds.value = rows.map(r => r.id)
}

const isSelectable = (row: any) => {
  // 允许对尚未分发且处于评分后状态的记录进行选择
  // 状态包括：已手动评分、已提交至考评办公室(待定分)、已确定得分、已审定
  const canPublishStatus = ['manually_scored', 'ready_for_final', 'finalized', 'approved'].includes(row.status)
  return !row.is_distributed && canPublishStatus
}

const handlePublish = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要公示的教研室')
    return
  }

  const selectedNames = evaluations.value
    .filter(e => selectedIds.value.includes(e.id))
    .map(e => e.teaching_office_name)
    .join('、')

  try {
    await ElMessageBox.confirm(
      `确定要将以下 ${selectedIds.value.length} 个教研室的考评结果公示并分发到教研室端吗？\n\n${selectedNames}\n\n分发后，各教研室可在"结果查看"中看到自己的最终得分。`,
      '确认公示',
      {
        confirmButtonText: '确认公示',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )

    isPublishing.value = true
    try {
      const res = await publicationApi.publish({ evaluation_ids: selectedIds.value })
      ElMessage.success({
        message: res.data.message || '公示成功！',
        duration: 5000
      })
      selectedIds.value = []
      if (tableRef.value) tableRef.value.clearSelection()
      await Promise.all([loadEvaluations(), loadHistory()])
    } catch (e: any) {
      ElMessage.error({
        message: '公示失败：' + (e.response?.data?.detail || e.message),
        duration: 6000,
        showClose: true
      })
    }
  } catch {
    // 用户取消
  } finally {
    isPublishing.value = false
  }
}

const handleSyncToPresident = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要将所有已完成评分的考评信息同步到校长办公会端吗？校长可以查看各教研室的评分情况和附件。',
      '确认同步',
      {
        confirmButtonText: '确认同步',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    isSyncing.value = true
    try {
      const res = await publicationApi.syncToPresident()
      syncResult.value = res.data
      syncResultVisible.value = true
      ElMessage.success('信息已成功同步至校长办公会端')
    } catch (e: any) {
      ElMessage.error('同步失败：' + (e.response?.data?.detail || e.message))
    }
  } catch {
    // 用户取消
  } finally {
    isSyncing.value = false
  }
}

const toggleExpand = (id: string) => {
  const idx = expandedRows.value.indexOf(id)
  if (idx >= 0) {
    expandedRows.value.splice(idx, 1)
  } else {
    expandedRows.value.push(id)
  }
}

const handleExpandChange = (row: any, expanded: boolean) => {
  if (expanded) {
    if (!expandedRows.value.includes(row.id)) expandedRows.value.push(row.id)
  } else {
    expandedRows.value = expandedRows.value.filter(id => id !== row.id)
  }
}

const getManualAvg = (scores: any[]) => {
  if (!scores || scores.length === 0) return 0
  const total = scores.reduce((sum, s) => sum + (s.total || 0), 0)
  return total / scores.length
}

const downloadFile = (att: any) => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
  const token = localStorage.getItem('token')
  const url = `${baseURL}/teaching-office/attachments/${att.id}/download`
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(res => res.blob())
    .then(blob => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = att.file_name
      a.click()
    })
    .catch(() => ElMessage.error('下载失败'))
}

const getStatusType = (status: string): string => {
  const map: Record<string, string> = {
    manually_scored: 'primary',
    finalized: 'success',
    approved: 'success',
    published: 'warning',
    distributed: 'success',
    ai_scored: 'info',
    submitted: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string): string => {
  const map: Record<string, string> = {
    submitted: '已提交',
    ai_scored: 'AI已评分',
    manually_scored: '已手动评分',
    ready_for_final: '待最终确定',
    finalized: '已确定得分',
    approved: '已审定',
    published: '已公示',
    distributed: '已分发'
  }
  return map[status] || status
}

const getRoleLabel = (role: string): string => {
  const map: Record<string, string> = {
    evaluation_team: '考评小组',
    evaluation_office: '考评办公室'
  }
  return map[role] || role
}

const formatDateTime = (str: string) => {
  if (!str) return '-'
  const d = new Date(str)
  return d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>

<style scoped>
.publication-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.header-row h1 {
  margin: 0;
  font-size: 26px;
  color: #1a237e;
  font-weight: 700;
}

.back-home-link {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
  padding: 4px 12px;
  border: 1px solid #b3d8ff;
  border-radius: 16px;
  background: white;
  transition: all 0.2s;
}

.back-home-link:hover {
  background: #409eff;
  color: white;
}

.page-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar-card {
  border-radius: 12px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.main-card, .history-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.card-subtitle {
  font-size: 13px;
  color: #909399;
}

.expand-content {
  padding: 16px 24px;
  background: #fafbfc;
  border-radius: 8px;
}

.expand-section {
  margin-bottom: 8px;
}

.expand-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #606266;
  font-weight: 600;
}

.score-highlight {
  color: #e6a23c;
  font-weight: bold;
  font-size: 15px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.att-link {
  color: #409eff;
  text-decoration: none;
  font-size: 13px;
}

.att-link:hover {
  text-decoration: underline;
}

.att-date {
  font-size: 12px;
  color: #c0c4cc;
  margin-left: auto;
}

.score-text {
  color: #409eff;
  font-weight: 600;
}

.final-score {
  color: #67c23a;
  font-weight: bold;
  font-size: 15px;
}

.no-data {
  color: #c0c4cc;
  font-size: 13px;
}

.history-card {
  margin-top: 4px;
}

.history-item-card {
  background: #fafafa;
}

.history-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.history-count {
  font-size: 14px;
  color: #606266;
}

.history-detail {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.sync-result {
  padding: 4px;
}

/* 管理端面包屑 */
.management-breadcrumb {
  margin-top: 4px;
}
</style>
