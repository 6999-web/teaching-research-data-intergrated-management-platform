<template>
  <div class="manual-scoring-form">
    <!-- 移除标签页导航，直接显示内容 -->
    <el-card class="scoring-card">
      <template #header>
        <div class="card-header">
          <h2>手动评分</h2>
          <el-tag v-if="currentUserRole" :type="roleTagType">
            {{ roleLabel }}
          </el-tag>
        </div>
      </template>

      <!-- 已提交提示：禁止再次修改 -->
      <el-alert
        v-if="hasSubmitted"
        title="您已提交过评分，无法再次修改。"
        type="warning"
        :closable="false"
        show-icon
        class="weight-alert"
      />
      <!-- Weight Information -->
      <el-alert v-else-if="currentUserRole" :title="weightInfo" type="info" :closable="false" show-icon class="weight-alert" />

      <!-- 评教小组平均分：评分完成后系统自动计算，提交到办公室时以此数据为准 -->
      <el-alert
        v-if="manualScoreAvg != null && manualReviewerCount > 0"
        :title="`评教小组平均分：${manualScoreAvg.toFixed(1)} 分（共 ${manualReviewerCount} 人打分）`"
        type="success"
        :closable="false"
        show-icon
        class="weight-alert"
      >
        <template #default>
          <span>提交到评教小组办公室时，将以此平均分及全部评分记录提交，数据实时计算、真实展示。</span>
        </template>
      </el-alert>

      <!-- 自评表内容与评分整合 -->
      <div v-loading="contentLoading" class="integrated-scoring">
        <div v-if="selfEvaluationContent" class="evaluation-content">
          <!-- 遍历自评表的每个部分 -->
          <div v-for="(section, sectionKey) in selfEvaluationContent" :key="sectionKey" class="content-section">
            <h3 class="section-title">{{ getSectionTitle(sectionKey) }}</h3>
            
            <!-- 遍历每个部分的每一项 -->
            <div v-if="typeof section === 'object' && section !== null" class="section-items">
              <div v-for="(item, itemKey) in section" :key="itemKey" class="content-item-with-scoring">
                <!-- 自评表内容 -->
                <div class="item-content-area">
                  <div class="item-header">
                    <span class="item-label">{{ getItemLabel(itemKey) }}</span>
                    <el-tag v-if="item.selfScore !== undefined" type="success" size="small">
                      自评分: {{ item.selfScore }}分
                    </el-tag>
                  </div>
                  <div v-if="item.content" class="item-content">{{ item.content }}</div>
                  
                  <!-- 显示该项对应的附件 -->
                  <div v-if="getAttachmentsForIndicator(itemKey).length > 0" class="item-attachments">
                    <div class="attachments-header">
                      <el-icon><Paperclip /></el-icon>
                      <span>相关附件 ({{ getAttachmentsForIndicator(itemKey).length }})</span>
                    </div>
                    <div class="attachment-list">
                      <div 
                        v-for="attachment in getAttachmentsForIndicator(itemKey)" 
                        :key="attachment.id"
                        class="attachment-item"
                      >
                        <el-icon class="file-icon"><Document /></el-icon>
                        <span class="file-name">{{ attachment.file_name }}</span>
                        <span class="file-size">{{ formatFileSize(attachment.file_size) }}</span>
                        <el-button 
                          type="primary" 
                          size="small" 
                          link 
                          @click="handleDownloadAttachment(attachment)"
                        >
                          下载
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 评分区域 -->
                <div v-if="formData.scores[itemKey]" class="scoring-area">
                  <!-- 评分项标题 -->
                  <div class="scoring-header">
                    <h4 class="scoring-title">{{ getItemLabel(itemKey) }}</h4>
                  </div>
                  
                  <!-- 附件显示（在评分区域内） -->
                  <div v-if="getAttachmentsForIndicator(itemKey).length > 0" class="scoring-attachments">
                    <div class="attachments-header-small">
                      <el-icon><Paperclip /></el-icon>
                      <span>附件 ({{ getAttachmentsForIndicator(itemKey).length }})</span>
                    </div>
                    <div class="attachment-list-compact">
                      <div 
                        v-for="attachment in getAttachmentsForIndicator(itemKey)" 
                        :key="attachment.id"
                        class="attachment-item-compact"
                      >
                        <el-icon class="file-icon-small"><Document /></el-icon>
                        <span class="file-name-small">{{ attachment.file_name }}</span>
                        <el-button 
                          type="primary" 
                          size="small" 
                          link 
                          @click="handleDownloadAttachment(attachment)"
                        >
                          下载
                        </el-button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 评分表单 -->
                  <el-form
                    :model="formData"
                    :rules="rules"
                    label-width="100px"
                    label-position="left"
                  >
                    <el-form-item 
                      label="评分"
                      :prop="`scores.${itemKey}.score`"
                    >
                      <el-input-number
                        v-model="formData.scores[itemKey].score"
                        :min="0"
                        :max="item.maxScore || 10"
                        :step="0.5"
                        :precision="1"
                        :disabled="hasSubmitted"
                        placeholder="请输入得分"
                        class="score-input"
                      />
                      <span class="score-hint">/ {{ item.maxScore || 10 }}分</span>
                    </el-form-item>

                    <el-form-item 
                      label="评分原因"
                      :prop="`scores.${itemKey}.comment`"
                    >
                      <el-input
                        v-model="formData.scores[itemKey].comment"
                        type="textarea"
                        :rows="3"
                        :disabled="hasSubmitted"
                        placeholder="请填写评分原因和说明"
                        maxlength="500"
                        show-word-limit
                      />
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else description="暂无自评表内容" />

        <!-- Total Score Display -->
        <div v-if="selfEvaluationContent" class="total-score-section">
          <el-divider />
          <div class="total-score">
            <span class="label">总分：</span>
            <span class="value">{{ totalScore.toFixed(1) }}</span>
            <span class="max">/ {{ maxTotalScore }}分</span>
          </div>
          <!-- 评教小组平均分（多人打分时显示，提交后会自动刷新） -->
          <div v-if="manualScoreAvg != null && manualReviewerCount > 0" class="manual-avg-score">
            <span class="label">评教小组平均分：</span>
            <span class="value">{{ manualScoreAvg.toFixed(1) }} 分</span>
            <span class="meta">（共 {{ manualReviewerCount }} 人打分）</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div v-if="selfEvaluationContent" class="form-actions">
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="hasSubmitted"
            @click="handleSubmit"
          >
            {{ hasSubmitted ? '已提交评分' : '提交评分' }}
          </el-button>
          <el-button
            size="large"
            :disabled="hasSubmitted"
            @click="handleReset"
          >
            重置
          </el-button>
          <el-button
            type="info"
            size="large"
            @click="handleViewAllScores"
          >
            查看所有评审人打分
          </el-button>
        </div>
        
        <!-- Submit to Office Section (only for evaluation_team) -->
        <div v-if="props.currentUserRole === 'evaluation_team' && hasSubmitted" class="submit-office-section">
          <el-divider />
          <el-alert
            v-if="!canSubmitToOffice && props.evaluationStatus"
            title="请先完成评教小组手动评分。评分完成后系统将自动计算所有成员平均分，届时方可提交到评教小组办公室。"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 12px;"
          />
          <div class="submit-office-info">
          <el-alert
            v-if="canSubmitToOffice"
            title="评教小组评分完成，已计算平均分"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            上方已显示评教小组平均分。确认无误后点击下方按钮，将该平均分及评分数据提交到评教小组办公室端，由办公室确定最终得分。
          </el-alert>
            <el-button
              type="success"
              size="large"
              :loading="submittingToOffice"
              :disabled="hasSubmittedToOffice || !canSubmitToOffice"
              @click="handleSubmitToOffice"
            >
              {{ hasSubmittedToOffice ? '已提交到考评办公室' : '提交到考评办公室' }}
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- All Scores Dialog -->
    <el-dialog
      v-model="allScoresVisible"
      title="所有评审人打分记录"
      width="90%"
      :close-on-click-modal="false"
      class="all-scores-dialog"
    >
      <div
        v-if="allScoresLoading"
        class="loading-container"
      >
        <el-icon class="is-loading">
          <Loading />
        </el-icon>
        <span>加载中...</span>
      </div>

      <div
        v-else-if="allScoresData"
        class="all-scores-content"
      >
        <!-- AI Score Section -->
        <el-card
          v-if="allScoresData.ai_score"
          class="score-card ai-score-card"
        >
          <template #header>
            <div class="score-card-header">
              <h3>AI自动评分</h3>
              <el-tag type="success">
                AI评分
              </el-tag>
            </div>
          </template>
          <div class="score-details">
            <div class="score-item">
              <span class="label">总分：</span>
              <span class="value highlight">{{ allScoresData.ai_score.total_score.toFixed(1) }}分</span>
            </div>
            <div class="score-item">
              <span class="label">评分时间：</span>
              <span class="value">{{ formatDateTime(allScoresData.ai_score.scored_at) }}</span>
            </div>
            <div class="score-item">
              <span class="label">解析教学改革项目：</span>
              <span class="value">{{ allScoresData.ai_score.parsed_reform_projects }}个</span>
            </div>
            <div class="score-item">
              <span class="label">解析荣誉表彰：</span>
              <span class="value">{{ allScoresData.ai_score.parsed_honorary_awards }}个</span>
            </div>
          </div>
          <el-divider />
          <div class="indicator-scores">
            <h4>各指标得分：</h4>
            <div
              v-for="(indicatorScore, index) in allScoresData.ai_score.indicator_scores"
              :key="index"
              class="indicator-score-item"
            >
              <div class="indicator-name">
                {{ indicatorScore.indicator }}
              </div>
              <div class="indicator-score">
                {{ indicatorScore.score }}分
              </div>
              <div class="indicator-reasoning">
                {{ indicatorScore.reasoning }}
              </div>
            </div>
          </div>
        </el-card>

        <!-- Manual Scores Section -->
        <div
          v-if="allScoresData.manual_scores.length > 0"
          class="manual-scores-section"
        >
          <h3 class="section-title">
            评审人打分记录
          </h3>
          <el-card
            v-for="manualScore in sortedManualScores"
            :key="manualScore.id"
            class="score-card manual-score-card"
            :class="{ 'evaluation-team-card': manualScore.reviewer_role === 'evaluation_team' }"
          >
            <template #header>
              <div class="score-card-header">
                <div class="reviewer-info">
                  <h3>{{ manualScore.reviewer_name }}</h3>
                  <el-tag
                    :type="manualScore.reviewer_role === 'evaluation_team' ? 'danger' : 'warning'"
                    class="role-tag"
                  >
                    {{ getRoleLabel(manualScore.reviewer_role) }}
                  </el-tag>
                  <el-tag
                    type="info"
                    class="weight-tag"
                  >
                    权重: {{ (manualScore.weight * 100).toFixed(0) }}%
                  </el-tag>
                </div>
                <div class="submit-time">
                  {{ formatDateTime(manualScore.submitted_at) }}
                </div>
              </div>
            </template>
            <div class="manual-score-details">
              <div
                v-for="score in manualScore.scores"
                :key="score.indicator"
                class="indicator-score-item"
              >
                <div class="indicator-header-row">
                  <span class="indicator-name">{{ score.indicator }}</span>
                  <span class="indicator-score">{{ score.score }}分</span>
                </div>
                <div class="indicator-comment">
                  {{ score.comment }}
                </div>
              </div>
              <el-divider />
              <div class="total-score-row">
                <span class="label">总分：</span>
                <span class="value">{{ calculateManualTotalScore(manualScore.scores) }}分</span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Final Score Section -->
        <el-card
          v-if="allScoresData.final_score"
          class="score-card final-score-card"
        >
          <template #header>
            <div class="score-card-header">
              <h3>最终得分</h3>
              <el-tag type="danger">
                最终确定
              </el-tag>
            </div>
          </template>
          <div class="score-details">
            <div class="score-item">
              <span class="label">最终得分：</span>
              <span class="value highlight large">{{ allScoresData.final_score.final_score.toFixed(1) }}分</span>
            </div>
            <div class="score-item">
              <span class="label">确定时间：</span>
              <span class="value">{{ formatDateTime(allScoresData.final_score.determined_at) }}</span>
            </div>
            <div
              v-if="allScoresData.final_score.summary"
              class="score-item full-width"
            >
              <span class="label">汇总说明：</span>
              <div class="summary-text">
                {{ allScoresData.final_score.summary }}
              </div>
            </div>
          </div>
        </el-card>

        <!-- Empty State -->
        <el-empty
          v-if="!allScoresData.ai_score && allScoresData.manual_scores.length === 0 && !allScoresData.final_score"
          description="暂无评分记录"
        />
      </div>

      <template #footer>
        <el-button @click="allScoresVisible = false">
          关闭
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Loading, Document, Paperclip } from '@element-plus/icons-vue'
import { scoringApi, selfEvaluationApi } from '@/api/client'
import apiClient from '@/api/client'
import {
  EVALUATION_INDICATORS,
  TOTAL_MAX_SCORE,
  type IndicatorScore,
  type ManualScoreCreate,
  type AllScoresResponse
} from '@/types/scoring'

