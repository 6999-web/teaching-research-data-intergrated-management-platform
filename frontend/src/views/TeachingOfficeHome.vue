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
          
          <!-- 材料提交（附件管理） -->
          <AttachmentUpload
            v-if="activeMenu === 1"
            :evaluation-id="currentEvaluationId || 'a1b2c3d4-e5f6-4a5b-8c9d-000000000000'"
            :evaluation-year="new Date().getFullYear()"
            :is-locked="false"
            @submit="handleAttachmentSubmit"
            @back="handleAttachmentBack"
          />
          
          <!-- 下学期改进措施 -->
          <div v-if="activeMenu === 2" class="improvement-list">
            <div class="list-header">
              <h3>下学期所有老师的改进措施</h3>
              <el-tag type="info">共 {{ improvementPlans.length }} 条</el-tag>
            </div>
            
            <el-table :data="improvementPlans" style="width: 100%" stripe>
              <el-table-column prop="teacher_name" label="教师" width="100" fixed />
              <el-table-column prop="indicator" label="考核指标" width="120" show-overflow-tooltip />
              <el-table-column prop="weakness" label="薄弱项分析" min-width="150" show-overflow-tooltip />
              <el-table-column prop="target" label="改进目标" min-width="140" show-overflow-tooltip />
              <el-table-column prop="measures" label="具体措施" min-width="150" show-overflow-tooltip />
              <el-table-column prop="effect" label="预期效果" min-width="120" show-overflow-tooltip />
              <el-table-column prop="charger" label="责任人" width="90" />
              <el-table-column prop="deadline" label="完成时限" width="110" />
              <el-table-column prop="status" label="状态" width="90" fixed="right">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)" size="small">
                    {{ scope.row.status }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
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
import AttachmentUpload from '@/components/AttachmentUpload.vue'
import { selfEvaluationApi } from '@/api/client'
import { 
  User,
  EditPen,
  Upload,
  ArrowRight,
  CircleCheck,
  FolderOpened,
  SwitchButton,
  View
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

// 改进措施数据
const improvementPlans = ref([
  {
    teacher_name: '张三',
    indicator: '教学过程管理',
    weakness: '课堂纪律管理不够严格，部分学生上课玩手机现象较为普遍',
    target: '下学期将课堂纪律管理纳入日常教学考核，学生专注度提升20%以上',
    measures: '制定明确的课堂纪律规范；采用课堂互动教学法；建立课堂表现记录制度',
    effect: '课堂纪律明显改善，学生专注度和学习效果显著提升',
    charger: '张三',
    deadline: '2026-06-30',
    status: '执行中'
  },
  {
    teacher_name: '李四',
    indicator: '课程建设',
    weakness: '教学资源更新不及时，部分课件内容陈旧，缺少最新的行业案例',
    target: '下学期完成课程资源全面更新，引入至少10个最新行业案例',
    measures: '每月关注行业最新动态；与企业建立合作关系；重新制作核心章节课件',
    effect: '课程内容更加贴近行业实际，学生学习兴趣和就业竞争力明显提升',
    charger: '李四',
    deadline: '2026-07-15',
    status: '待执行'
  },
  {
    teacher_name: '王五',
    indicator: '教学改革项目',
    weakness: '教学改革项目申报数量不足，缺乏对教学改革的系统性研究',
    target: '下学期至少申报2项校级教学改革项目，并完成1项项目的中期研究',
    measures: '组建教学改革研究小组；定期开展教学研讨会；学习借鉴其他院校经验',
    effect: '教学改革意识和能力显著提升，形成可推广的教学改革成果',
    charger: '王五',
    deadline: '2026-08-30',
    status: '待执行'
  },
  {
    teacher_name: '赵六',
    indicator: '教学质量',
    weakness: '学生评教分数偏低，主要反映在教学方法单一、师生互动不足',
    target: '下学期学生评教分数提升至90分以上，课堂互动频次增加50%',
    measures: '学习并应用多种教学方法；增加课堂讨论和小组活动；建立课后答疑机制',
    effect: '教学质量明显提升，学生满意度大幅提高，形成良好的师生互动氛围',
    charger: '赵六',
    deadline: '2026-06-30',
    status: '执行中'
  },
  {
    teacher_name: '孙七',
    indicator: '科研工作',
    weakness: '论文发表数量较少，科研成果转化率低，缺乏高水平科研项目支撑',
    target: '下学期完成2篇核心期刊论文投稿，申报1项省级科研项目',
    measures: '制定详细的科研计划；加强与科研团队的合作；参加学术会议拓展视野',
    effect: '科研能力和水平显著提升，形成稳定的科研产出机制',
    charger: '孙七',
    deadline: '2026-08-31',
    status: '待执行'
  }
])

// 判断是否显示表单（第一个、第二个和第三个菜单）
const shouldShowForm = computed(() => {
  return activeMenu.value === 0 || activeMenu.value === 1 || activeMenu.value === 2
})

// 菜单项（只有教研室）
const menuItems = ref([
  { name: '填写自评表', icon: markRaw(EditPen) },
  { name: '材料提交', icon: markRaw(Upload) },
  { name: '下学期改进措施', icon: markRaw(CircleCheck) }
])

// 标签页配置（只有教研室）
const tabsConfig = [
  [
    { name: '教研室工作考核评分表', icon: markRaw(EditPen), description: '填写教研室工作考核评分表' }
  ],
  [
    { name: '附件列表', icon: markRaw(FolderOpened), description: '查看和提交附件' }
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
  
  // 如果切换到材料提交页面，且还没有evaluation_id，先创建草稿
  if (index === 1 && !currentEvaluationId.value) {
    try {
      const saveResponse = await selfEvaluationApi.save({
        teaching_office_id: authStore.teachingOfficeId || 'a1b2c3d4-e5f6-4a5b-8c9d-111111111111',
        evaluation_year: new Date().getFullYear(),
        content: {} // 空内容，创建草稿
      })
      currentEvaluationId.value = saveResponse.data.evaluation_id
    } catch (error) {
      console.error('Failed to create draft evaluation:', error)
      ElMessage.error('无法创建自评表草稿，请先填写自评表')
      activeMenu.value = 0 // 返回到自评表页面
    }
  }
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
const handleSubmit = async (formData: any) => {
  try {
    // 显示加载提示
    const loadingMessage = ElMessage({
      message: '正在提交自评表，请稍候...',
      type: 'info',
      duration: 0,
      showClose: false
    })
    
    // Step 1: Save self-evaluation
    const saveResponse = await selfEvaluationApi.save({
      teaching_office_id: authStore.teachingOfficeId || 'a1b2c3d4-e5f6-4a5b-8c9d-111111111111',
      evaluation_year: new Date().getFullYear(),
      content: formData
    })

    const evaluationId = saveResponse.data.evaluation_id

    // 保存evaluation_id供附件上传使用
    currentEvaluationId.value = evaluationId

    // Step 2: Submit and lock
    await selfEvaluationApi.submit(evaluationId)

    // Step 3: Trigger AI scoring
    try {
      await selfEvaluationApi.triggerAIScoring(evaluationId)
    } catch (aiError) {
      console.warn('AI评分触发失败，但不影响提交:', aiError)
    }

    // Success
    loadingMessage.close()
    ElMessage.success('提交成功！数据已上传到考评小组端')
    
  } catch (error: any) {
    console.error('Failed to submit self-evaluation:', error)
    
    if (error.response?.status === 401) {
      ElMessage.error('请先登录后再提交')
      // 跳转到登录页
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('提交失败，请检查网络连接或联系管理员')
    }
  }
}

// 附件管理处理函数
const handleAttachmentSubmit = () => {
  ElMessage.success('附件提交成功')
}

const handleAttachmentBack = () => {
  // 可以选择返回到上一个菜单或其他操作
  ElMessage.info('返回')
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
</style>
