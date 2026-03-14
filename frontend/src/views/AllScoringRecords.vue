<template>
  <div class="all-scoring-records-page">
    <div class="page-header">
      <div class="header-row">
        <h1>全部评分</h1>
        <router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>
      </div>
      <el-breadcrumb class="management-breadcrumb" separator="/">
        <el-breadcrumb-item :to="{ path: '/management-home' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>管理端</el-breadcrumb-item>
        <el-breadcrumb-item>全部评分</el-breadcrumb-item>
      </el-breadcrumb>
      <p class="page-description">查看所有评审人打分记录，支持真实数据流通与评分对比。</p>
    </div>

    <el-tabs v-model="activeTab" class="content-tabs">
      <el-tab-pane label="全部评分记录" name="list">
        <el-card v-loading="loading" class="card">
          <template #header>
            <span>所有评审人打分记录</span>
            <el-button :icon="Refresh" size="small" @click="loadAudit">刷新</el-button>
          </template>
          <el-table :data="auditRecords" border stripe>
            <el-table-column prop="teaching_office_name" label="教研室" min-width="130" />
            <el-table-column prop="evaluation_year" label="年度" width="80" />
            <el-table-column prop="score_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.score_type === 'manual_score'" type="primary">手动评分</el-tag>
                <el-tag v-else-if="row.score_type === 'ai_score'" type="info">AI评分</el-tag>
                <el-tag v-else type="success">最终得分</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score_value" label="得分" width="90">
              <template #default="{ row }">{{ row.score_value != null ? Number(row.score_value).toFixed(1) : '-' }}</template>
            </el-table-column>
            <el-table-column prop="reviewer_name" label="评审人" width="100" />
            <el-table-column prop="created_at" label="时间" width="170">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="showDetail(row)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && auditRecords.length === 0" description="暂无评分记录" />
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="评分对比" name="compare">
        <el-card v-loading="compareLoading" class="card">
          <template #header><span>同一考评下多评审人评分对比</span></template>
          <el-form inline class="compare-form">
            <el-form-item label="选择考评">
              <el-select v-model="selectedEvalId" placeholder="请选择教研室考评" filterable style="width: 280px" @change="loadCompare">
                <el-option v-for="item in evaluationOptions" :key="item.evaluation_id" :label="`${item.teaching_office_name}（${item.evaluation_year}年）`" :value="item.evaluation_id" />
              </el-select>
            </el-form-item>
          </el-form>
          <div v-if="compareData" class="compare-table-wrap">
            <el-table :data="compareData.rows" border stripe max-height="400">
              <el-table-column prop="indicator" label="考核指标" min-width="140" fixed />
              <el-table-column v-for="r in compareData.reviewers" :key="r.name" :label="r.name" width="100">
                <template #default="{ row }">{{ row[r.name] != null ? Number(row[r.name]).toFixed(1) : '-' }}</template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-else-if="!compareLoading && !selectedEvalId" description="请先选择一条考评" />
          <el-empty v-else-if="!compareLoading && selectedEvalId && (!compareData || compareData.rows.length === 0)" description="该考评暂无多评审人数据可对比" />
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-drawer v-model="detailVisible" title="评分详情" size="480" direction="rtl">
      <div v-if="detailLoading" class="detail-loading"><el-icon class="is-loading"><Loading /></el-icon> 加载中...</div>
      <div v-else-if="detailData" class="detail-content">
        <p><strong>教研室：</strong>{{ detailData.teaching_office_name }}</p>
        <p><strong>年度：</strong>{{ detailData.evaluation_year }}</p>
        <el-divider />
        <h4>各指标得分</h4>
        <el-table :data="detailData.indicatorScores" border size="small">
          <el-table-column prop="indicator" label="指标" min-width="140" />
          <el-table-column prop="score" label="得分" width="80" />
        </el-table>
        <p v-if="detailData.aiScore != null" class="mt"><strong>AI 得分：</strong>{{ detailData.aiScore }}</p>
        <p v-if="detailData.finalScore != null" class="mt"><strong>最终得分：</strong>{{ detailData.finalScore }}</p>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh, Loading } from '@element-plus/icons-vue'
import { scoringApi } from '@/api/client'