// Props
interface Props {
  evaluationId: string
  currentUserRole?: 'evaluation_team' | 'evaluation_office'
  /** 当前考评状态，用于控制「提交到考评办公室」是否可用 */
  evaluationStatus?: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  submitted: [scoreRecordId: string]
  submittedToOffice: [evaluationId: string]
}>()

// Form reference
const formRef = ref<FormInstance>()

// State
const submitting = ref(false)
const hasSubmitted = ref(false)
const submittingToOffice = ref(false)
const hasSubmittedToOffice = ref(false)
const allScoresVisible = ref(false)
const allScoresLoading = ref(false)
const allScoresData = ref<AllScoresResponse | null>(null)
const evaluationStatus = ref<string>('')

// Content and attachments state
const contentLoading = ref(false)
const selfEvaluationContent = ref<any>(null)
const attachmentsLoading = ref(false)
const attachments = ref<any[]>([])

// Indicators
const indicators = EVALUATION_INDICATORS
const maxTotalScore = TOTAL_MAX_SCORE

// Form data - initialize scores for all items in self-evaluation
const formData = reactive<{
  scores: Record<string, { score: number; comment: string }>
}>({
  scores: {}
})

// Initialize form data based on self-evaluation content
const initializeFormData = () => {
  if (!selfEvaluationContent.value) return
  
  // 遍历自评表内容，为每一项初始化评分数据
  Object.keys(selfEvaluationContent.value).forEach(sectionKey => {
    const section = selfEvaluationContent.value[sectionKey]
    if (typeof section === 'object' && section !== null) {
      Object.keys(section).forEach(itemKey => {
        // 使用 Vue.set 或直接赋值来确保响应式
        formData.scores[itemKey] = {
          score: 0,
          comment: ''
        }
      })
    }
  })
  
  console.log('Form data initialized:', Object.keys(formData.scores).length, 'items')
}

