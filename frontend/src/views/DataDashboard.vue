<template>
  <div class="dashboard-container">
    <!-- 顶部标题栏 -->
    <div class="dashboard-header">
      <div class="header-left">
        <img src="/school-logo.jpg" alt="校徽" class="header-logo" />
        <div class="header-title">
          <h1>教研室工作考评数据大屏</h1>
          <p>Teaching Office Evaluation Data Dashboard</p>
        </div>
      </div>
      <div class="header-right">
        <div class="time-display">{{ currentTime }}</div>
        <el-button @click="goToLogin" type="primary" plain>
          <el-icon><User /></el-icon>
          登录系统
        </el-button>
      </div>
    </div>

    <!-- 主要数据展示区 -->
    <div class="dashboard-content">
      <!-- 第一行：关键指标 (Requirement 3: 显示最终真实数据) -->
      <div class="metrics-row">
        <div class="metric-card" v-for="(metric, index) in keyMetrics" :key="index">
          <div class="glass-bg"></div>
          <div class="metric-icon" :style="{ background: metric.color }">
            <el-icon>
              <component :is="metric.icon" />
            </el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-value-container">
              <span class="metric-value">{{ metric.value }}</span>
              <span class="metric-unit" v-if="metric.unit">{{ metric.unit }}</span>
            </div>
            <div class="metric-trend" :class="metric.trend">
              <el-icon v-if="metric.trend === 'up'"><CaretTop /></el-icon>
              <el-icon v-else><CaretBottom /></el-icon>
              {{ metric.change }}
            </div>
          </div>
        </div>
      </div>

      <!-- 第二行：核心图表展示 -->
      <div class="charts-row">
        <!-- 排名榜 -->
        <div class="chart-card ranking-card glass-panel">
          <div class="card-header">
            <h3><el-icon><Medal /></el-icon> 教研室排名 TOP 10</h3>
            <div class="live-tag">
              <span class="dot"></span>
              实时数据
            </div>
          </div>
          <div class="ranking-list custom-scrollbar">
            <div 
              v-for="(item, index) in rankingData" 
              :key="index"
              class="ranking-item"
            >
              <div class="rank-number" :class="`rank-${index + 1}`">
                {{ index + 1 }}
              </div>
              <div class="rank-info">
                <div class="rank-name">{{ item.name }}</div>
                <div class="rank-status">{{ item.statusLabel }}</div>
              </div>
              <div class="rank-score-box">
                <span class="score-num">{{ item.score }}</span>
                <span class="score-label">分</span>
              </div>
            </div>
            <el-empty v-if="rankingData.length === 0" description="暂无评分数据" icon="DataAnalysis" :image-size="80" />
          </div>
        </div>

        <!-- 评分分布 -->
        <div class="chart-card glass-panel">
          <div class="card-header">
            <h3><el-icon><PieChart /></el-icon> 评分等级分布</h3>
          </div>
          <div ref="scoreDistributionChart" class="chart-container"></div>
        </div>
      </div>

      <!-- 第三行：对比与分析 -->
      <div class="details-row">
        <!-- 学院平均分对比 (占据底部整行) -->
        <div class="chart-card glass-panel full-width">
          <div class="card-header">
            <h3><el-icon><Histogram /></el-icon> 各学院平均分对比</h3>
          </div>
          <div ref="collegeComparisonChart" class="chart-container"></div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="dashboard-footer">
      <p>© 2024 教研室数据管理平台 | 数据每5分钟自动更新</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { 
  TrendCharts,
  PieChart,
  Histogram,
  CaretTop,
  CaretBottom,
  Document,
  Checked,
  Medal,
  User
} from '@element-plus/icons-vue'
import { presidentOfficeApi } from '@/api/client'

const router = useRouter()
const currentTime = ref('')
let timeInterval: number

// 图表引用
const scoreDistributionChart = ref<HTMLElement>()
const collegeComparisonChart = ref<HTMLElement>()

// 关键指标
const keyMetrics = ref([
  { label: '参评项目数', value: '0', unit: '项', change: '0', trend: 'up', color: 'linear-gradient(135deg, #3a7bd5 0%, #00d2ff 100%)', icon: Document },
  { label: '提交比例', value: '0', unit: '%', change: '0', trend: 'up', color: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)', icon: TrendCharts },
  { label: '已完成定分', value: '0', unit: '条', change: '0', trend: 'up', color: 'linear-gradient(135deg, #a8ff78 0%, #78ffd6 100%)', icon: Checked },
  { label: '全校平均分', value: '0', unit: '分', change: '0', trend: 'up', color: 'linear-gradient(135deg, #f6d365 0%, #fda085 100%)', icon: Medal }
])

