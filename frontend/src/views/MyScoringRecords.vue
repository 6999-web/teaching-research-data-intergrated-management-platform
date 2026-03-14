<template>
  <div class="my-scoring-records-page">
    <div class="page-header">
      <h1>我的评分记录</h1>
      <p class="page-description">
        查看本人提交的评分记录及每次评分的详细信息（真实可流通数据）。
        <router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>
      </p>
    </div>

    <el-card v-loading="loading" class="records-card">
      <template #header>
        <div class="card-header">
          <span>评分记录列表</span>
          <el-button :icon="Refresh" @click="loadRecords">刷新</el-button>
        </div>
      </template>

      <el-table :data="records" border stripe @row-click="handleRowClick">
        <el-table-column prop="teaching_office_name" label="教研室" min-width="140" />
        <el-table-column prop="evaluation_year" label="年度" width="90" />
        <el-table-column prop="score_type" label="类型" width="110">
          <template #default="{ row }">
            <el-tag v-if="row.score_type === 'manual_score'" type="primary">手动评分</el-tag>
            <el-tag v-else-if="row.score_type === 'ai_score'" type="info">AI评分</el-tag>
            <el-tag v-else type="success">最终得分</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score_value" label="得分" width="90">
          <template #default="{ row }">
            {{ row.score_value != null ? Number(row.score_value).toFixed(1) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="reviewer_name" label="评审人" width="100" />
        <el-table-column prop="created_at" label="时间" width="170">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.score_type === 'manual_score' || row.score_type === 'final_score'" type="primary" link @click.stop="showDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && records.length === 0" description="暂无评分记录" />
    </el-card>

    <!-- 评分详情抽屉 -->
    <el-drawer v-model="detailVisible" title="评分详情" size="480" direction="rtl">
      <div v-if="detailLoading" class="detail-loading"><el-icon class="is-loading"><Loading /></el-icon> 加载中...</div>
      <div v-else-if="detailData" class="detail-content">
        <p><strong>教研室：</strong>{{ detailData.teachingOfficeName }}</p>
        <p><strong>考评年度：</strong>{{ detailData.evaluationYear }}</p>
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Refresh, Loading } from '@element-plus/icons-vue'
import { scoringApi } from '@/api/client'

const authStore = useAuthStore()
const loading = ref(false)
const records = ref<any[]>([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref<{
  teachingOfficeName: string
  evaluationYear: number
  indicatorScores: { indicator: string; score: number }[]
  aiScore?: number
  finalScore?: number
} | null>(null)

function formatTime (v: string | null) {
  if (!v) return '-'
  return new Date(v).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadRecords () {
  loading.value = true
  try {
    const userId = authStore.userId || localStorage.getItem('userId')
    const res = await scoringApi.getScoringAudit({ reviewer_id: userId || undefined })
    const list = (res.data as any)?.records ?? []
    records.value = list.filter((r: any) => r.score_type === 'manual_score' || r.score_type === 'final_score')
  } catch (e) {
    console.error(e)
    records.value = []
  } finally {
    loading.value = false
  }
}

function handleRowClick (row: any) {
  if (row.score_type === 'manual_score' || row.score_type === 'final_score') showDetail(row)
}

async function showDetail (row: any) {
  detailVisible.value = true
  detailData.value = null
  detailLoading.value = true
  try {
    const res = await scoringApi.getAllScores(row.evaluation_id)
    const data = res.data as any
    const manualDetails = data?.manual_scores ?? []
    const indicatorScores: { indicator: string; score: number }[] = []
    let teachingOfficeName = row.teaching_office_name || ''
    let evaluationYear = row.evaluation_year || new Date().getFullYear()
    if (manualDetails.length) {
      const first = manualDetails[0]
      if (first.scores && Array.isArray(first.scores)) {
        first.scores.forEach((s: any) => {
          indicatorScores.push({ indicator: s.indicator || s.indicator_name || '-', score: Number(s.score) || 0 })
        })
      }
    }
    detailData.value = {
      teachingOfficeName,
      evaluationYear,
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

onMounted(() => loadRecords())
</script>

<style scoped>
.my-scoring-records-page { min-height: 100vh; background: #f5f7fa; padding: 20px; }
.page-header { margin-bottom: 20px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.page-header h1 { margin: 0 0 8px 0; font-size: 24px; color: #303133; }
.page-description { margin: 0; color: #606266; font-size: 14px; }
.back-home-link { margin-left: 12px; color: #409eff; text-decoration: none; }
.back-home-link:hover { text-decoration: underline; }
.records-card { max-width: 1100px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.detail-loading { padding: 20px; text-align: center; color: #909399; }
.detail-content { padding: 0 8px; }
.detail-content h4 { margin: 12px 0 8px 0; font-size: 14px; }
.mt { margin-top: 12px; }
</style>