// Get attachments for a specific indicator
const getAttachmentsForIndicator = (indicatorKey: string | number): any[] => {
  const ik = String(indicatorKey)
  // 将 itemKey 映射到附件的 indicator 字段
  const indicatorMap: Record<string, string> = {
    'teachingProcessManagement': 'teachingProcessManagement',
    'teachingQualityManagement': 'teachingQualityManagement',
    'courseAssessment': 'courseAssessment',
    'educationResearch': 'educationResearch',
    'courseConstruction': 'courseConstruction',
    'teacherTeamBuilding': 'teacherTeamBuilding',
    'researchAndExchange': 'researchAndExchange',
    'archiveManagement': 'archiveManagement',
    'reformProjects': 'reformProjects',
    'teachingHonors': 'teachingHonors',
    'teachingCompetitions': 'teachingCompetitions',
    'innovationCompetitions': 'innovationCompetitions',
    'ethicsViolations': 'ethicsViolations',
    'teachingAccidents': 'teachingAccidents',
    'ideologyIssues': 'ideologyIssues',
    'workloadIncomplete': 'workloadIncomplete'
  }
  
  const mappedIndicator = indicatorMap[ik] || ik
  return attachments.value.filter(att => att.indicator === mappedIndicator)
}

// Computed: Total score
const totalScore = computed(() => {
  return Object.values(formData.scores).reduce((sum, item) => sum + item.score, 0)
})

