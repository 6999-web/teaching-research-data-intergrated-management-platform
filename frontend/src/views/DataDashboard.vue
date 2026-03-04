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
      <!-- 第一行：关键指标 -->
      <div class="metrics-row">
        <div class="metric-card" v-for="(metric, index) in keyMetrics" :key="index">
          <div class="metric-icon" :style="{ background: metric.color }">
            <el-icon>
              <component :is="metric.icon" />
            </el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-value">{{ metric.value }}</div>
            <div class="metric-trend" :class="metric.trend">
              <el-icon v-if="metric.trend === 'up'"><CaretTop /></el-icon>
              <el-icon v-else><CaretBottom /></el-icon>
              {{ metric.change }}
            </div>
          </div>
        </div>
      </div>

      <!-- 第二行：图表展示 -->
      <div class="charts-row">
        <!-- 排名榜 -->
        <div class="chart-card ranking-card">
          <div class="card-header">
            <h3>教研室排名 TOP 10</h3>
            <el-tag type="success">实时更新</el-tag>
          </div>
          <div class="ranking-list">
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
                <div class="rank-college">{{ item.college }}</div>
              </div>
              <div class="rank-score">{{ item.score }}</div>
            </div>
          </div>
        </div>

        <!-- 评分分布 -->
        <div class="chart-card">
          <div class="card-header">
            <h3>评分分布</h3>
          </div>
          <div ref="scoreDistributionChart" class="chart-container"></div>
        </div>

        <!-- 趋势分析 -->
        <div class="chart-card">
          <div class="card-header">
            <h3>月度趋势</h3>
          </div>
          <div ref="trendChart" class="chart-container"></div>
        </div>
      </div>

      <!-- 第三行：详细数据 -->
      <div class="details-row">
        <!-- 各学院对比 -->
        <div class="chart-card wide-card">
          <div class="card-header">
            <h3>各学院平均分对比</h3>
          </div>
          <div ref="collegeComparisonChart" class="chart-container"></div>
        </div>

        <!-- 指标雷达图 -->
        <div class="chart-card">
          <div class="card-header">
            <h3>综合指标分析</h3>
          </div>
          <div ref="radarChart" class="chart-container"></div>
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
  User,
  TrendCharts,
  PieChart,
  Histogram,
  DataAnalysis,
  CaretTop,
  CaretBottom,
  School,
  Document,
  Checked,
  Medal
} from '@element-plus/icons-vue'

const router = useRouter()

const currentTime = ref('')
let timeInterval: number

// 图表引用
const scoreDistributionChart = ref<HTMLElement>()
const trendChart = ref<HTMLElement>()
const collegeComparisonChart = ref<HTMLElement>()
const radarChart = ref<HTMLElement>()

// 关键指标
const keyMetrics = ref([
  {
    label: '参评教研室',
    value: '48',
    change: '+3',
    trend: 'up',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    icon: School
  },
  {
    label: '已完成自评',
    value: '45',
    change: '+5',
    trend: 'up',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    icon: Document
  },
  {
    label: '已完成评分',
    value: '42',
    change: '+8',
    trend: 'up',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    icon: Checked
  },
  {
    label: '平均得分',
    value: '87.5',
    change: '+2.3',
    trend: 'up',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    icon: Medal
  }
])

// 排名数据
const rankingData = ref([
  { name: '计算机科学教研室', college: '信息工程学院', score: 95.8 },
  { name: '数学分析教研室', college: '理学院', score: 94.2 },
  { name: '英语教研室', college: '外国语学院', score: 93.5 },
  { name: '机械设计教研室', college: '机械工程学院', score: 92.8 },
  { name: '电子技术教研室', college: '电气工程学院', score: 91.6 },
  { name: '化学实验教研室', college: '化学化工学院', score: 90.9 },
  { name: '体育教研室', college: '体育学院', score: 90.2 },
  { name: '艺术设计教研室', college: '艺术学院', score: 89.7 },
  { name: '经济学教研室', college: '经济管理学院', score: 89.1 },
  { name: '法学教研室', college: '法学院', score: 88.5 }
])

// 初始化评分分布图表
const initScoreDistributionChart = () => {
  if (!scoreDistributionChart.value) return
  
  const chart = echarts.init(scoreDistributionChart.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}个 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: {
        color: '#fff'
      }
    },
    series: [
      {
        name: '评分分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#0a0e27',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: '#fff'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 8, name: '优秀(90-100)', itemStyle: { color: '#43e97b' } },
          { value: 18, name: '良好(80-89)', itemStyle: { color: '#4facfe' } },
          { value: 14, name: '中等(70-79)', itemStyle: { color: '#f093fb' } },
          { value: 6, name: '及格(60-69)', itemStyle: { color: '#ffa726' } },
          { value: 2, name: '不及格(<60)', itemStyle: { color: '#f5576c' } }
        ]
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => chart.resize())
}

