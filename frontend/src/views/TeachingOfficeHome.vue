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
          <div v-if="activeMenu === 0 && !authStore.teachingOfficeId" class="no-office-warning">
            <el-result
              icon="warning"
              title="账号未关联教研室"
              sub-title="您的账号尚未关联教研室，请联系系统管理员配置教研室信息后再提交自评表。"
            />
          </div>
          <NewSelfEvaluationForm
            v-else-if="activeMenu === 0 && authStore.teachingOfficeId"
            :teaching-office-id="authStore.teachingOfficeId"
            :evaluation-year="new Date().getFullYear()"
            @submit="handleSubmit"
          />
          
          <!-- 结果查看 -->
          <div v-if="activeMenu === 1" class="result-view">
            <el-card class="results-list-card" v-loading="resultsLoading">
              <template #header>
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <h3>历年考评结果</h3>
                  <el-button type="default" size="small" @click="loadPublishedResults">刷新</el-button>
                </div>
              </template>

              <!-- 已发布结果列表 -->
              <div v-if="publishedResults.length > 0" class="evaluation-results-list">
                <el-card
                  v-for="result in publishedResults"
                  :key="result.evaluation_id"
                  class="result-item"
                  shadow="hover"
                >
                  <div class="result-header">
                    <div class="result-title-section">
                      <h4 class="result-year">{{ result.evaluation_year }}年考评结果</h4>
                      <el-tag type="success">已公示</el-tag>
                    </div>
                    <el-button type="primary" link @click="viewResultDetail(result)">
                      查看详情
                      <el-icon><ArrowRight /></el-icon>
                    </el-button>
                  </div>
                  <div class="result-summary">
                    <el-descriptions :column="2" border size="small">
                      <el-descriptions-item label="最终得分">
                        <span class="final-score">{{ result.final_score?.final_score?.toFixed(1) ?? '-' }} 分</span>
                      </el-descriptions-item>
                      <el-descriptions-item label="评审人数">
                        {{ result.manual_scores?.length ?? 0 }} 人
                      </el-descriptions-item>
                      <el-descriptions-item label="教研室">
                        {{ result.teaching_office_name }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-card>
              </div>

              <!-- 无结果时的提示 -->
              <div v-else class="no-results">
                <el-card class="result-item" shadow="hover">
                  <div class="result-header">
                    <div class="result-title-section">
                      <h4 class="result-year">{{ new Date().getFullYear() }}年考评结果</h4>
                      <el-tag type="warning">考评未完成</el-tag>
                    </div>
                  </div>
                  <div class="result-pending">
                    <el-alert
                      title="考评尚未完成，无法查看"
                      type="info"
                      :closable="false"
                      show-icon
                    >
                      <p>当前考评工作尚未完成，请等待考评小组办公室发起公示后查看结果</p>
                      <p style="margin-top: 10px;">
                        预计公示时间：{{ estimatedPublishDate }}
                      </p>
                    </el-alert>
                  </div>
                </el-card>
              </div>
            </el-card>

            <!-- 结果详情弹窗 -->
            <el-dialog
              v-model="resultDetailVisible"
              :title="`${selectedResult?.evaluation_year ?? ''}年考评结果详情`"
              width="700px"
            >
              <div v-if="selectedResult">
                <el-descriptions :column="2" border style="margin-bottom:20px">
                  <el-descriptions-item label="教研室">{{ selectedResult.teaching_office_name }}</el-descriptions-item>
                  <el-descriptions-item label="考评年度">{{ selectedResult.evaluation_year }}</el-descriptions-item>
                  <el-descriptions-item label="最终得分">
                    <span class="final-score-big">{{ selectedResult.final_score?.final_score?.toFixed(1) ?? '-' }} 分</span>
                  </el-descriptions-item>
                </el-descriptions>

                <h4 style="margin-bottom:12px">评审人打分记录</h4>
                <el-table :data="selectedResult.manual_scores || []" border size="small">
                  <el-table-column prop="reviewer_name" label="评审人" width="140" />
                  <el-table-column prop="reviewer_role" label="角色" width="120">
                    <template #default="{ row }">
                      <el-tag size="small">{{ row.reviewer_role }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="提交时间">
                    <template #default="{ row }">
                      {{ row.submitted_at ? new Date(row.submitted_at).toLocaleString('zh-CN') : '-' }}
                    </template>
                  </el-table-column>
                </el-table>

                <div v-if="selectedResult.final_score?.summary" style="margin-top:16px">
                  <h4>感悟总结</h4>
                  <el-card shadow="never" style="background:#f9f9f9;margin-top:8px">
                    <p>{{ selectedResult.final_score.summary }}</p>
                  </el-card>
                </div>
              </div>
              <template #footer>
                <el-button @click="resultDetailVisible = false">关闭</el-button>
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
import { selfEvaluationApi, resultApi } from '@/api/client'
import { 
  User,
  EditPen,
  ArrowRight,
  SwitchButton,
  View
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 在组件挂载时加载认证信息
onMounted(async () => {
  authStore.loadFromStorage()
  
  // 检查是否已登录
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  // 加载已发布结果
  await loadPublishedResults()
})

const activeMenu = ref(0)
const activeTab = ref(0)

// 保存当前的evaluation_id，用于附件上传
const currentEvaluationId = ref<string>('')

// 考评状态（保留兼容性）
const estimatedPublishDate = ref('2026-07-15') // 预计公示时间

// 已发布结果
const publishedResults = ref<any[]>([])
const resultsLoading = ref(false)
const resultDetailVisible = ref(false)
const selectedResult = ref<any>(null)

const loadPublishedResults = async () => {
  if (!authStore.teachingOfficeId) return
  resultsLoading.value = true
  try {
    const res = await resultApi.getPublishedResults(authStore.teachingOfficeId)
    publishedResults.value = Array.isArray(res.data) ? res.data : []
  } catch (e: any) {
    console.warn('加载考评结果失败:', e.message)
    publishedResults.value = []
  } finally {
    resultsLoading.value = false
  }
}

// 查看结果详情
const viewResultDetail = (result: any) => {
  selectedResult.value = result
  resultDetailVisible.value = true
}

// 判断是否显示表单（第一个、第二个菜单）
const shouldShowForm = computed(() => {
  return activeMenu.value === 0 || activeMenu.value === 1
})

// 菜单项（只有教研室）
const menuItems = ref([
  { name: '填写自评表', icon: markRaw(EditPen) },
  { name: '结果查看', icon: markRaw(View) }
])

// 标签页配置（只有教研室）
const tabsConfig = [
  [
    { name: '教研室工作考核评分表', icon: markRaw(EditPen), description: '填写教研室工作考核评分表' }
  ],
  [
    { name: '评分结果', icon: markRaw(View), description: '查看自评表评分结果' }
  ]
]

// 功能配置（只有教研室）
const functionsConfig = [
  [], // 第一个菜单显示自评表表单
  []  // 第二个菜单显示附件管理表单
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
  router.push('/')
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
    router.push('/')
  })
}

// 自评表表单处理函数
const handleSubmit = async (submitData: any) => {
  let loadingMessage: any = null
  
  // 检查 teachingOfficeId 是否存在
  if (!authStore.teachingOfficeId) {
    ElMessage.error('您的账号未关联教研室，无法提交自评表。请联系管理员。')
    return
  }

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
      teaching_office_id: authStore.teachingOfficeId,
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

</script>

<style scoped>
/* 未关联教研室的警告提示 */
.no-office-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 2rem;
}

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