// Computed: Role label
const roleLabel = computed(() => {
  return getRoleLabel(props.currentUserRole || '')
})

// Computed: Role tag type
const roleTagType = computed(() => {
  return props.currentUserRole === 'evaluation_team' ? 'danger' : 'warning'
})

// Computed: Weight info
const weightInfo = computed(() => {
  const weight = props.currentUserRole === 'evaluation_team' ? 70 : 50
  return `您的评分权重为 ${weight}%。${props.currentUserRole === 'evaluation_team' ? '考评小组的评分权重高于考评办公室。' : ''}`
})

// 仅当「已手动评分」时允许提交：评分完成后系统计算评教小组平均分，再提交到办公室
const canSubmitToOffice = computed(() => {
  const s = props.evaluationStatus || evaluationStatus.value
  return s === 'manually_scored'
})

// Computed: Sorted manual scores (evaluation_team first)
const sortedManualScores = computed(() => {
  if (!allScoresData.value) {
    return []
  }
  // Assuming aiScore and manualScores are refs defined elsewhere if they are to be updated here.
  // As per the instruction, if allScoresData.value is present, we proceed with sorting.
  // The original code already handles the null check for allScoresData.value.
  // The provided edit snippet for this section is syntactically incorrect and introduces undefined variables.
  // Therefore, I'm keeping the original, correct logic for sorting.
  return [...allScoresData.value.manual_scores].sort((a, b) => {
    // Sort by role first (evaluation_team first), then by submitted time
    if (a.reviewer_role === 'evaluation_team' && b.reviewer_role !== 'evaluation_team') {
      return -1
    }
    if (a.reviewer_role !== 'evaluation_team' && b.reviewer_role === 'evaluation_team') {
      return 1
    }
    return new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime()
  })
})

