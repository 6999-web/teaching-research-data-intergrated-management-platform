<template>
  <div class="platform-layout" :class="`role-${authStore.userRole}`">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="sidebar-header" @click="goToHome">
        <img src="/school-logo.jpg" alt="校徽" class="sidebar-logo" />
        <h2 class="sidebar-title">教研室端</h2>
        <div class="role-badge">{{ authStore.roleName }}</div>
      </div>
      
      <div class="sidebar-menu">
        <div 
          v-for="(item, index) in menuItems" 
          :key="index"
          class="menu-item"
          :class="{ active: activeMenu === index }"
          @click="selectMenu(index)"
        >
          <el-icon class="menu-icon">
            <component :is="item.icon" />
          </el-icon>
          <span class="menu-text">{{ item.name }}</span>
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <el-icon class="user-avatar"><User /></el-icon>
          <div class="user-details">
            <span class="user-name">{{ authStore.userName }}</span>
            <span class="user-role-text">{{ authStore.roleName }}</span>
          </div>
        </div>
        <el-button class="logout-btn" @click="handleLogout" text>
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </div>

    <!-- 右侧主内容区 -->
    <div class="main-content">
      <!-- 顶部标签栏 -->
      <div class="content-tabs">
        <div 
          v-for="(tab, index) in currentTabs" 
          :key="index"
          class="tab-item"
          :class="{ active: activeTab === index }"
          @click="activeTab = index"
        >
          <el-icon class="tab-icon">
            <component :is="tab.icon" />
          </el-icon>
          <span class="tab-text">{{ tab.name }}</span>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="content-area">
        <div class="content-header">
          <h2 class="content-title">{{ currentTabs[activeTab]?.name }}</h2>
          <p class="content-subtitle">{{ currentTabs[activeTab]?.description }}</p>
        </div>

        <!-- 根据菜单显示不同内容 -->
        <div v-if="shouldShowForm" class="form-container">
          <!-- 填写自评表 -->
          <NewSelfEvaluationForm
            v-if="activeMenu === 0"
            :teaching-office-id="authStore.teachingOfficeId || 'a1b2c3d4-e5f6-4a5b-8c9d-111111111111'"
            :evaluation-year="new Date().getFullYear()"
            @submit="handleSubmit"
          />
          
          <!-- 结果查看 -->
          <div v-if="activeMenu === 1" class="result-view">
            <el-card class="results-list-card">
              <template #header>
                <h3>历年考评结果</h3>
              </template>

              <!-- 考评结果列表 -->
              <div class="evaluation-results-list">
                <!-- 2026年考评结果 -->
                <el-card class="result-item" shadow="hover">
                  <div class="result-header">
                    <div class="result-title-section">
                      <h4 class="result-year">2026年考评结果</h4>
                      <el-tag v-if="!evaluationPublished" type="warning">考评未完成</el-tag>
                      <el-tag v-else type="success">已公示</el-tag>
                    </div>
                    <el-button 
                      v-if="evaluationPublished" 
                      type="primary" 
                      link
                      @click="viewResultDetail(2026)"
                    >
                      查看详情
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                  </div>

                  <!-- 未完成状态 -->
                  <div v-if="!evaluationPublished" class="result-pending">
                    <el-alert
                      title="考评尚未完成，无法查看"
                      type="info"
                      :closable="false"
                      show-icon
                    >
                      <p>当前考评工作尚未完成，请等待校长办公会公示后查看结果</p>
                      <p style="margin-top: 10px;">
                        <el-icon><Clock /></el-icon>
                        预计公示时间：{{ estimatedPublishDate }}
                      </p>
                    </el-alert>
                  </div>

                  <!-- 已完成状态 -->
                  <div v-else class="result-summary">
                    <el-descriptions :column="2" border size="small">
                      <el-descriptions-item label="常规教学工作">
                        <span class="score-value">80</span> 分
                      </el-descriptions-item>
                      <el-descriptions-item label="特色与亮点">
                        <span class="score-value">0</span> 分
                      </el-descriptions-item>
                      <el-descriptions-item label="负面清单扣分">
                        <span class="score-value negative">-0</span> 分
                      </el-descriptions-item>
                      <el-descriptions-item label="最终得分">
                        <span class="final-score">0</span> 分
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-card>

                <!-- 2025年考评结果（示例） -->
                <el-card class="result-item" shadow="hover">
                  <div class="result-header">
                    <div class="result-title-section">
                      <h4 class="result-year">2025年考评结果</h4>
                      <el-tag type="info">历史记录</el-tag>
                    </div>
                    <el-button type="primary" link @click="viewResultDetail(2025)">
                      查看详情
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                  </div>

                  <div class="result-summary">
                    <el-descriptions :column="2" border size="small">
                      <el-descriptions-item label="常规教学工作">
                        <span class="score-value">85</span> 分
                      </el-descriptions-item>
                      <el-descriptions-item label="特色与亮点">
                        <span class="score-value">10</span> 分
                      </el-descriptions-item>
                      <el-descriptions-item label="负面清单扣分">
                        <span class="score-value negative">-0</span> 分
                      </el-descriptions-item>
                      <el-descriptions-item label="最终得分">
                        <span class="final-score">95</span> 分
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-card>
              </div>
            </el-card>
          </div>
          
          <!-- 下学期改进措施 -->
          <div v-if="activeMenu === 2" class="improvement-form">
            <el-card class="improvements-list-card">
              <template #header>
                <h3>历年改进措施</h3>
              </template>

              <!-- 改进措施列表 -->
              <div class="improvement-plans-list">
                <!-- 2026年改进措施 -->
                <el-card class="improvement-item" shadow="hover">
                  <div class="improvement-header">
                    <div class="improvement-title-section">
                      <h4 class="improvement-year">2026年下学期改进措施</h4>
                      <el-tag v-if="!evaluationCompleted" type="warning">考评未完成</el-tag>
                      <el-tag v-else-if="improvementSubmitted" type="success">已提交</el-tag>
                      <el-tag v-else type="info">待填写</el-tag>
                    </div>
                    <el-button 
                      v-if="evaluationCompleted && !improvementSubmitted" 
                      type="primary"
                      @click="showImprovementForm = true"
                    >
                      填写改进措施
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button 
                      v-else-if="improvementSubmitted" 
                      type="primary" 
                      link
                      @click="viewImprovementDetail(2026)"
                    >
                      查看详情
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                  </div>

                  <!-- 未完成状态 -->
                  <div v-if="!evaluationCompleted" class="improvement-pending">
                    <el-alert
                      title="考评尚未完成，无法填写"
                      type="info"
                      :closable="false"
                      show-icon
                    >
                      <p>请等待考评完成后再填写下学期改进措施</p>
                      <p style="margin-top: 10px;">
                        <el-icon><Clock /></el-icon>
                        预计可填写时间：{{ estimatedImprovementDate }}
                      </p>
                    </el-alert>
                  </div>

                  <!-- 已提交状态 -->
                  <div v-else-if="improvementSubmitted" class="improvement-summary">
                    <el-descriptions :column="1" border size="small">
                      <el-descriptions-item label="提交时间">
                        2026-07-15 14:30:00
                      </el-descriptions-item>
                      <el-descriptions-item label="改进措施数量">
                        {{ improvementPlans.length }} 项
                      </el-descriptions-item>
                      <el-descriptions-item label="状态">
                        <el-tag type="success">已提交到考评小组</el-tag>
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>

                  <!-- 待填写状态 -->
                  <div v-else class="improvement-todo">
                    <el-empty 
                      description="尚未填写改进措施，点击上方按钮开始填写"
                      :image-size="100"
                    />
                  </div>
                </el-card>

                <!-- 2025年改进措施（示例） -->
                <el-card class="improvement-item" shadow="hover">
                  <div class="improvement-header">
                    <div class="improvement-title-section">
                      <h4 class="improvement-year">2025年下学期改进措施</h4>
                      <el-tag type="info">历史记录</el-tag>
                    </div>
                    <el-button type="primary" link @click="viewImprovementDetail(2025)">
                      查看详情
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                  </div>

                  <div class="improvement-summary">
                    <el-descriptions :column="1" border size="small">
                      <el-descriptions-item label="提交时间">
                        2025-07-10 10:20:00
                      </el-descriptions-item>
                      <el-descriptions-item label="改进措施数量">
                        3 项
                      </el-descriptions-item>
                      <el-descriptions-item label="状态">
                        <el-tag type="success">已完成</el-tag>
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-card>
              </div>
            </el-card>

            <!-- 改进措施填写对话框 -->
            <el-dialog
              v-model="showImprovementForm"
              title="填写2026年下学期改进措施"
              width="80%"
              :close-on-click-modal="false"
            >
              <el-card class="improvement-card">
                <template #header>
                  <div class="card-header">
                    <h3>改进措施表单</h3>
                    <el-button 
                      type="primary" 
                      @click="addImprovementPlan"
                      :disabled="improvementSubmitted"
                    >
                      <el-icon><Plus /></el-icon>
                      添加改进措施
                    </el-button>
                  </div>
                </template>

                <!-- 改进措施列表 -->
                <div v-if="improvementPlans.length > 0" class="plans-list">
                  <el-card 
                    v-for="(plan, index) in improvementPlans" 
                    :key="index"
                    class="plan-item"
                    shadow="hover"
                  >
                    <template #header>
                      <div class="plan-header">
                        <span class="plan-title">改进措施 {{ index + 1 }}</span>
                        <el-button 
                          type="danger" 
                          size="small" 
                          link
                          :disabled="improvementSubmitted"
                          @click="removeImprovementPlan(index)"
                        >
                          <el-icon><Delete /></el-icon>
                          删除
                        </el-button>
                      </div>
                    </template>

                    <el-form :model="plan" label-width="120px" label-position="left">
                      <el-form-item label="考核指标" required>
                        <el-select 
                          v-model="plan.indicator" 
                          placeholder="请选择考核指标"
                          style="width: 100%"
                          :disabled="improvementSubmitted"
                        >
                          <el-option label="教学过程管理" value="教学过程管理" />
                          <el-option label="教学质量管理" value="教学质量管理" />
                          <el-option label="课程考核" value="课程考核" />
                          <el-option label="教育教学科研工作" value="教育教学科研工作" />
                          <el-option label="课程建设" value="课程建设" />
                          <el-option label="教师队伍建设" value="教师队伍建设" />
                          <el-option label="科学研究与学术交流" value="科学研究与学术交流" />
                          <el-option label="教学档案室管理与建设" value="教学档案室管理与建设" />
                        </el-select>
                      </el-form-item>

                      <el-form-item label="薄弱项分析" required>
                        <el-input
                          v-model="plan.weakness"
                          type="textarea"
                          :rows="3"
                          placeholder="请分析本学期在该指标上存在的问题和不足"
                          maxlength="500"
                          show-word-limit
                          :disabled="improvementSubmitted"
                        />
                      </el-form-item>

                      <el-form-item label="改进目标" required>
                        <el-input
                          v-model="plan.target"
                          type="textarea"
                          :rows="2"
                          placeholder="请描述下学期要达到的具体目标"
                          maxlength="300"
                          show-word-limit
                          :disabled="improvementSubmitted"
                        />
                      </el-form-item>

                      <el-form-item label="具体措施" required>
                        <el-input
                          v-model="plan.measures"
                          type="textarea"
                          :rows="4"
                          placeholder="请详细说明为达成目标将采取的具体措施和行动计划"
                          maxlength="800"
                          show-word-limit
                          :disabled="improvementSubmitted"
                        />
                      </el-form-item>

                      <el-form-item label="预期效果" required>
                        <el-input
                          v-model="plan.effect"
                          type="textarea"
                          :rows="2"
                          placeholder="请描述实施这些措施后预期达到的效果"
                          maxlength="300"
                          show-word-limit
                          :disabled="improvementSubmitted"
                        />
                      </el-form-item>

                      <el-form-item label="责任人" required>
                        <el-input
                          v-model="plan.charger"
                          placeholder="请输入负责人姓名"
                          style="width: 200px"
                          :disabled="improvementSubmitted"
                        />
                      </el-form-item>

                      <el-form-item label="完成时限" required>
                        <el-date-picker
                          v-model="plan.deadline"
                          type="date"
                          placeholder="选择完成日期"
                          format="YYYY-MM-DD"
                          value-format="YYYY-MM-DD"
                          style="width: 200px"
                          :disabled="improvementSubmitted"
                        />
                      </el-form-item>
                    </el-form>
                  </el-card>
                </div>

                <!-- 空状态 -->
                <el-empty 
                  v-else 
                  description="暂无改进措施，点击上方按钮添加"
                  :image-size="120"
                />

                <!-- 提交按钮 -->
                <div v-if="improvementPlans.length > 0" class="form-actions">
                  <el-button 
                    type="primary" 
                    size="large"
                    :loading="submittingPlans"
                    :disabled="improvementSubmitted"
                    @click="submitImprovementPlans"
                  >
                    {{ improvementSubmitted ? '已提交到考评小组' : '提交改进措施' }}
                  </el-button>
                  <el-button 
                    size="large" 
                    :disabled="improvementSubmitted"
                    @click="resetImprovementPlans"
                  >
                    重置
                  </el-button>
                </div>

                <!-- 已提交提示 -->
                <el-alert
                  v-if="improvementSubmitted"
                  title="改进措施已提交"
                  type="success"
                  :closable="false"
                  show-icon
                  style="margin-top: 20px;"
                >
                  您的改进措施已成功提交到考评小组端，考评小组可以查看您的改进计划和完成情况。
                </el-alert>
              </el-card>

              <template #footer>
                <el-button @click="showImprovementForm = false">关闭</el-button>
              </template>
            </el-dialog>
          </div>
        </div>
        
        <!-- 功能卡片网格 -->
        <div v-else class="function-grid">
          <div 
            v-for="(func, index) in currentFunctions" 
            :key="index"
            class="function-card"
            @click="navigateTo(func.route)"
          >
            <div class="function-icon">
              <el-icon>
                <component :is="func.icon" />
              </el-icon>
            </div>
            <div class="function-info">
              <h3 class="function-title">{{ func.name }}</h3>
              <p class="function-desc">{{ func.description }}</p>
            </div>
            <el-icon class="function-arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 页脚 -->
      <div class="content-footer">
        <p>© 2024 教研室数据管理平台 | 版本 2.0.0</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, markRaw, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import NewSelfEvaluationForm from '@/components/NewSelfEvaluationForm.vue'
