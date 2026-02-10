<template>
  <div class="platform-layout" :class="`role-${authStore.userRole}`">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="sidebar-header" @click="goToHome">
        <img src="/school-logo.jpg" alt="校徽" class="sidebar-logo" />
        <h2 class="sidebar-title">教研室数据管理平台</h2>
        <div class="role-badge">{{ isRoleMode ? authStore.roleName : modules[activeModule]?.name }}</div>
      </div>
      
      <!-- 模式切换按钮 -->
      <div class="mode-toggle">
        <button @click="toggleMode" class="toggle-button">
          <el-icon><Switch /></el-icon>
          <span>{{ isRoleMode ? '切换到三端模式' : '切换到四角色模式' }}</span>
        </button>
      </div>
      
      <div class="sidebar-menu">
        <div 
          v-for="(module, index) in modules" 
          :key="index"
          class="menu-item"
          :class="{ active: activeModule === index }"
          @click="selectModule(index)"
        >
          <el-icon class="menu-icon">
            <component :is="module.icon" />
          </el-icon>
          <span class="menu-text">{{ module.name }}</span>
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <el-icon class="user-avatar"><User /></el-icon>
          <div class="user-details">
            <span class="user-name">{{ authStore.userName }}</span>
            <span class="user-role-text">{{ isRoleMode ? authStore.roleName : '管理员' }}</span>
          </div>
        </div>
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
        <!-- 流程条 (仅在四角色模式下显示) -->
        <ProcessBar v-if="isRoleMode" :user-role="authStore.userRole" :current-step="3" />
        
        <div class="content-header">
          <h2 class="content-title">{{ currentTabs[activeTab]?.name }}</h2>
          <p class="content-subtitle">{{ currentTabs[activeTab]?.description }}</p>
        </div>

        <!-- 功能卡片网格 -->
        <div class="function-grid">
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
        <p>© 2024 教研室数据管理平台 | 版本 1.0.0</p>
        <div class="footer-links">
          <a href="#">使用指南</a>
          <a href="#">系统公告</a>
          <a href="#">联系我们</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ProcessBar from '@/components/ProcessBar.vue'