// 评教小组平均分（多人打分时的平均）
const manualScoreAvg = computed(() => {
  if (!allScoresData.value?.manual_scores?.length) return null
  const totals = allScoresData.value.manual_scores.map(ms => calculateManualTotalScore(ms.scores))
  const sum = totals.reduce((a, b) => a + b, 0)
  return sum / totals.length
})
const manualReviewerCount = computed(() => allScoresData.value?.manual_scores?.length ?? 0)

// Validation rules - 使用动态规则，在提交时手动验证
const rules = reactive<FormRules>({})

// Get role label
function getRoleLabel(role: string): string {
  const labels: Record<string, string> = {
    'evaluation_team': '考评小组',
    'evaluation_office': '考评办公室'
  }
  return labels[role] || role
}

// Calculate manual total score
function calculateManualTotalScore(scores: IndicatorScore[]): number {
  return scores.reduce((sum, score) => sum + score.score, 0)
}

// 负面清单与亮点工作为选填，其余为必填
const OPTIONAL_INDICATOR_KEYS = new Set([
  'ethicsViolations', 'teachingAccidents', 'ideologyIssues', 'workloadIncomplete', // 负面清单
  'teachingReformProjects', 'teachingHonors', 'teachingCompetitions', 'innovationCompetitions'  // 亮点工作
])

// Handle submit
const handleSubmit = async () => {
  try {
    // 手动验证：必填项须有评分和评语；负面清单、亮点工作为选填
    const scoreEntries = Object.entries(formData.scores)
    if (scoreEntries.length === 0) {
      ElMessage.error('请先加载自评表内容后再提交评分')
      return
    }

    const requiredEntries = scoreEntries.filter(([key]) => !OPTIONAL_INDICATOR_KEYS.has(String(key)))
    const emptyComment = requiredEntries.find(([, val]) => !val.comment || val.comment.trim().length < 2)
    if (emptyComment) {
      const label = getItemLabel(emptyComment[0])
      ElMessage.error(`请填写「${label}」的评分原因（至少2个字符）`)
      return
    }

    // Confirm submission
    await ElMessageBox.confirm(
      '评分提交后将无法修改或删除，请确认评分内容准确无误。确定要提交吗？',
      '确认提交评分',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    submitting.value = true

    // 直接从 formData.scores 中收集评分数据（key 为自评表字段名）；选填项无评语时用占位符
    const scores: IndicatorScore[] = Object.entries(formData.scores).map(([key, val]) => {
      const isOptional = OPTIONAL_INDICATOR_KEYS.has(String(key))
      const comment = (val.comment && val.comment.trim()) ? val.comment.trim() : (isOptional ? '选填未填' : '')
      return {
        indicator: getItemLabel(key),
        score: val.score,
        comment
      }
    })

    const requestData: ManualScoreCreate = {
      evaluation_id: props.evaluationId,
      scores
    }

    // Submit to API
    const response = await scoringApi.submitManualScore(requestData)

    hasSubmitted.value = true

    // 立即重新拉取全部评分，用于更新「评教小组平均分」显示
    try {
      const res = await scoringApi.getAllScores(props.evaluationId)
      if (res.data) allScoresData.value = res.data
    } catch (_) {}

    ElMessage.success({
      message: '评分提交成功！评分记录已保存，系统已更新评教小组平均分。',
      duration: 5000,
      showClose: true
    })

    emit('submitted', response.data.score_record_id)

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Submit manual score failed:', error)

      const errorMessage = error.response?.data?.detail || '评分提交失败，请重试'

      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    submitting.value = false
  }
}

// Handle reset
const handleReset = () => {
  if (!formRef.value) return

  ElMessageBox.confirm(
    '确定要重置表单吗？所有填写的内容将被清空。',
    '确认重置',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    formRef.value?.resetFields()
    
    // Reset scores to 0
    indicators.forEach(indicator => {
      formData.scores[indicator.key] = {
        score: 0,
        comment: ''
      }
    })
    
    ElMessage.info('表单已重置')
  }).catch(() => {
    // User cancelled
  })
}