import { selfEvaluationApi } from '@/api/client'
import { 
  User,
  EditPen,
  Upload,
  ArrowRight,
  CircleCheck,
  FolderOpened,
  SwitchButton,
  View,
  Clock,
  Plus,
  Delete
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 在组件挂载时加载认证信息
onMounted(() => {
  authStore.loadFromStorage()
  
  // 检查是否已登录
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
  }
})

const activeMenu = ref(0)
const activeTab = ref(0)

// 保存当前的evaluation_id，用于附件上传
const currentEvaluationId = ref<string>('')

// 考评状态
const evaluationPublished = ref(false) // 是否已公示
const estimatedPublishDate = ref('2026-07-15') // 预计公示时间

// 改进措施状态
const evaluationCompleted = ref(false) // 考评是否完成（可以填写改进措施）
const estimatedImprovementDate = ref('2026-07-20') // 预计可填写改进措施时间
const improvementSubmitted = ref(false) // 改进措施是否已提交
const showImprovementForm = ref(false) // 是否显示改进措施填写对话框

// 改进措施数据结构
interface ImprovementPlan {
  indicator: string
  weakness: string
  target: string
  measures: string
  effect: string
  charger: string
  deadline: string
}

// 改进措施表单数据
const improvementPlans = ref<ImprovementPlan[]>([])
const submittingPlans = ref(false)