// 初始化趋势图表
const initTrendChart = () => {
  if (!trendChart.value) return
  
  const chart = echarts.init(trendChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['9月', '10月', '11月', '12月', '1月', '2月'],
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: '#fff'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: '#fff'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    },
    series: [
      {
        name: '平均分',
        type: 'line',
        smooth: true,
        data: [82.5, 84.2, 85.8, 86.5, 87.2, 87.5],
        lineStyle: {
          color: '#667eea',
          width: 3
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
          ])
        },
        itemStyle: {
          color: '#667eea'
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => chart.resize())
}

// 初始化学院对比图表
const initCollegeComparisonChart = () => {
  if (!collegeComparisonChart.value) return
  
  const chart = echarts.init(collegeComparisonChart.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['信息工程', '理学院', '外国语', '机械工程', '电气工程', '化学化工', '体育学院', '艺术学院'],
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: '#fff',
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      axisLabel: {
        color: '#fff'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    },
    series: [
      {
        name: '平均分',
        type: 'bar',
        data: [92.5, 91.8, 90.5, 89.8, 88.9, 88.2, 87.5, 86.8],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [10, 10, 0, 0]
        },
        barWidth: '60%'
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => chart.resize())
}

// 初始化雷达图
const initRadarChart = () => {
  if (!radarChart.value) return
  
  const chart = echarts.init(radarChart.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: [
        { name: '教学质量', max: 100 },
        { name: '科研成果', max: 100 },
        { name: '团队建设', max: 100 },
        { name: '学生评价', max: 100 },
        { name: '创新能力', max: 100 },
        { name: '社会服务', max: 100 }
      ],
      splitArea: {
        areaStyle: {
          color: ['rgba(102, 126, 234, 0.1)', 'rgba(102, 126, 234, 0.2)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)'
        }
      },
      name: {
        textStyle: {
          color: '#fff'
        }
      }
    },
    series: [
      {
        name: '综合指标',
        type: 'radar',
        data: [
          {
            value: [88, 85, 90, 92, 87, 84],
            name: '全校平均',
            areaStyle: {
              color: 'rgba(102, 126, 234, 0.3)'
            },
            lineStyle: {
              color: '#667eea',
              width: 2
            },
            itemStyle: {
              color: '#667eea'
            }
          }
        ]
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式
  window.addEventListener('resize', () => chart.resize())
}

const updateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const date = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  const weekday = weekdays[now.getDay()]
  
  currentTime.value = `${year}-${month}-${date} ${hours}:${minutes}:${seconds} ${weekday}`
}

const goToLogin = () => {
  router.push('/login')
}

onMounted(() => {
  updateTime()
  timeInterval = window.setInterval(updateTime, 1000)
  
  // 初始化所有图表
  setTimeout(() => {
    initScoreDistributionChart()
    initTrendChart()
    initCollegeComparisonChart()
    initRadarChart()
  }, 100)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #0a0e27;
  color: white;
  display: flex;
  flex-direction: column;
}

/* 顶部标题栏 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #1a1f3a 0%, #0a0e27 100%);
  border-bottom: 2px solid rgba(102, 126, 234, 0.3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-logo {
  width: 60px;
  height: 60px;
  object-fit: contain;
  border-radius: 10px;
}

.header-title h1 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-title p {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0.25rem 0 0 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.time-display {
  font-size: 1.1rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Courier New', monospace;
}

/* 主要内容区 */
.dashboard-content {
  flex: 1;
  padding: 2rem;
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
  background: linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-5px);
  border-color: rgba(102, 126, 234, 0.5);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: white;
}

.metric-info {
  flex: 1;
}

.metric-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.25rem;
}

.metric-trend {
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.metric-trend.up {
  color: #43e97b;
}

.metric-trend.down {
  color: #f5576c;
}

/* 图表行 */
.charts-row,
.details-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.chart-card {
  background: linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%);
  border-radius: 15px;
  padding: 1.5rem;
  border: 1px solid rgba(102, 126, 234, 0.2);
  display: flex;
  flex-direction: column;
}

.wide-card {
  grid-column: span 2;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.card-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
  color: white;
}

/* 排名列表 */
.ranking-card {
  background: linear-gradient(135deg, #1a1f3a 0%, #0f1729 100%);
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 10px;
  transition: all 0.3s;
}

.ranking-item:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateX(5px);
}

.rank-number {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.rank-number.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #0a0e27;
}

.rank-number.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #0a0e27;
}

.rank-number.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #e8a87c 100%);
  color: #0a0e27;
}

.rank-info {
  flex: 1;
}

.rank-name {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.rank-college {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.rank-score {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

/* 图表容器 */
.chart-container {
  flex: 1;
  min-height: 250px;
  width: 100%;
}

/* 图表占位符 */
.chart-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.4);
  min-height: 250px;
}

.chart-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.chart-placeholder p {
  font-size: 1rem;
}

/* 页脚 */
.dashboard-footer {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #1a1f3a 0%, #0a0e27 100%);
  border-top: 2px solid rgba(102, 126, 234, 0.3);
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-row,
  .details-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .wide-card {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .metrics-row,
  .charts-row,
  .details-row {
    grid-template-columns: 1fr;
  }
  
  .header-title h1 {
    font-size: 1.3rem;
  }
}
</style>