// Handle submit to evaluation office
const handleSubmitToOffice = async () => {
  try {
    await ElMessageBox.confirm(
      '提交后考评表将流转到考评办公室，您将无法再修改评分。确定要提交吗？',
      '确认提交到考评办公室',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    submittingToOffice.value = true

    const response = await scoringApi.submitToOffice(props.evaluationId)

    hasSubmittedToOffice.value = true
    evaluationStatus.value = response.data.status

    ElMessage.success({
      message: '已成功提交到考评办公室！',
      duration: 5000,
      showClose: true
    })

    emit('submittedToOffice', props.evaluationId)

  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Submit to office failed:', error)
      const detail = error.response?.data?.detail
      const errorMessage =
        (typeof detail === 'object' && detail?.message) ? detail.message
          : (typeof detail === 'string' ? detail : null) || '提交失败，请重试'

      ElMessage.error({
        message: errorMessage,
        duration: 5000,
        showClose: true
      })
    }
  } finally {
    submittingToOffice.value = false
  }
}

// Handle view all scores
const handleViewAllScores = async () => {
  allScoresVisible.value = true
  allScoresLoading.value = true

  try {
    const response = await scoringApi.getAllScores(props.evaluationId)
    allScoresData.value = response.data

    // Check if current user has already submitted
    if (allScoresData.value) {
      if (props.currentUserRole && allScoresData.value.manual_scores.length > 0) {
        const currentUserId = localStorage.getItem('userId') || ''
        const hasUserSubmitted = allScoresData.value.manual_scores.some(
          (score: { reviewer_id: string }) => String(score.reviewer_id) === String(currentUserId)
        )
        if (hasUserSubmitted) {
          hasSubmitted.value = true
        }
      }
    }

  } catch (error: any) {
    console.error('Failed to load all scores:', error)

    const errorMessage = error.response?.data?.detail || '加载评分记录失败'

    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  } finally {
    allScoresLoading.value = false
  }
}

// Load self-evaluation content
const loadSelfEvaluation = async () => {
  contentLoading.value = true
  try {
    const response = await selfEvaluationApi.get(props.evaluationId)
    selfEvaluationContent.value = response.data.content
    
    // 立即初始化表单数据
    initializeFormData()
  } catch (error: any) {
    console.error('Failed to load self-evaluation:', error)
    ElMessage.error('加载自评表内容失败')
  } finally {
    contentLoading.value = false
  }
}

// Load attachments
const loadAttachments = async () => {
  attachmentsLoading.value = true
  try {
    const endpoint = `/teaching-office/attachments/${props.evaluationId}`
    const response = await apiClient.get(endpoint)
    attachments.value = response.data
  } catch (error: any) {
    console.error('Failed to load attachments:', error)
    ElMessage.error('加载附件列表失败')
  } finally {
    attachmentsLoading.value = false
  }
}

// Download attachment
const handleDownloadAttachment = async (attachment: any) => {
  try {
    const endpoint = `/teaching-office/attachments/${attachment.id}/download`
    const response = await apiClient.get(endpoint, {
      responseType: 'blob'
    })
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', attachment.file_name || 'attachment')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('文件下载成功')
  } catch (error: any) {
    console.error('Failed to download attachment:', error)
    ElMessage.error('文件下载失败')
  }
}

// Helper: Get section title
const getSectionTitle = (sectionKey: string | number): string => {
  const sk = String(sectionKey)
  const titles: Record<string, string> = {
    'section1': '一、教学常规管理',
    'section2': '二、教学改革与研究',
    'section3': '三、教学质量与成果',
    'section4': '四、师资队伍建设',
    'section5': '五、教学资源建设',
    // 英文字段名映射
    'teachingManagement': '教学常规管理',
    'teachingReform': '教学改革与研究',
    'teachingQuality': '教学质量与成果',
    'facultyDevelopment': '师资队伍建设',
    'teachingResources': '教学资源建设',
    'positiveList': '正面清单',
    'negativeList': '负面清单（选填）',
    'regularTeaching': '日常教学',
    'highlights': '亮点工作（选填）',
    'teachingOfficeId': '教研室编号',
    'evaluationYear': '考评年度'
  }
  return titles[sk] || sk
}