// 查看结果详情
const viewResultDetail = (year: number) => {
  ElMessage.info(`查看${year}年考评结果详情`)
  // TODO: 实现详情页面
}

// 查看改进措施详情
const viewImprovementDetail = (year: number) => {
  ElMessage.info(`查看${year}年改进措施详情`)
  // TODO: 实现详情页面
}

// 判断是否显示表单（第一个、第二个和第三个菜单）
const shouldShowForm = computed(() => {
  return activeMenu.value === 0 || activeMenu.value === 1 || activeMenu.value === 2
})

// 菜单项（只有教研室）
const menuItems = ref([
  { name: '填写自评表', icon: markRaw(EditPen) },
  { name: '结果查看', icon: markRaw(View) },
  { name: '下学期改进措施', icon: markRaw(CircleCheck) }
])

// 标签页配置（只有教研室）
const tabsConfig = [
  [
    { name: '教研室工作考核评分表', icon: markRaw(EditPen), description: '填写教研室工作考核评分表' }
  ],
  [
    { name: '评分结果', icon: markRaw(View), description: '查看自评表评分结果' }
  ],
  [
    { name: '下学期改进措施', icon: markRaw(CircleCheck), description: '查看下学期所有老师的改进措施' }
  ]
]

// 功能配置（只有教研室）
const functionsConfig = [
  [], // 第一个菜单显示自评表表单
  [], // 第二个菜单显示附件管理表单
  []  // 第三个菜单显示改进措施表格
]

