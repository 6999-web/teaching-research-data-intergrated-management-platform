<template>
  <div class="scoring-progress-page">
    <div class="page-header">
      <h1>评分进度</h1>
      <p class="page-description">
        查看当前评分进度，以及<strong>还有哪些尚未评分</strong>的教研室考评表。
        <router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>
      </p>
    </div>

    <el-card v-loading="loading" class="progress-card">
      <template #header>
        <div class="card-header">
          <span>筛选</span>
          <el-select v-model="filterYear" placeholder="考评年度" clearable style="width: 140px" @change="loadData">
            <el-option v-for="y in years" :key="y" :label="`${y}年`" :value="y" />
          </el-select>
        </div>
      </template>

      <!-- 待评分：还有哪些没有评分 -->
      <div class="section">
        <h3 class="section-title">
          <el-icon class="warning-icon"><WarningFilled /></el-icon>
          待评分（尚未手动评分）
        </h3>
        <p class="section-desc">以下教研室已完成自评并已AI评分，等待评教小组进行手动评分。</p>
        <el-table :data="pendingList" border stripe>
          <el-table-column prop="teaching_office_name" label="教研室" min-width="140" />
          <el-table-column prop="evaluation_year" label="年度" width="90" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="submitted_at" label="提交时间" width="180">
            <template #default="{ row }">{{ formatTime(row.submitted_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="goManualScoring(row.id)">去评分</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && pendingList.length === 0" description="暂无待评分项" />
      </div>

      <!-- 已评分 -->
      <div class="section">
        <h3 class="section-title success">
          <el-icon><CircleCheckFilled /></el-icon>
          已手动评分
        </h3>
        <p class="section-desc">以下教研室已完成手动评分。</p>
        <el-table :data="scoredList" border stripe>
          <el-table-column prop="teaching_office_name" label="教研室" min-width="140" />
          <el-table-column prop="evaluation_year" label="年度" width="90" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="submitted_at" label="提交时间" width="180">
            <template #default="{ row }">{{ formatTime(row.submitted_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="goResult(row.id)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && scoredList.length === 0" description="暂无已评分项" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { WarningFilled, CircleCheckFilled } from '@element-plus/icons-vue'
import { scoringApi } from '@/api/client'

const router = useRouter()
const loading = ref(false)
const filterYear = ref<number | null>(null)
const allEvaluations = ref<any[]>([])

const years = computed(() => {
  const set = new Set(allEvaluations.value.map((e: any) => e.evaluation_year))
  return Array.from(set).sort((a, b) => b - a)
})

// 待评分：含「待AI评分」(submitted/locked) 与「待手动评分」(ai_scored)，展示真实数据
const pendingList = computed(() =>
  allEvaluations.value.filter((e: any) =>
    ['submitted', 'locked', 'ai_scored'].includes(e.status)
  )
)
// 已手动评分：已评或已提交到办公室
const scoredList = computed(() =>
  allEvaluations.value.filter((e: any) =>
    ['manually_scored', 'ready_for_final', 'finalized', 'published'].includes(e.status)
  )
)

// 状态文案（与手动评分页一致）：评分前、已评分、已提交
function getStatusLabel (status: string): string {
  if (!status) return '评分前'
  if (['manually_scored'].includes(status)) return '已评分'
  if (['ready_for_final', 'finalized', 'published', 'distributed'].includes(status)) return '已提交'
  return '评分前'
}
function getStatusTagType (status: string): string {
  const label = getStatusLabel(status)
  const map: Record<string, string> = { '评分前': 'warning', '已评分': 'success', '已提交': 'primary' }
  return map[label] || 'info'
}

function formatTime (v: string | null) {
  if (!v) return '-'
  return new Date(v).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadData () {
  loading.value = true
  try {
    const res = await scoringApi.getEvaluationsForScoring({ year: filterYear.value ?? undefined })
    const raw = res.data
    // 兼容数组或包装结构，确保展示真实数据
    allEvaluations.value = Array.isArray(raw) ? raw : (raw?.items ?? raw?.value ?? raw?.list ?? [])
  } catch (e) {
    console.error(e)
    allEvaluations.value = []
  } finally {
    loading.value = false
  }
}

function goManualScoring (evaluationId: string) {
  router.push({ path: '/manual-scoring', query: { evaluationId } })
}

function goResult (evaluationId: string) {
  router.push({ path: '/result/' + evaluationId })
}

onMounted(() => loadData())
const onVisibilityChange = () => {
  if (document.visibilityState === 'visible') loadData()
}
onMounted(() => document.addEventListener('visibilitychange', onVisibilityChange))
onUnmounted(() => document.removeEventListener('visibilitychange', onVisibilityChange))
</script>

<style scoped>
.scoring-progress-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}
.page-header {
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.page-header h1 { margin: 0 0 8px 0; font-size: 24px; color: #303133; }
.page-description { margin: 0; color: #606266; font-size: 14px; }
.back-home-link {
  margin-left: 12px;
  color: #409eff;
  text-decoration: none;
}
.back-home-link:hover { text-decoration: underline; }
.progress-card { max-width: 1200px; margin: 0 auto; }
.card-header { display: flex; align-items: center; gap: 12px; }
.section { margin-top: 28px; }
.section:first-of-type { margin-top: 0; }
.section-title { display: flex; align-items: center; gap: 8px; margin: 0 0 8px 0; font-size: 16px; color: #303133; }
.section-title .warning-icon { color: #e6a23c; }
.section-title.success .el-icon { color: #67c23a; }
.section-desc { margin: 0 0 12px 0; font-size: 13px; color: #909399; }
</style>
