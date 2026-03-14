<template>
  <div class="anomaly-handling-view">
    <div class="page-header">
      <h1>异常数据处理</h1>
      <p class="page-description">
        查看和处理AI评分过程中检测到的<strong>评分失败/异常数据及原因</strong>，包括数量不一致、缺少附件等。
        <router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>
      </p>
    </div>

    <el-tabs v-model="activeTab" class="anomaly-tabs">
      <el-tab-pane label="异常数据列表" name="list">
        <p class="tab-desc">以下为AI标记的异常数据，包含评分失败或需人工核对的项及原因说明。</p>
        <AnomalyHandling />
      </el-tab-pane>
      <el-tab-pane label="异常分析" name="analysis">
        <div class="analysis-card" v-loading="analysisLoading">
          <h3>异常数据统计与原因分析</h3>
          <el-row :gutter="20" class="stats-row">
            <el-col :span="8">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-value">{{ analysisSummary.total }}</div>
                <div class="stat-label">异常总数</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="stat-card warning">
                <div class="stat-value">{{ analysisSummary.pending }}</div>
                <div class="stat-label">待处理</div>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card shadow="hover" class="stat-card success">
                <div class="stat-value">{{ analysisSummary.handled }}</div>
                <div class="stat-label">已处理</div>
              </el-card>
            </el-col>
          </el-row>
          <h4>按类型分布</h4>
          <el-table :data="analysisSummary.byType" border stripe size="small">
            <el-table-column prop="type" label="异常类型" width="160">
              <template #default="{ row }">{{ typeLabel(row.type) }}</template>
            </el-table-column>
            <el-table-column prop="count" label="数量" width="100" />
          </el-table>
          <h4>评分失败/异常原因汇总</h4>
          <el-table :data="analysisSummary.reasons" border stripe max-height="360">
            <el-table-column prop="indicator" label="考核指标" width="140" />
            <el-table-column prop="type" label="类型">
              <template #default="{ row }">{{ typeLabel(row.type) }}</template>
            </el-table-column>
            <el-table-column prop="description" label="原因说明" min-width="320" />
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">{{ row.status === 'pending' ? '待处理' : '已处理' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!analysisLoading && analysisSummary.reasons.length === 0" description="暂无异常数据" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AnomalyHandling from '@/components/AnomalyHandling.vue'
import { reviewApi } from '@/api/client'

const route = useRoute()
const activeTab = ref(route.query.tab === 'analysis' ? 'analysis' : 'list')
const analysisLoading = ref(false)
const analysisSummary = ref<{
  total: number
  pending: number
  handled: number
  byType: { type: string; count: number }[]
  reasons: { indicator: string; type: string; description: string; status: string }[]
}>({
  total: 0,
  pending: 0,
  handled: 0,
  byType: [],
  reasons: []
})

watch(() => route.query.tab, (tab) => {
  if (tab === 'analysis') activeTab.value = 'analysis'
})

function typeLabel (type: string) {
  const map: Record<string, string> = {
    count_mismatch: '数量不一致',
    missing_attachment: '缺少附件',
    invalid_data: '无效数据'
  }
  return map[type] || type
}

async function loadAnalysis () {
  analysisLoading.value = true
  try {
    const res = await reviewApi.getAnomalies({})
    const list = (res.data as any)?.anomalies ?? []
    const byType: Record<string, number> = {}
    const reasons = list.map((a: any) => {
      byType[a.type] = (byType[a.type] || 0) + 1
      return {
        indicator: a.indicator || '-',
        type: a.type || '-',
        description: a.description || '-',
        status: a.status || 'pending'
      }
    })
    const byTypeArr = Object.entries(byType).map(([type, count]) => ({ type, count }))
    analysisSummary.value = {
      total: list.length,
      pending: list.filter((a: any) => a.status === 'pending').length,
      handled: list.filter((a: any) => a.status === 'handled').length,
      byType: byTypeArr,
      reasons
    }
  } catch (e) {
    console.error(e)
    analysisSummary.value = { total: 0, pending: 0, handled: 0, byType: [], reasons: [] }
  } finally {
    analysisLoading.value = false
  }
}

onMounted(() => {
  if (activeTab.value === 'analysis') loadAnalysis()
})
watch(activeTab, (tab) => {
  if (tab === 'analysis') loadAnalysis()
})
</script>

<style scoped>
.anomaly-handling-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}
.page-header {
  max-width: 1400px;
  margin: 0 auto 20px;
  padding: 30px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
.page-header h1 { margin: 0 0 10px 0; font-size: 28px; color: #303133; font-weight: 600; }
.page-description { margin: 0; font-size: 14px; color: #606266; line-height: 1.6; }
.back-home-link { margin-left: 12px; color: #409eff; text-decoration: none; }
.back-home-link:hover { text-decoration: underline; }
.anomaly-tabs { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.tab-desc { margin: 0 0 16px 0; font-size: 13px; color: #909399; }
.analysis-card h3 { margin: 0 0 16px 0; font-size: 16px; }
.analysis-card h4 { margin: 20px 0 10px 0; font-size: 14px; color: #606266; }
.stats-row { margin-bottom: 20px; }
.stat-card { text-align: center; }
.stat-value { font-size: 28px; font-weight: 600; color: #409eff; }
.stat-card.warning .stat-value { color: #e6a23c; }
.stat-card.success .stat-value { color: #67c23a; }
.stat-label { font-size: 13px; color: #909399; margin-top: 4px; }
</style>