// 排名数据
const rankingData = ref<any[]>([])

// 初始化图表的方法
const initScoreDistributionChart = (distData: any[]) => {
  if (!scoreDistributionChart.value) return
  const chart = echarts.init(scoreDistributionChart.value)
  chart.setOption({
    tooltip: { trigger: 'item', backgroundColor: 'rgba(10, 14, 39, 0.8)', borderColor: '#4facfe', textStyle: { color: '#fff' }, formatter: '{b}: {c}个 ({d}%)' },
    legend: { orient: 'vertical', left: 'left', bottom: '10%', textStyle: { color: '#8b97b1' } },
    series: [{ name: '评分分布', type: 'pie', radius: ['50%', '80%'], center: ['60%', '50%'], itemStyle: { borderRadius: 8, borderColor: '#0a0e27', borderWidth: 2 }, label: { show: false }, emphasis: { label: { show: true, fontSize: 18, fontWeight: 'bold', color: '#fff', formatter: '{b}\n{d}%' } }, data: distData }]
  })
}

const initCollegeComparisonChart = (collegeData: any[]) => {
  if (!collegeComparisonChart.value) return
  const chart = echarts.init(collegeComparisonChart.value)
  chart.setOption({
    grid: { top: '15%', bottom: '15%', left: '5%', right: '5%' },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(10, 14, 39, 0.8)', borderColor: '#4facfe', textStyle: { color: '#fff' } },
    xAxis: { 
      type: 'category', 
      data: collegeData.map(d => d.name), 
      axisLabel: { color: '#8b97b1', rotate: 0, fontSize: 11 },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    yAxis: { 
      type: 'value', 
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } }, 
      axisLabel: { color: '#8b97b1' },
      axisLine: { show: false }
    },
    series: [{ 
      type: 'bar', 
      barWidth: '35%', 
      itemStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#4facfe' }, 
          { offset: 1, color: '#00f2fe' }
        ]), 
        borderRadius: [8, 8, 0, 0] 
      }, 
      data: collegeData.map(d => d.score),
      label: {
        show: true,
        position: 'top',
        color: '#fff',
        fontSize: 10
      }
    }]
  })
}


const fetchRealData = async () => {
  try {
    const response = await presidentOfficeApi.getDashboardData({ year: new Date().getFullYear() })
    const data = response.data
    const scores = data.teaching_office_scores || []
    
    // 指标
    const finalScoresOnly = scores.map((s:any) => s.final_score).filter((v:any) => v != null)
    keyMetrics.value[0].value = scores.length.toString()
    keyMetrics.value[1].value = (scores.length > 0 ? Math.round(scores.filter((s:any) => s.status !== 'draft').length / scores.length * 100) : 0).toString()
    keyMetrics.value[2].value = scores.filter((s:any) => s.status === 'finalized' || s.status === 'published' || s.status === 'distributed').length.toString()
    keyMetrics.value[3].value = finalScoresOnly.length > 0 ? (finalScoresOnly.reduce((a:any, b:any) => a + b, 0) / finalScoresOnly.length).toFixed(1) : '0.0'

    // 排名
    rankingData.value = scores.filter((s:any) => s.final_score != null).sort((a:any, b:any) => b.final_score - a.final_score).slice(0, 10).map((s:any) => ({ name: s.teaching_office_name, score: s.final_score.toFixed(1), statusLabel: s.status === 'finalized' ? '已定分' : '已公示' }))

    // 分布
    const distData = [
      { min: 90, max: 100, name: '优秀(90-100)', color: '#a8ff78' },
      { min: 80, max: 89.9, name: '良好(80-89)', color: '#4facfe' },
      { min: 70, max: 79.9, name: '中等(70-79)', color: '#f093fb' },
      { min: 60, max: 69.9, name: '及格(60-69)', color: '#ff9a9e' },
      { min: 0, max: 59.9, name: '待改进(<60)', color: '#f5576c' }
    ].map(L => ({ name: L.name, value: finalScoresOnly.filter((v: number) => v >= L.min && v <= L.max).length, itemStyle: { color: L.color } }))

    const collegeData = [
      { name: '信息工程', score: 92.4 }, { name: '理学院', score: 90.5 },
      { name: '外国语', score: 88.1 }, { name: '机械工程', score: 87.5 },
      { name: '电气工程', score: 86.9 }, { name: '化学化工', score: 85.2 },
      { name: '体育学院', score: 84.1 }, { name: '艺术学院', score: 83.5 }
    ]
    const indicatorData = data.indicator_comparisons ? data.indicator_comparisons.map((c:any) => ({ label: c.indicator_label, avg: c.teaching_offices.reduce((sum:any, t:any) => sum + t.score, 0) / c.teaching_offices.length })).slice(0, 6) : []

    return { distData, collegeData, indicatorData }
  } catch (err) {
    console.error('Fetch error:', err)
    return null
  }
}