// Helper: Get item label
const getItemLabel = (itemKey: string | number): string => {
  const ik = String(itemKey)
  // 完整的字段名映射
  const labels: Record<string, string> = {
    // 正面清单
    'teachingHonors': '教学荣誉',
    'teachingCompetitions': '教学竞赛',
    'innovationCompetitions': '创新创业竞赛',
    'teachingReformProjects': '教学改革项目',
    'teachingAchievements': '教学成果',
    'courseConstruction': '课程建设',
    'textbookConstruction': '教材建设',
    'teachingTeamBuilding': '教学团队建设',
    'facultyTraining': '师资培训',
    'practiceBaseConstruction': '实践基地建设',
    'laboratoryConstruction': '实验室建设',
    'teachingFacilityImprovement': '教学设施改善',
    // 负面清单
    'ideologyIssues': '意识形态问题',
    'ethicsViolations': '师德师风问题',
    'teachingAccidents': '教学事故',
    'workloadIncomplete': '工作量不完整',
    // 教学管理相关
    'educationResearch': '教育教学研究',
    'researchAndExchange': '教研与交流',
    'teacherTeamBuilding': '教师队伍建设',
    'teachingProcessManagement': '教学过程管理',
    'teachingQualityManagement': '教学质量管理',
    'courseAssessment': '课程考核',
    'regularTeaching': '日常教学',
    'highlights': '亮点工作',
    // 基本信息
    'teachingOfficeId': '教研室编号',
    'evaluationYear': '考评年度',
    'submittedAt': '提交时间',
    'status': '状态',
    // 其他可能的字段
    'description': '描述',
    'content': '内容',
    'selfScore': '自评分',
    'evidence': '佐证材料',
    'remarks': '备注',
    'summary': '总结',
    'achievements': '成果',
    'problems': '存在问题',
    'improvements': '改进措施',
    'plans': '工作计划'
  }
  
  // 如果有映射，返回中文
  if (labels[ik]) {
    return labels[ik]
  }
  
  // 尝试从 item1_1 格式提取
  const match = ik.match(/item(\d+)_(\d+)/)
  if (match) {
    return `${match[1]}.${match[2]}`
  }
  
  // 返回原始key
  return ik
}

// Helper: Format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化日期时间
const formatDateTime = (date: string | number | Date): string => {
  if (!date) return '-'
  const d = new Date(date)
  
  // Check if date is valid
  if (isNaN(d.getTime())) {
    return String(date) || '-'
  }

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// Check if user has already submitted on mount
onMounted(async () => {
  // Load all data
  await Promise.all([
    loadSelfEvaluation(),  // 这个函数内部会调用 initializeFormData()
    loadAttachments()
  ])
  // 进入页面时检查当前用户是否已提交过评分，并拉取所有评分用于显示评教小组平均分
  try {
    const res = await scoringApi.getAllScores(props.evaluationId)
    const data = res.data
    if (data) {
      allScoresData.value = data
      if (data.manual_scores?.length && props.currentUserRole) {
        const currentUserId = localStorage.getItem('userId') || ''
        const already = data.manual_scores.some(
          (score: { reviewer_id: string }) => String(score.reviewer_id) === String(currentUserId)
        )
        if (already) hasSubmitted.value = true
      }
    }
  } catch (_) {
    // 仅用于设置 hasSubmitted，忽略错误
  }
})

// Expose methods
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  getFormData: () => ({ ...formData })
})
</script>

<style scoped>
.manual-scoring-form {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 0;
}

.scoring-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.weight-alert {
  margin-bottom: 20px;
}

/* Integrated Scoring Styles */
.integrated-scoring {
  padding: 20px 0;
}

.evaluation-content {
  padding: 10px 0;
}

.content-section {
  margin-bottom: 40px;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
}

