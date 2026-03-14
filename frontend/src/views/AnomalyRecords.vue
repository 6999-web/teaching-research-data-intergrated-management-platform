<template>
  <div class="anomaly-records-page">
    <div class="page-header">
      <div class="header-row">
        <h1>处理记录</h1>
        <router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>
      </div>
      <el-breadcrumb class="management-breadcrumb" separator="/">
        <el-breadcrumb-item :to="{ path: '/management-home' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>管理端</el-breadcrumb-item>
        <el-breadcrumb-item>处理记录</el-breadcrumb-item>
      </el-breadcrumb>
      <p class="page-description">查看异常数据处理记录与处理统计（真实数据）。</p>
    </div>

    <el-tabs v-model="activeTab" class="content-tabs">
      <el-tab-pane label="处理记录" name="records">
        <el-card v-loading="loading" class="card">
          <template #header>
            <span>异常数据处理记录</span>
            <el-button :icon="Refresh" size="small" @click="loadAnomalies">刷新</el-button>
          </template>
          <el-table :data="handledList" border stripe>
            <el-table-column prop="teaching_office_name" label="教研室" width="140">
              <template #default="{ row }">{{ row.teaching_office_name || '-' }}</template>
            </el-table-column>
            <el-table-column prop="evaluation_year" label="年度" width="80" />
            <el-table-column prop="type" label="异常类型" width="120">
              <template #default="{ row }">{{ typeLabel(row.type) }}</template>
            </el-table-column>
            <el-table-column prop="indicator" label="考核指标" min-width="120" />
            <el-table-column prop="description" label="原因说明" min-width="260" show-overflow-tooltip />
            <el-table-column prop="handled_action" label="处理方式" width="100">
              <template #default="{ row }">
                <el-tag :type="row.handled_action === 'reject' ? 'warning' : 'success'">
                  {{ row.handled_action === 'reject' ? '打回' : '修正' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="handled_at" label="处理时间" width="170">
              <template #default="{ row }">{{ formatTime(row.handled_at) }}</template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && handledList.length === 0" description="暂无处理记录" />
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="处理统计" name="stats">
        <el-card v-loading="loading" class="card">
          <template #header><span>异常处理统计</span></template>
          <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
              <div class="stat-box">
                <div class="stat-value">{{ stats.total }}</div>
                <div class="stat-label">异常总数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-box warning">
                <div class="stat-value">{{ stats.pending }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-box success">
                <div class="stat-value">{{ stats.handled }}</div>
                <div class="stat-label">已处理</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-box info">
                <div class="stat-value">{{ stats.rejectCount }}</div>
                <div class="stat-label">打回数</div>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <h4>按类型分布</h4>
              <el-table :data="stats.byType" border size="small">
                <el-table-column prop="type" label="类型">
                  <template #default="{ row }">{{ typeLabel(row.type) }}</template>
                </el-table-column>
                <el-table-column prop="count" label="数量" width="80" />
              </el-table>
            </el-col>
            <el-col :span="12">
              <h4>按处理方式</h4>
              <el-table :data="stats.byAction" border size="small">
                <el-table-column prop="action" label="方式" />
                <el-table-column prop="count" label="数量" width="80" />
              </el-table>
            </el-col>
          </el-row>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh } from '@element-plus/icons-vue'
import { reviewApi } from '@/api/client'
import apiClient from '@/api/client'

const route = useRoute()
const activeTab = ref((route.query.tab as string) === 'stats' ? 'stats' : 'records')
const loading = ref(false)
const anomalies = ref<any[]>([])
const evaluationMap = ref<Record<string, { teaching_office_name?: string; evaluation_year?: number }>>({})

watch(() => route.query.tab, (tab) => { if (tab === 'stats') activeTab.value = 'stats' })

function typeLabel (t: string) {
  const m: Record<string, string> = { count_mismatch: '数量不一致', missing_attachment: '缺少附件', invalid_data: '无效数据' }
  return m[t] || t
}
function formatTime (v: string | null) {
  if (!v) return '-'
  return new Date(v).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const handledList = computed(() => {
  const list = anomalies.value.filter((a: any) => a.status === 'handled')
  return list.map((a: any) => ({
    ...a,
    teaching_office_name: evaluationMap.value[a.evaluation_id]?.teaching_office_name,
    evaluation_year: evaluationMap.value[a.evaluation_id]?.evaluation_year
  }))
})

const stats = computed(() => {
  const list = anomalies.value
  const byType: Record<string, number> = {}
  const byAction: Record<string, number> = {}
  list.forEach((a: any) => {
    byType[a.type] = (byType[a.type] || 0) + 1
    if (a.status === 'handled' && a.handled_action) {
      byAction[a.handled_action] = (byAction[a.handled_action] || 0) + 1
    }
  })
  return {
    total: list.length,
    pending: list.filter((a: any) => a.status === 'pending').length,
    handled: list.filter((a: any) => a.status === 'handled').length,
    rejectCount: list.filter((a: any) => a.handled_action === 'reject').length,
    byType: Object.entries(byType).map(([type, count]) => ({ type, count })),
    byAction: Object.entries(byAction).map(([action, count]) => ({ action: action === 'reject' ? '打回' : '修正', count }))
  }
})

async function loadAnomalies () {
  loading.value = true
  try {
    const res = await reviewApi.getAnomalies({})
    const list = (res.data as any)?.anomalies ?? []
    anomalies.value = list
    const ids = [...new Set(list.map((a: any) => a.evaluation_id))]
    for (const id of ids) {
      try {
        const r = await apiClient.get(`/teaching-office/self-evaluation/${id}`)
        const d = r.data
        evaluationMap.value[id] = {
          teaching_office_name: d.teaching_office_name ?? d.teachingOfficeName,
          evaluation_year: d.evaluation_year ?? d.evaluationYear
        }
      } catch {
        evaluationMap.value[id] = {}
      }
    }
  } catch (e) {
    console.error(e)
    anomalies.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => loadAnomalies())
</script>

<style scoped>
.anomaly-records-page { min-height: 100vh; background: #f5f7fa; padding: 20px; }
.page-header { margin-bottom: 20px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.page-header .header-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.page-header .header-row h1 { margin: 0; font-size: 24px; color: #303133; }
.page-header .el-breadcrumb { margin-bottom: 8px; }
.back-home-link { color: #409eff; text-decoration: none; font-size: 14px; }
.back-home-link:hover { text-decoration: underline; }
.page-header h1 { margin: 0 0 8px 0; font-size: 24px; color: #303133; }
.page-description { margin: 0; color: #606266; font-size: 14px; }
.content-tabs { max-width: 1200px; margin: 0 auto; }
.card { margin-bottom: 20px; }
.card .el-card__header { display: flex; justify-content: space-between; align-items: center; }
.stats-row { margin-bottom: 24px; }
.stat-box { text-align: center; padding: 20px; background: #f0f9ff; border-radius: 8px; }
.stat-box .stat-value { font-size: 28px; font-weight: 600; color: #409eff; }
.stat-box.warning .stat-value { color: #e6a23c; }
.stat-box.success .stat-value { color: #67c23a; }
.stat-box.info .stat-value { color: #909399; }
.stat-label { font-size: 13px; color: #606266; margin-top: 4px; }
h4 { margin: 16px 0 8px 0; font-size: 14px; }
</style>