const currentTabs = computed(() => {
  return tabsConfig[activeMenu.value] || []
})

const currentFunctions = computed(() => {
  return functionsConfig[activeMenu.value]?.[activeTab.value] || []
})

const selectMenu = async (index: number) => {
  activeMenu.value = index
  activeTab.value = 0
}

const goToHome = () => {
  activeMenu.value = 0
  activeTab.value = 0
}

const navigateTo = (route: string) => {
  if (route !== '#') {
    router.push(route).catch(err => {
      console.error('导航失败:', err)
    })
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.logout()
    router.push('/login')
  })
}

// 自评表表单处理函数
const handleSubmit = async (submitData: any) => {
  let loadingMessage: any = null
  
  try {
    // 显示加载提示
    loadingMessage = ElMessage({
      message: '正在提交自评表，请稍候...',
      type: 'info',
      duration: 0,
      showClose: false
    })
    
    // Extract form data and attachment upload function
    const { formData, attachments, uploadAttachments } = submitData
    
    // Step 1: Save self-evaluation
    const saveResponse = await selfEvaluationApi.save({
      teaching_office_id: authStore.teachingOfficeId || 'a1b2c3d4-e5f6-4a5b-8c9d-111111111111',
      evaluation_year: new Date().getFullYear(),
      content: formData
    })

    const evaluationId = saveResponse.data.evaluation_id

    // 保存evaluation_id供附件上传使用
    currentEvaluationId.value = evaluationId

    // Step 2: Upload attachments if any
    if (attachments && attachments.length > 0) {
      if (loadingMessage) loadingMessage.close()
      loadingMessage = ElMessage({
        message: '正在上传附件，请稍候...',
        type: 'info',
        duration: 0,
        showClose: false
      })
      
      const uploadSuccess = await uploadAttachments(evaluationId)
      if (!uploadSuccess) {
        if (loadingMessage) loadingMessage.close()
        ElMessage.warning('附件上传失败，但表单已保存。您可以稍后单独上传附件。')
        // Continue with submission even if attachment upload fails
      }
    }

    // Step 3: Submit and lock
    if (loadingMessage) loadingMessage.close()
    loadingMessage = ElMessage({
      message: '正在提交到考评小组，请稍候...',
      type: 'info',
      duration: 0,
      showClose: false
    })
    
    try {
      await selfEvaluationApi.submit(evaluationId)
    } catch (submitError: any) {
      if (loadingMessage) loadingMessage.close()
      console.error('Submit error:', submitError)
      
      // 如果是403错误，可能是权限问题
      if (submitError.response?.status === 403) {
        ElMessage.error('提交失败：没有权限。请确保您已正确登录。')
      } else {
        ElMessage.error(submitError.response?.data?.detail || '提交失败，请重试')
      }
      return
    }

    // Success
    if (loadingMessage) loadingMessage.close()
    ElMessage.success('提交成功！数据已上传到考评小组端')
    
  } catch (error: any) {
    if (loadingMessage) loadingMessage.close()
    console.error('Failed to submit self-evaluation:', error)
    
    if (error.response?.status === 401) {
      ElMessage.error('请先登录后再提交')
      // 跳转到登录页
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else if (error.response?.status === 403) {
      ElMessage.error('没有权限执行此操作，请检查登录状态')
    } else if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('提交失败，请检查网络连接或联系管理员')
    }
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    '待执行': 'info',
    '执行中': 'warning',
    '已完成': 'success',
    '已驳回': 'danger'
  }
  return typeMap[status] || 'info'
}

