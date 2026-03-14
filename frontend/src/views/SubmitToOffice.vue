<template>
  <div class="submit-to-office-page">
    <div class="page-header">
      <h1>提交评教数据到评教办公室</h1>
      <p class="page-description">
        将已完成手动评分的考评数据<strong>上传到评教办公室端</strong>，由评教办公室进行最终得分确定。
        <router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>
      </p>
    </div>

    <el-card v-loading="loading" class="content-card">
      <template #header>
        <div class="card-header">
          <span>筛选</span>
          <el-select v-model="filterYear" placeholder="考评年度" clearable style="width: 140px" @change="loadData">
            <el-option v-for="y in years" :key="y" :label="`${y}年`" :value="y" />
          </el-select>
          <el-button :icon="Refresh" @click="loadData">刷新</el-button>
        </div>
      </template>

      <!-- 待提交到评教办公室 -->
      <div class="section">
        <h3 class="section-title">
          <el-icon class="warning-icon"><Upload /></el-icon>
          待提交到评教办公室
        </h3>
        <p class="section-desc">以下教研室已完成评教小组手动评分且已计算平均分，可点击「提交」将该平均分及评分数据上传至评教办公室，由办公室确定最终得分。</p>
        <el-table :data="pendingSubmitList" border stripe>
          <el-table-column prop="teaching_office_name" label="教研室" min-width="140" />
          <el-table-column prop="evaluation_year" label="年度" width="90" />
          <el-table-column prop="status" label="状态" width="130">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="submitted_at" label="提交时间" width="180">
            <template #default="{ row }">{{ formatTime(row.submitted_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="160" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                :loading="submittingId === row.id"
                @click="submitOne(row)"
              >
                提交到评教办公室
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && pendingSubmitList.length === 0" description="暂无待提交项（需先完成评教小组手动评分，系统将自动计算平均分）" />
      </div>

      <!-- 已提交到评教办公室 -->
      <div class="section">
        <h3 class="section-title success">
          <el-icon><CircleCheckFilled /></el-icon>
          已提交到评教办公室
        </h3>
        <p class="section-desc">以下数据已上传至评教办公室，等待办公室确定最终得分。</p>
        <el-table :data="submittedList" border stripe>
          <el-table-column prop="teaching_office_name" label="教研室" min-width="140" />
          <el-table-column prop="evaluation_year" label="年度" width="90" />
          <el-table-column prop="status" label="状态" width="150">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="submitted_at" label="提交时间" width="180">
            <template #default="{ row }">{{ formatTime(row.submitted_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="goResult(row.id)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && submittedList.length === 0" description="暂无已提交项" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload, CircleCheckFilled, Refresh } from '@element-plus/icons-vue'
import { scoringApi } from '@/api/client'

const router = useRouter()
const loading = ref(false)
const submittingId = ref<string | null>(null)
const filterYear = ref<number | null>(null)
const allEvaluations = ref<any[]>([])

const years = computed(() => {
  const set = new Set(allEvaluations.value.map((e: any) => e.evaluation_year))
  return Array.from(set).sort((a, b) => b - a)
})

// 可提交的：仅已手动评分（评分完成后已计算评教小组平均分，方可提交到办公室）
const pendingSubmitList = computed(() =>
  allEvaluations.value.filter((e: any) => e.status === 'manually_scored')
)

// 已提交的：已提交到办公室（ready_for_final、finalized、published）
const submittedList = computed(() =>
  allEvaluations.value.filter((e: any) =>
    ['ready_for_final', 'finalized', 'published'].includes(e.status)
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
    allEvaluations.value = Array.isArray(raw) ? raw : (raw?.items ?? raw?.value ?? raw?.list ?? [])
  } catch (e) {
    console.error(e)
    ElMessage.error('加载列表失败')
    allEvaluations.value = []
  } finally {
    loading.value = false
  }
}

async function submitOne (row: { id: string; teaching_office_name?: string }) {
  const evaluationId = String(row.id)
  submittingId.value = evaluationId
  try {
    const res = await scoringApi.submitToOffice(evaluationId)
    const msg = (res as any)?.data?.message || '已成功提交到评教办公室'
    ElMessage.success(msg)
    await loadData()
  } catch (err: any) {
    const detail = err.response?.data?.detail
    const msg = (typeof detail === 'object' && detail?.message) ? detail.message : (typeof detail === 'string' ? detail : null) || '提交失败，请重试'
    ElMessage.error(msg)
  } finally {
    submittingId.value = null
  }
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
.submit-to-office-page {
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
.back-home-link { margin-left: 12px; color: #409eff; text-decoration: none; }
.back-home-link:hover { text-decoration: underline; }
.content-card { max-width: 1200px; margin: 0 auto; }
.card-header { display: flex; align-items: center; gap: 12px; }
.section { margin-top: 28px; }
.section:first-of-type { margin-top: 0; }
.section-title { display: flex; align-items: center; gap: 8px; margin: 0 0 8px 0; font-size: 16px; color: #303133; }
.section-title .warning-icon { color: #e6a23c; }
.section-title.success .el-icon { color: #67c23a; }
.section-desc { margin: 0 0 12px 0; font-size: 13px; color: #909399; }
</style>