const route = useRoute()
const activeTab = ref((route.query.tab as string) === 'compare' ? 'compare' : 'list')
const loading = ref(false)
const compareLoading = ref(false)
const auditRecords = ref<any[]>([])
const evaluationOptions = ref<{ evaluation_id: string; teaching_office_name: string; evaluation_year: number }[]>([])
const selectedEvalId = ref('')
const compareData = ref<{ reviewers: { name: string }[]; rows: Record<string, any>[] } | null>(null)
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref<{ teaching_office_name: string; evaluation_year: number; indicatorScores: { indicator: string; score: number }[]; aiScore?: number; finalScore?: number } | null>(null)

watch(() => route.query.tab, (tab) => { if (tab === 'compare') activeTab.value = 'compare' })

function formatTime (v: string | null) {
  if (!v) return '-'
  return new Date(v).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadAudit () {
  loading.value = true
  try {
    const res = await scoringApi.getScoringAudit({})
    auditRecords.value = (res.data as any)?.records ?? []
    const seen = new Map<string, { teaching_office_name: string; evaluation_year: number }>()
    auditRecords.value.forEach((r: any) => {
      if (r.evaluation_id && !seen.has(r.evaluation_id)) {
        seen.set(r.evaluation_id, { teaching_office_name: r.teaching_office_name || '-', evaluation_year: r.evaluation_year })
      }
    })
    evaluationOptions.value = Array.from(seen.entries()).map(([evaluation_id, o]) => ({ evaluation_id, ...o }))
  } catch (e) {
    console.error(e)
    auditRecords.value = []
    evaluationOptions.value = []
  } finally {
    loading.value = false
  }
}

async function loadCompare () {
  if (!selectedEvalId.value) { compareData.value = null; return }
  compareLoading.value = true
  compareData.value = null
  try {
    const res = await scoringApi.getAllScores(selectedEvalId.value)
    const data = res.data as any
    const manualScores = data?.manual_scores ?? []
    if (manualScores.length < 2) {
      compareLoading.value = false
      return
    }
    const reviewers = manualScores.map((m: any) => ({ name: m.reviewer_name || m.reviewer_id || '未知' }))
    const indicatorSet = new Set<string>()
    manualScores.forEach((m: any) => {
      (m.scores || []).forEach((s: any) => indicatorSet.add(s.indicator || ''))
    })
    const indicators = Array.from(indicatorSet).filter(Boolean)
    const rows = indicators.map(indicator => {
      const row: Record<string, any> = { indicator }
      manualScores.forEach((m: any, idx: number) => {
        const name = reviewers[idx].name
        const s = (m.scores || []).find((x: any) => (x.indicator || '') === indicator)
        row[name] = s?.score ?? null
      })
      return row
    })
    compareData.value = { reviewers, rows }
  } catch (e) {
    console.error(e)
  } finally {
    compareLoading.value = false
  }
}

async function showDetail (row: any) {
  detailVisible.value = true
  detailData.value = null
  detailLoading.value = true
  try {
    const res = await scoringApi.getAllScores(row.evaluation_id)
    const data = res.data as any
    const manualDetails = data?.manual_scores ?? []
    let indicatorScores: { indicator: string; score: number }[] = []
    if (manualDetails.length) {
      const first = manualDetails[0]
      ;(first.scores || []).forEach((s: any) => {
        indicatorScores.push({ indicator: s.indicator || '-', score: Number(s.score) || 0 })
      })
    }
    detailData.value = {
      teaching_office_name: row.teaching_office_name || '-',
      evaluation_year: row.evaluation_year || new Date().getFullYear(),
      indicatorScores,
      aiScore: data?.ai_score?.total_score != null ? Number(data.ai_score.total_score) : undefined,
      finalScore: data?.final_score?.final_score != null ? Number(data.final_score.final_score) : undefined
    }
  } catch (e) {
    console.error(e)
  } finally {
    detailLoading.value = false
  }
}

onMounted(() => {
  loadAudit()
  if (activeTab.value === 'compare' && selectedEvalId.value) loadCompare()
})
watch(activeTab, (tab) => {
  if (tab === 'compare' && evaluationOptions.value.length === 0) loadAudit()
})
</script>

<style scoped>
.all-scoring-records-page { min-height: 100vh; background: #f5f7fa; padding: 20px; }
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
.compare-form { margin-bottom: 16px; }
.compare-table-wrap { margin-top: 12px; }
.detail-loading { padding: 20px; text-align: center; color: #909399; }
.detail-content { padding: 0 8px; }
.detail-content h4 { margin: 12px 0 8px 0; font-size: 14px; }
.mt { margin-top: 12px; }
</style>