// 添加改进措施
const addImprovementPlan = () => {
  improvementPlans.value.push({
    indicator: '',
    weakness: '',
    target: '',
    measures: '',
    effect: '',
    charger: authStore.userName || '',
    deadline: ''
  })
}

// 删除改进措施
const removeImprovementPlan = (index: number) => {
  ElMessageBox.confirm('确定要删除这条改进措施吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    improvementPlans.value.splice(index, 1)
    ElMessage.success('删除成功')
  }).catch(() => {
    // 取消删除
  })
}

// 重置改进措施
const resetImprovementPlans = () => {
  ElMessageBox.confirm('确定要重置所有改进措施吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    improvementPlans.value = []
    ElMessage.success('重置成功')
  }).catch(() => {
    // 取消重置
  })
}

// 提交改进措施
const submitImprovementPlans = async () => {
  // 验证表单
  for (let i = 0; i < improvementPlans.value.length; i++) {
    const plan = improvementPlans.value[i]
    if (!plan.indicator) {
      ElMessage.warning(`请选择第 ${i + 1} 条改进措施的考核指标`)
      return
    }
    if (!plan.weakness) {
      ElMessage.warning(`请填写第 ${i + 1} 条改进措施的薄弱项分析`)
      return
    }
    if (!plan.target) {
      ElMessage.warning(`请填写第 ${i + 1} 条改进措施的改进目标`)
      return
    }
    if (!plan.measures) {
      ElMessage.warning(`请填写第 ${i + 1} 条改进措施的具体措施`)
      return
    }
    if (!plan.effect) {
      ElMessage.warning(`请填写第 ${i + 1} 条改进措施的预期效果`)
      return
    }
    if (!plan.charger) {
      ElMessage.warning(`请填写第 ${i + 1} 条改进措施的责任人`)
      return
    }
    if (!plan.deadline) {
      ElMessage.warning(`请选择第 ${i + 1} 条改进措施的完成时限`)
      return
    }
  }

  // 确认提交
  try {
    await ElMessageBox.confirm(
      '提交后改进措施将发送到考评小组端，考评小组可以查看您的改进计划和完成情况。确定要提交吗？',
      '确认提交',
      {
        confirmButtonText: '确定提交',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return // 用户取消
  }

  submittingPlans.value = true
  
  try {
    // TODO: 调用API提交改进措施到考评小组端
    // await improvementApi.submitToEvaluationTeam({
    //   teaching_office_id: authStore.teachingOfficeId,
    //   evaluation_year: new Date().getFullYear(),
    //   plans: improvementPlans.value
    // })
    
    // 模拟提交
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 标记为已提交
    improvementSubmitted.value = true
    
    ElMessage.success('改进措施已成功提交到考评小组端！')
    
  } catch (error: any) {
    console.error('Failed to submit improvement plans:', error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submittingPlans.value = false
  }
}
</script>

<style scoped>
/* 使用与 Home.vue 相同的样式 */
.platform-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
  overflow-x: hidden;
  max-width: 100vw;
}

.sidebar {
  width: 220px;
  background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
}

.sidebar-header {
  padding: 1.5rem 1rem;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: background 0.3s;
}

.sidebar-header:hover {
  background: rgba(255, 255, 255, 0.05);
}

.sidebar-logo {
  width: 60px;
  height: 60px;
  object-fit: contain;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.sidebar-title {
  color: white;
  font-size: 1rem;
  font-weight: 600;
  margin: 0.5rem 0;
}

.role-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-top: 0.5rem;
}

.sidebar-menu {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.menu-item.active {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-left-color: #7cb342;
}

.role-teacher .menu-item.active {
  border-left-color: #42a5f5;
}

.role-director .menu-item.active {
  border-left-color: #66bb6a;
}

.role-college_leader .menu-item.active {
  border-left-color: #ab47bc;
}

.menu-icon {
  font-size: 1.3rem;
  margin-right: 0.75rem;
}

.menu-text {
  font-size: 0.95rem;
  font-weight: 500;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  color: white;
  margin-bottom: 0.5rem;
}

.user-avatar {
  font-size: 2rem;
  margin-right: 0.75rem;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.95rem;
  font-weight: 600;
}

.user-role-text {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
}

.logout-btn {
  width: 100%;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 0.5rem;
}

.logout-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.main-content {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  overflow-x: hidden;
  max-width: calc(100vw - 220px);
}

.content-tabs {
  background: white;
  display: flex;
  padding: 0 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.tab-item {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  cursor: pointer;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s;
}

.tab-item:hover {
  color: #1a237e;
  background: #f5f7fa;
}

.tab-item.active {
  color: #1a237e;
  border-bottom-color: #1a237e;
  font-weight: 600;
}

.tab-icon {
  font-size: 1.2rem;
  margin-right: 0.5rem;
}

.tab-text {
  font-size: 0.95rem;
}

.content-area {
  flex: 1;
  padding: 2rem;
  background: #f5f7fa;
  overflow-x: hidden;
  max-width: 100%;
}

.content-header {
  margin-bottom: 2rem;
}

.content-title {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.content-subtitle {
  font-size: 1rem;
  color: #666;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.function-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.function-card:hover {
  border-color: #1a237e;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(26, 35, 126, 0.15);
}

.function-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.function-info {
  flex: 1;
}

.function-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.3rem;
}

.function-desc {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.4;
}

.function-arrow {
  font-size: 1.5rem;
  color: #1a237e;
  opacity: 0;
  transition: opacity 0.3s;
}

.function-card:hover .function-arrow {
  opacity: 1;
}

.content-footer {
  background: white;
  padding: 2rem;
  text-align: center;
  border-top: 1px solid #e5e7eb;
  color: #666;
  font-size: 0.9rem;
}

.form-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow-x: auto;
  max-width: 100%;
}

.improvement-list {
  width: 100%;
  overflow-x: auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.list-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

:deep(.el-table) {
  font-size: 14px;
  width: 100%;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table__body-wrapper) {
  overflow-x: auto;
}

/* 表格列宽度控制 */
:deep(.el-table .el-table__cell) {
  padding: 12px 8px;
}

/* 表格内容超长时显示省略号 */
:deep(.el-table .cell) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 表格容器滚动 */
:deep(.el-table__body-wrapper) {
  overflow-x: auto;
}

/* 固定列阴影效果 */
:deep(.el-table__fixed),
:deep(.el-table__fixed-right) {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.12);
}

@media (max-width: 1024px) {
  .function-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  
  .sidebar-title,
  .menu-text,
  .user-details,
  .role-badge {
    display: none;
  }
  
  .main-content {
    margin-left: 60px;
  }
}

/* 结果查看页面样式 */
.result-view {
  width: 100%;
}

.score-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.score-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-card .card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.score-value {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.score-value.negative {
  color: #F56C6C;
}

.final-score {
  font-size: 28px;
  font-weight: bold;
  color: #67C23A;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.feedback-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.feedback-card h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

/* 考评未完成状态 */
.evaluation-pending {
  width: 100%;
}

.evaluation-pending :deep(.el-result__title) {
  font-size: 24px;
  color: #409EFF;
}

.evaluation-pending :deep(.el-result__subtitle) {
  font-size: 16px;
  margin-top: 10px;
}

.evaluation-pending ol {
  text-align: left;
  line-height: 2;
}

.evaluation-pending ol li {
  margin: 5px 0;
}

/* 改进措施未完成状态 */
.evaluation-not-completed {
  width: 100%;
}

.evaluation-not-completed :deep(.el-result__title) {
  font-size: 24px;
  color: #E6A23C;
}

.evaluation-not-completed :deep(.el-result__subtitle) {
  font-size: 16px;
  margin-top: 10px;
}

.evaluation-not-completed ol {
  text-align: left;
  line-height: 2;
}

.evaluation-not-completed ol li {
  margin: 5px 0;
}

/* 改进措施表单 */
.improvement-form {
  width: 100%;
}

.improvement-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.improvement-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.improvement-card .card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.plans-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.plan-item {
  border: 1px solid #e5e7eb;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

/* 结果查看列表样式 */
.results-list-card,
.improvements-list-card {
  margin: 20px 0;
}

.evaluation-results-list,
.improvement-plans-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-item,
.improvement-item {
  transition: transform 0.2s;
}

.result-item:hover,
.improvement-item:hover {
  transform: translateY(-2px);
}

.result-header,
.improvement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.result-title-section,
.improvement-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-year,
.improvement-year {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.result-pending,
.improvement-pending {
  padding: 10px 0;
}

.result-summary,
.improvement-summary {
  margin-top: 15px;
}

.improvement-todo {
  padding: 20px 0;
}
</style>