import { 
  User,
  Edit,
  EditPen,
  Upload,
  View,
  Setting,
  Checked,
  Medal,
  Warning,
  Connection,
  Promotion,
  FolderOpened,
  Monitor,
  DataAnalysis,
  CircleCheck,
  ArrowRight,
  Document,
  TrendCharts,
  Histogram,
  PieChart,
  Switch
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 模式切换：false=三端模式，true=四角色模式
const isRoleMode = ref(false)

// 三端模块（原来的）
const threePortModules = ref([
  { name: '教研室端', icon: Edit },
  { name: '管理端', icon: Setting },
  { name: '校长办公会端', icon: Monitor }
])

// 四个角色模块（新的）
const fourRoleModules = ref([
  { name: '普通教师', icon: User, role: 'teacher' },
  { name: '教研室', icon: Edit, role: 'director' },
  { name: '二级学院负责人', icon: Histogram, role: 'college_leader' },
  { name: '评教小组', icon: Medal, role: 'evaluation_team' }
])

// 当前使用的模块
const modules = computed(() => {
  return isRoleMode.value ? fourRoleModules.value : threePortModules.value
})

const activeModule = ref(0)
const activeTab = ref(0)

// 切换模式
const toggleMode = () => {
  isRoleMode.value = !isRoleMode.value
  activeModule.value = 0
  activeTab.value = 0
  localStorage.setItem('viewMode', isRoleMode.value ? 'role' : 'port')
}

onMounted(() => {
  authStore.loadFromStorage()
  // 恢复模式设置
  const savedMode = localStorage.getItem('viewMode')
  if (savedMode === 'role') {
    isRoleMode.value = true
    // 根据存储的角色设置activeModule
    const roleIndex = fourRoleModules.value.findIndex(m => m.role === authStore.userRole)
    if (roleIndex !== -1) {
      activeModule.value = roleIndex
    }
  }
})

// 三端模式的标签页（原来的）
const threePortTabs = ref([
  // 教研室端
  [
    { name: '详教方案', icon: Document, description: '查看和管理教学方案' },
    { name: '分发材料', icon: Upload, description: '上传和分发教学材料' }
  ],
  // 管理端
  [
    { name: '监控中心', icon: TrendCharts, description: '实时监控系统运行状态' },
    { name: '分析中心', icon: DataAnalysis, description: '数据分析和报表' },
    { name: '应用中心', icon: Setting, description: '应用管理和配置' }
  ],
  // 校长办公会端
  [
    { name: '数据看板', icon: Monitor, description: '实时数据展示' },
    { name: '审批中心', icon: CircleCheck, description: '审批和审定' }
  ]
])

// 四角色模式的标签页（新的）
const fourRoleTabs = ref([
  // 普通教师
  [
    { name: '我的教研室', icon: Document, description: '查看本教研室考评结果' },
    { name: '数据分析', icon: DataAnalysis, description: '历史对比和指标分析' }
  ],
  // 教研室
  [
    { name: '自评管理', icon: EditPen, description: '填写和管理自评表' },
    { name: '材料管理', icon: Upload, description: '上传和管理附件' },
    { name: 'AI评分', icon: Monitor, description: '触发AI评分' },
    { name: '改进闭环', icon: CircleCheck, description: '提交改进措施' }
  ],
  // 二级学院负责人
  [
    { name: '学院驾驶舱', icon: TrendCharts, description: '全院概览和对比' },
    { name: '整改督导', icon: Checked, description: '审核改进措施' }
  ],
  // 学校教务处负责人
  [
    { name: '监控中心', icon: Monitor, description: '全校数据监控' },
    { name: '评分管理', icon: Medal, description: '手动评分和最终得分' },
    { name: '异常处理', icon: Warning, description: '处理异常数据' },
    { name: '公示管理', icon: Promotion, description: '发起公示' }
  ]
])

// 当前使用的标签页
const moduleTabs = computed(() => {
  return isRoleMode.value ? fourRoleTabs.value : threePortTabs.value
})

// 三端模式的功能列表（原来的）
const threePortFunctions = ref([
  // 教研室端功能
  [
    [
      { name: '填写自评表', description: '在线填写工作考核表，支持实时保存和预览', icon: EditPen, route: '/self-evaluation' },
      { name: '查看结果', description: '查看考评结果和详细评分细则', icon: View, route: '/result/eval-123' }
    ],
    [
      { name: '上传附件', description: '上传支撑材料，支持多文件批量上传', icon: Upload, route: '/attachment-upload' },
      { name: '附件管理', description: '查看和管理所有附件', icon: FolderOpened, route: '/attachment-management' }
    ]
  ],
  // 管理端功能
  [
    [
      { name: '手动评分', description: '考评小组和办公室进行专业评分', icon: Checked, route: '/manual-scoring' },
      { name: '最终得分', description: '综合所有评分确定最终结果', icon: Medal, route: '/final-score' },
      { name: '异常处理', description: '处理AI标记的异常数据', icon: Warning, route: '/anomaly-handling' }
    ],
    [
      { name: '数据同步', description: '同步数据至校长办公会', icon: Connection, route: '/data-sync' },
      { name: '发起公示', description: '公示考评结果，透明公开', icon: Promotion, route: '/publication' }
    ],
    [
      { name: '附件管理', description: '查看和管理所有附件', icon: FolderOpened, route: '/attachment-management' },
      { name: '系统配置', description: '系统参数和权限配置', icon: Setting, route: '#' }
    ]
  ],
  // 校长办公会端功能
  [
    [
      { name: '实时监控', description: '查看实时数据和排名对比', icon: DataAnalysis, route: '/president-office-dashboard' },
      { name: '数据分析', description: '深度数据分析和趋势预测', icon: TrendCharts, route: '#' }
    ],
    [
      { name: '结果审定', description: '审定考评结果，决定是否公示', icon: CircleCheck, route: '#' },
      { name: '公示管理', description: '管理公示流程和结果', icon: Promotion, route: '/publication' }
    ]
  ]
])

// 四角色模式的功能列表（新的）
const fourRoleFunctions = ref([
  // 普通教师功能
  [
    [
      { name: '考评结果', description: '查看本教研室的考评结果和排名', icon: View, route: '/result/eval-123' },
      { name: '评分详情', description: '查看详细的评分记录和评语', icon: Document, route: '/result/eval-123' },
      { name: '改进措施', description: '查看教研室的改进措施', icon: CircleCheck, route: '/improvement-plan/1' }
    ],
    [
      { name: '历史对比', description: '查看历年考评数据对比', icon: TrendCharts, route: '#' },
      { name: '指标雷达图', description: '查看各项指标的雷达图分析', icon: PieChart, route: '#' }
    ]
  ],
  // 教研室功能
  [
    [
      { name: '填写自评表', description: '在线填写工作考核表，支持实时保存', icon: EditPen, route: '/self-evaluation' },
      { name: '查看自评表', description: '查看已提交的自评表内容', icon: View, route: '/result/eval-123' }
    ],
    [
      { name: '上传附件', description: '上传支撑材料，支持多文件批量上传', icon: Upload, route: '/attachment-upload' },
      { name: '附件列表', description: '查看和管理所有附件', icon: FolderOpened, route: '/attachment-management' }
    ],
    [
      { name: '触发评分', description: '手动触发AI自动评分', icon: Monitor, route: '#' },
      { name: '评分结果', description: '查看AI评分结果', icon: View, route: '/result/eval-123' }
    ],
    [
      { name: '提交改进措施', description: '针对薄弱项提交改进措施', icon: EditPen, route: '/improvement-plan/1' },
      { name: '查看审核状态', description: '查看改进措施的审核状态', icon: CircleCheck, route: '/improvement-plan/1' }
    ]
  ],
  // 二级学院负责人功能
  [
    [
      { name: '全院概览', description: '查看全院教研室考评概况', icon: TrendCharts, route: '/college-dashboard' },
      { name: '教研室对比', description: '横向对比各教研室得分', icon: Histogram, route: '/college-dashboard' },
      { name: '指标分析', description: '分析各项指标的得分情况', icon: DataAnalysis, route: '/college-dashboard' }
    ],
    [
      { name: '改进措施审核', description: '审核教研室提交的改进措施', icon: Checked, route: '/improvement-plan/1' },
      { name: '执行进度跟踪', description: '跟踪改进措施的执行进度', icon: Monitor, route: '/improvement-plan/1' },
      { name: '督导记录', description: '添加督导批注和记录', icon: Document, route: '/improvement-plan/1' }
    ]
  ],
  // 学校教务处负责人功能
  [
    [
      { name: '全校概览', description: '查看全校考评进度和数据', icon: Monitor, route: '/president-office-dashboard' },
      { name: '实时数据', description: '实时监控各教研室状态', icon: DataAnalysis, route: '/president-office-dashboard' },
      { name: 'AI评分监控', description: '监控AI评分执行情况', icon: TrendCharts, route: '#' }
    ],
    [
      { name: '手动评分', description: '考评小组和办公室进行专业评分', icon: Checked, route: '/manual-scoring' },
      { name: '最终得分确定', description: '综合所有评分确定最终结果', icon: Medal, route: '/final-score' },
      { name: '评分记录查询', description: '查询所有评审人打分记录', icon: Document, route: '/management-results' }
    ],
    [
      { name: '异常数据列表', description: '查看AI标记的异常数据', icon: Warning, route: '/anomaly-handling' },
      { name: '处理记录', description: '查看异常数据处理记录', icon: Document, route: '/anomaly-handling' }
    ],
    [
      { name: '发起公示', description: '公示考评结果，透明公开', icon: Promotion, route: '/publication' },
      { name: '公示状态', description: '查看公示进度和状态', icon: View, route: '/publication' },
      { name: '数据同步', description: '同步数据至校长办公会', icon: Connection, route: '/data-sync' }
    ]
  ]
])

// 当前使用的功能列表
const moduleFunctions = computed(() => {
  return isRoleMode.value ? fourRoleFunctions.value : threePortFunctions.value
})

// 当前选中模块的标签页
const currentTabs = computed(() => moduleTabs.value[activeModule.value])

// 当前选中标签页的功能列表
const currentFunctions = computed(() => {
  return moduleFunctions.value[activeModule.value][activeTab.value] || []
})

const selectModule = (index: number) => {
  activeModule.value = index
  activeTab.value = 0
  // 仅在四角色模式下更新用户角色
  if (isRoleMode.value) {
    const role = modules.value[index].role as any
    if (role) {
      authStore.setRole(role)
    }
  }
}

const goToHome = () => {
  // 重置到默认状态
  if (isRoleMode.value) {
    activeModule.value = 1 // 默认教研室
  } else {
    activeModule.value = 0 // 默认教研室端
  }
  activeTab.value = 0
}

const navigateTo = (route: string) => {
  if (route !== '#') {
    router.push(route).catch(err => {
      console.error('导航失败:', err)
      // 可以在这里添加用户提示
    })
  }
}
</script>

<style scoped>
/* 平台布局 */
.platform-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

/* 左侧边栏 */
.sidebar {
  width: 220px;
  background: #1e3a5f;
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

/* 不同角色的激活色 */
.role-teacher .menu-item.active {
  border-left-color: #42a5f5;
}

.role-director .menu-item.active {
  border-left-color: #66bb6a;
}

.role-college_leader .menu-item.active {
  border-left-color: #ab47bc;
}

.role-evaluation_team .menu-item.active {
  border-left-color: #ff7043;
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

/* 模式切换按钮 */
.mode-toggle {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.toggle-button {
  width: 100%;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  transition: all 0.3s;
}

.toggle-button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.toggle-button .el-icon {
  font-size: 1.1rem;
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 顶部标签栏 */
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
  position: relative;
}

.tab-item:hover {
  color: #2c4a6d;
  background: #f5f7fa;
}

.tab-item.active {
  color: #2c4a6d;
  border-bottom-color: #2c4a6d;
  font-weight: 600;
}

.tab-icon {
  font-size: 1.2rem;
  margin-right: 0.5rem;
}

.tab-text {
  font-size: 0.95rem;
}

/* 内容区域 */
.content-area {
  flex: 1;
  padding: 2rem;
  background: #f5f7fa;
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

/* 功能卡片网格 */
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
  border-color: #2c4a6d;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(44, 74, 109, 0.15);
}

.function-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2c4a6d 0%, #1e3a5f 100%);
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
  color: #2c4a6d;
  opacity: 0;
  transition: opacity 0.3s;
}

.function-card:hover .function-arrow {
  opacity: 1;
}

/* 页脚 */
.content-footer {
  background: white;
  padding: 2rem;
  text-align: center;
  border-top: 1px solid #e5e7eb;
  color: #666;
  font-size: 0.9rem;
}

.footer-links {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.footer-links a {
  color: #2c4a6d;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: #1e3a5f;
}

/* 响应式设计 */
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
  .role-badge,
  .mode-toggle {
    display: none;
  }
  
  .main-content {
    margin-left: 60px;
  }
  
  .content-tabs {
    padding: 0 1rem;
  }
  
  .tab-text {
    display: none;
  }
}
</style>
