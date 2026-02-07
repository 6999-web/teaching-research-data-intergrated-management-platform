<template>
  <div class="anomaly-handling-view">
    <div class="page-header">
      <h1>异常数据处理</h1>
      <p class="page-description">
        查看和处理AI评分过程中检测到的异常数据，包括数量不一致、缺少附件等问题。
      </p>
    </div>

    <AnomalyHandling />
  </div>
</template>

<script setup lang="ts">
import AnomalyHandling from '@/components/AnomalyHandling.vue'
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

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #303133;
  font-weight: 600;
}

.page-description {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
</style>