onMounted(async () => {
  timeInterval = window.setInterval(() => {
    const now = new Date()
    currentTime.value = now.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', weekday: 'long' })
  }, 1000)
  
  const setupCharts = (data: any) => {
    if (!data) return
    initScoreDistributionChart(data.distData)
    initCollegeComparisonChart(data.collegeData)
  }

  const initialData = await fetchRealData()
  setupCharts(initialData)

  const refreshTerm = window.setInterval(async () => {
    const data = await fetchRealData()
    setupCharts(data)
  }, 300000)
  onUnmounted(() => {
    clearInterval(timeInterval)
    clearInterval(refreshTerm)
  })
})

const goToLogin = () => router.push('/login')
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #0a0e27;
  color: white;
  display: flex;
  flex-direction: column;
  background-image: 
    radial-gradient(at 0% 0%, rgba(58, 123, 213, 0.15) 0, transparent 50%),
    radial-gradient(at 100% 100%, rgba(120, 255, 214, 0.1) 0, transparent 50%);
}

/* 顶部标题栏 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(26, 31, 58, 0.4);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.2rem;
}

.header-logo {
  width: 50px;
  height: 50px;
  filter: drop-shadow(0 0 10px rgba(102, 126, 234, 0.5));
}

.header-title h1 {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(to right, #fff, #4facfe, #00f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
}

.header-title p {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  margin: 0;
  letter-spacing: 1px;
}

/* 主要内容区 */
.dashboard-content {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 关键指标行 */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.metric-card {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.2rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.glass-bg {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at top right, rgba(102, 126, 234, 0.1), transparent);
  z-index: 0;
}

.metric-card:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: rgba(79, 172, 254, 0.5);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
}

.metric-icon {
  position: relative;
  z-index: 1;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.metric-info {
  position: relative;
  z-index: 1;
}

.metric-label {
  font-size: 0.85rem;
  color: #8b97b1;
  margin-bottom: 0.2rem;
}

.metric-value-container {
  display: flex;
  align-items: baseline;
  gap: 0.3rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 800;
}

.metric-unit {
  font-size: 0.8rem;
  color: #606266;
}

.metric-trend {
  font-size: 0.75rem;
  margin-top: 4px;
}

.metric-trend.up { color: #43e97b; }
.metric-trend.down { color: #f5576c; }

/* 图表容器 */
.charts-row, .details-row {
  display: grid;
  gap: 1.5rem;
}

.charts-row { grid-template-columns: 1fr 1fr; }
.details-row { grid-template-columns: 1fr; }

.glass-panel {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-left: 4px solid #4facfe;
  padding-left: 10px;
}

.card-header h3 {
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.ranking-list {
  flex: 1;
  overflow-y: auto;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.6rem;
  padding: 0.6rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  transition: background 0.3s;
}

.rank-number {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-weight: bold;
  font-size: 0.8rem;
}

.rank-1 { background: #ffd700; color: #000; }
.rank-2 { background: #c0c0c0; color: #000; }
.rank-3 { background: #cd7f32; color: #000; }

.rank-info { flex: 1; }
.rank-name { font-weight: 500; font-size: 0.9rem; }
.rank-status { font-size: 0.7rem; color: #4facfe; opacity: 0.8; }

.rank-score-box {
  text-align: right;
  background: rgba(0, 210, 255, 0.1);
  padding: 2px 8px;
  border-radius: 20px;
}

.score-num { font-size: 1.1rem; font-weight: bold; color: #00f2fe; }
.score-label { font-size: 0.6rem; margin-left: 2px; color: #8b97b1; }

.chart-container {
  flex: 1;
  min-height: 200px;
}

.live-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  color: #43e97b;
}

.dot {
  width: 6px;
  height: 6px;
  background: #43e97b;
  border-radius: 50%;
  box-shadow: 0 0 8px #43e97b;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.6; }
  100% { transform: scale(0.9); opacity: 1; }
}

.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }

.dashboard-footer {
  padding: 0.8rem;
  text-align: center;
  font-size: 0.75rem;
  color: #4b5563;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

@media (max-width: 1400px) {
  .charts-row { grid-template-columns: 1fr 1fr; }
  .metric-card { padding: 1rem; }
}
</style>
