<template>
  <div class="college-dashboard">
    <PageHeader 
      title="二级学院质量监测驾驶舱" 
      subtitle="学院：信息工程学院 (示例)" 
      :showBack="false"
    />
    
    <div v-if="loading" class="loading-state">
      <el-spin size="large" />
    </div>

    <div v-else class="content-container">
      <!-- Key Metrics -->
      <div class="metrics-cards">
        <el-card class="metric-card">
          <template #header>
            <div class="card-header">
              <span>平均分</span>
            </div>
          </template>
          <div class="metric-value">{{ stats.avg_score }}</div>
        </el-card>
        
        <el-card class="metric-card">
           <template #header>
            <div class="card-header">
              <span>待审核整改项</span>
            </div>
          </template>
          <div class="metric-value">3</div> <!-- Mock -->
        </el-card>
      </div>

      <!-- Rankings -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>教研室排名</span>
          </div>
        </template>
        <div class="bar-chart">
           <div v-for="item in stats.rank_list" :key="item.name" class="bar-item">
              <span class="label">{{ item.name }}</span>
              <div class="bar-container">
                <div class="bar" :style="{ width: item.score + '%' }"></div>
              </div>
              <span class="score">{{ item.score }}</span>
           </div>
        </div>
      </el-card>

      <!-- Weakness Analysis -->
      <el-card class="weakness-card">
        <template #header>
          <div class="card-header">
            <span>共性薄弱环节</span>
          </div>
        </template>
        <el-table :data="stats.weakness_analysis" stripe style="width: 100%">
          <el-table-column prop="indicator" label="失分指标" />
          <el-table-column prop="avg_loss_rate" label="平均失分率">
             <template #default="scope">
               {{ (scope.row.avg_loss_rate * 100).toFixed(1) }}%
             </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { collegeApi, type CollegeStats } from '@/api/college'
import { ElMessage } from 'element-plus'

const loading = ref(true)
const stats = ref<CollegeStats>({
  avg_score: 0,
  rank_list: [],
  weakness_analysis: []
})

onMounted(async () => {
  try {
    const res = await collegeApi.getDashboardStats()
    stats.value = res.data
  } catch (error) {
    ElMessage.error('无法加载仪表盘数据')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.college-dashboard {
  padding: 20px;
}
.metrics-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.metric-card {
  flex: 1;
}
.metric-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}
.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.bar-item {
  display: flex;
  align-items: center;
}
.label {
  width: 150px;
  text-align: right;
  margin-right: 15px;
}
.bar-container {
  flex: 1;
  background: #f0f2f5;
  height: 20px;
  border-radius: 10px;
  overflow: hidden;
}
.bar {
  height: 100%;
  background: #409EFF;
  transition: width 0.5s ease;
}
.score {
  width: 50px;
  margin-left: 10px;
}
.chart-card, .weakness-card {
  margin-bottom: 20px;
}
</style>