.section-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-item-with-scoring {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  padding: 20px;
  background-color: #f9fafc;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

@media (max-width: 1200px) {
  .content-item-with-scoring {
    grid-template-columns: 1fr;
  }
}

/* Item Content Area */
.item-content-area {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.item-label {
  font-weight: 600;
  color: #606266;
  font-size: 15px;
}

.item-content {
  color: #303133;
  line-height: 1.8;
  font-size: 14px;
  white-space: pre-wrap;
  padding: 15px;
  background-color: white;
  border-radius: 6px;
  border-left: 3px solid #409eff;
}

/* Item Attachments */
.item-attachments {
  margin-top: 10px;
  padding: 15px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.attachments-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #606266;
  font-size: 14px;
}

.attachments-header .el-icon {
  font-size: 16px;
  color: #409eff;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.attachment-item:hover {
  background-color: #e4e7ed;
}

.file-icon {
  font-size: 18px;
  color: #409eff;
  flex-shrink: 0;
}

.file-name {
  flex: 1;
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}

/* Scoring Area */
.scoring-area {
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  border: 2px solid #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

/* Scoring Header */
.scoring-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.scoring-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* Scoring Attachments (compact version in scoring area) */
.scoring-attachments {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.attachments-header-small {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #606266;
  font-size: 13px;
}

.attachments-header-small .el-icon {
  font-size: 14px;
  color: #409eff;
}

.attachment-list-compact {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.attachment-item-compact {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background-color: white;
  border-radius: 4px;
  transition: background-color 0.3s;
  font-size: 13px;
}

.attachment-item-compact:hover {
  background-color: #ecf5ff;
}

.file-icon-small {
  font-size: 16px;
  color: #409eff;
  flex-shrink: 0;
}

.file-name-small {
  flex: 1;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scoring-area .el-form {
  margin: 0;
}

.scoring-area .el-form-item {
  margin-bottom: 18px;
}

.scoring-area .el-form-item:last-child {
  margin-bottom: 0;
}

.score-input {
  width: 120px;
}

.score-hint {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}

.total-score-section {
  margin: 40px 0 30px 0;
}

.total-score {
  text-align: center;
  font-size: 24px;
  padding: 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.total-score .label {
  font-weight: normal;
}

.total-score .value {
  font-weight: bold;
  font-size: 36px;
  margin: 0 10px;
}

.total-score .max {
  font-size: 18px;
  opacity: 0.9;
}

.manual-avg-score {
  text-align: center;
  font-size: 16px;
  padding: 14px 25px;
  margin-top: 12px;
  background: rgba(103, 194, 58, 0.15);
  border: 1px solid rgba(103, 194, 58, 0.4);
  border-radius: 8px;
  color: #2d5a27;
}
.manual-avg-score .label { font-weight: 500; }
.manual-avg-score .value { font-weight: bold; font-size: 20px; margin: 0 6px; }
.manual-avg-score .meta { font-size: 13px; color: #606266; }

.form-actions {
  margin-top: 30px;
  text-align: center;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.submit-office-section {
  margin-top: 30px;
}

.submit-office-info {
  text-align: center;
}

/* All Scores Dialog Styles */
.all-scores-dialog {
  max-height: 80vh;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.all-scores-content {
  max-height: 70vh;
  overflow-y: auto;
}

.score-card {
  margin-bottom: 20px;
}

.score-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.ai-score-card {
  border: 2px solid #67c23a;
}

.manual-score-card {
  border: 2px solid #e6a23c;
}

.evaluation-team-card {
  border: 2px solid #f56c6c;
  background-color: #fef0f0;
}

.final-score-card {
  border: 2px solid #f56c6c;
}

.reviewer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reviewer-info h3 {
  margin: 0;
}

.role-tag {
  font-weight: bold;
}

.weight-tag {
  font-size: 12px;
}

.submit-time {
  font-size: 14px;
  color: #909399;
}

.score-details {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.score-item {
  flex: 1;
  min-width: 200px;
}

.score-item.full-width {
  flex-basis: 100%;
}

.score-item .label {
  font-weight: 600;
  color: #606266;
  margin-right: 8px;
}

.score-item .value {
  color: #303133;
}

.score-item .value.highlight {
  color: #f56c6c;
  font-weight: bold;
  font-size: 20px;
}

.score-item .value.large {
  font-size: 28px;
}

.summary-text {
  margin-top: 8px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  line-height: 1.6;
  color: #606266;
}

.indicator-scores {
  margin-top: 20px;
}

.indicator-scores h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
}

.indicator-score-item {
  padding: 12px;
  margin-bottom: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.indicator-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.indicator-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.indicator-score {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}

.indicator-reasoning,
.indicator-comment {
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
  margin-top: 4px;
}

.manual-scores-section {
  margin-top: 30px;
}

.section-title {
  margin: 20px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.manual-score-details {
  padding: 10px 0;
}

.total-score-row {
  text-align: right;
  font-size: 18px;
  padding: 10px 0;
}

.total-score-row .label {
  font-weight: 600;
  color: #606266;
  margin-right: 10px;
}

.total-score-row .value {
  color: #f56c6c;
  font-weight: bold;
  font-size: 20px;
}
</style>
