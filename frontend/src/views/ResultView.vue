<template>
  <div class="result-view-page">
    <div class="page-header">
      <h1>考评结果查看</h1>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">
          首页
        </el-breadcrumb-item>
        <el-breadcrumb-item>考评结果</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div
      v-if="loading"
      class="loading-container"
    >
      <el-skeleton
        :rows="10"
        animated
      />
    </div>

    <div
      v-else-if="error"
      class="error-container"
    >
      <el-alert
        title="加载失败"
        type="error"
        :description="error"
        show-icon
        :closable="false"
      />
    </div>

    <div
      v-else-if="result"
      class="result-content"
    >
      <!-- Final Score Card -->
      <el-card
        class="score-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <span class="card-title">最终得分</span>
            <el-tag
              type="success"
              size="large"
            >
              已公示
            </el-tag>
          </div>
        </template>
        <div class="final-score-display">
          <div class="score-value">
            {{ result.final_score?.final_score || 0 }}
          </div>
          <div class="score-label">
            分
          </div>
        </div>
        <div class="score-meta">
          <p><strong>教研室：</strong>{{ result.teaching_office_name }}</p>
          <p><strong>考评年度：</strong>{{ result.evaluation_year }}</p>
          <p><strong>公示时间：</strong>{{ formatDate(result.published_at) }}</p>
        </div>
      </el-card>

      <!-- AI Score Details -->
      <el-card
        v-if="result.ai_score"
        class="details-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <span class="card-title">AI评分详情</span>
            <el-tag type="info">
              总分：{{ result.ai_score.total_score }}
            </el-tag>
          </div>
        </template>
        <el-table
          :data="result.ai_score.indicator_scores"
          stripe
        >
          <el-table-column
            prop="indicator"
            label="考核指标"
            width="200"
          >
            <template #default="{ row }">
              {{ getIndicatorLabel(row.indicator) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="score"
            label="得分"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <el-tag type="primary">
                {{ row.score }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="reasoning"
            label="评分说明"
          />
        </el-table>
        <div class="ai-meta">
          <p><strong>解析教学改革项目数：</strong>{{ result.ai_score.parsed_reform_projects }}</p>
          <p><strong>解析荣誉表彰数：</strong>{{ result.ai_score.parsed_honorary_awards }}</p>
          <p><strong>评分时间：</strong>{{ formatDate(result.ai_score.scored_at) }}</p>
        </div>
      </el-card>

      <!-- Manual Scores Details -->
      <el-card
        class="details-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <span class="card-title">评审人打分记录</span>
            <el-tag type="warning">
              共 {{ result.manual_scores.length }} 位评审人
            </el-tag>
          </div>
        </template>
        <el-collapse
          v-model="activeReviewers"
          accordion
        >
          <el-collapse-item
            v-for="(manualScore, index) in result.manual_scores"
            :key="manualScore.id"
            :name="index"
          >
            <template #title>
              <div class="reviewer-title">
                <span class="reviewer-name">{{ manualScore.reviewer_name }}</span>
                <el-tag
                  :type="manualScore.reviewer_role === 'evaluation_team' ? 'danger' : 'info'"
                  size="small"
                >
                  {{ getRoleLabel(manualScore.reviewer_role) }}
                </el-tag>
                <el-tag
                  type="success"
                  size="small"
                >
                  权重：{{ (manualScore.weight * 100).toFixed(0) }}%
                </el-tag>
                <span class="reviewer-date">{{ formatDate(manualScore.submitted_at) }}</span>
              </div>
            </template>
            <el-table
              :data="manualScore.scores"
              stripe
              size="small"
            >
              <el-table-column
                prop="indicator"
                label="考核指标"
                width="200"
              >
                <template #default="{ row }">
                  {{ getIndicatorLabel(row.indicator) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="score"
                label="得分"
                width="100"
                align="center"
              >
                <template #default="{ row }">
                  <el-tag type="primary">
                    {{ row.score }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="comment"
                label="评语"
              />
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- Final Score Summary -->
      <el-card
        v-if="result.final_score"
        class="details-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <span class="card-title">最终得分汇总说明</span>
          </div>
        </template>
        <div class="summary-content">
          <p>{{ result.final_score.summary || '暂无汇总说明' }}</p>
          <div class="summary-meta">
            <p><strong>确定时间：</strong>{{ formatDate(result.final_score.determined_at) }}</p>
          </div>
        </div>
      </el-card>

      <!-- Insight Summary -->
      <el-card
        v-if="result.insight_summary"
        class="details-card insight-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <span class="card-title">系统生成的感悟总结</span>
            <el-tag type="success">
              自动生成
            </el-tag>
          </div>
        </template>
        <div class="insight-content">
          <el-icon class="insight-icon">
            <Document />
          </el-icon>
          <p class="insight-text">
            {{ result.insight_summary.summary }}
          </p>
          <div class="insight-meta">
            <p><strong>生成时间：</strong>{{ formatDate(result.insight_summary.generated_at) }}</p>
          </div>
        </div>
      </el-card>
    </div>

    <div
      v-else
      class="empty-container"
    >
      <el-empty description="暂无考评结果" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { resultApi } from '@/api/client'
import type { EvaluationResult } from '@/types/result'
import { EVALUATION_INDICATORS } from '@/types/scoring'

const route = useRoute()
const loading = ref(true)
const error = ref<string | null>(null)
const result = ref<EvaluationResult | null>(null)
const activeReviewers = ref<number>(0)

// Get evaluation ID from route params or query
const evaluationId = ref<string>(
  (route.params.id as string) || (route.query.evaluationId as string) || ''
)

// Load result data
onMounted(async () => {
  if (!evaluationId.value) {
    error.value = '缺少考评ID参数'
    loading.value = false
    return
  }

  try {
    loading.value = true
    const response = await resultApi.getResult(evaluationId.value)
    result.value = response.data
  } catch (err: any) {
    console.error('Failed to load result:', err)
    error.value = err.response?.data?.detail || '加载考评结果失败，请稍后重试'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
})

// Get indicator label from key
const getIndicatorLabel = (key: string): string => {
  const indicator = EVALUATION_INDICATORS.find(ind => ind.key === key)
  return indicator?.label || key
}

// Get role label
const getRoleLabel = (role: string): string => {
  const roleMap: Record<string, string> = {
    evaluation_team: '考评小组',
    evaluation_office: '考评办公室'
  }
  return roleMap[role] || role
}

// Format date
const formatDate = (dateStr?: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.result-view-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}

.loading-container,
.error-container,
.empty-container {
  padding: 40px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

/* Final Score Card */
.score-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.score-card :deep(.el-card__header) {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.score-card .card-title {
  color: white;
}

.final-score-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin: 30px 0;
}

.score-value {
  font-size: 72px;
  font-weight: bold;
  line-height: 1;
}

.score-label {
  font-size: 24px;
  margin-left: 10px;
}

.score-meta {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.score-meta p {
  margin: 8px 0;
  font-size: 14px;
}

/* Details Cards */
.details-card {
  margin-top: 0;
}

.ai-meta {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.ai-meta p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

/* Reviewer Collapse */
.reviewer-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.reviewer-name {
  font-weight: 600;
  color: #303133;
}

.reviewer-date {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}

/* Summary Content */
.summary-content {
  padding: 10px 0;
}

.summary-content p {
  line-height: 1.8;
  color: #606266;
  margin-bottom: 15px;
}

.summary-meta {
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.summary-meta p {
  margin: 8px 0;
  font-size: 14px;
  color: #909399;
}

/* Insight Card */
.insight-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.insight-card :deep(.el-card__header) {
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.insight-card .card-title {
  color: white;
}

.insight-content {
  padding: 20px 0;
}

.insight-icon {
  font-size: 48px;
  display: block;
  text-align: center;
  margin-bottom: 20px;
  opacity: 0.9;
}

.insight-text {
  font-size: 16px;
  line-height: 2;
  text-align: justify;
  margin-bottom: 20px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  border-left: 4px solid rgba(255, 255, 255, 0.5);
}

.insight-meta {
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.insight-meta p {
  margin: 8px 0;
  font-size: 14px;
  opacity: 0.9;
}
</style>
