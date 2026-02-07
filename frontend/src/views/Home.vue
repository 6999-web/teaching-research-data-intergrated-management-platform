<template>
  <div class="platform-layout">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="sidebar-header" @click="goToHome">
        <img src="/school-logo.jpg" alt="校徽" class="sidebar-logo" />
        <h2 class="sidebar-title">教研室数据管理平台</h2>
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
          <span class="user-name">admin</span>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
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
  TrendCharts
} from '@element-plus/icons-vue'

const router = useRouter()

// 三个端口模块
const modules = ref([
  { name: '教研室端', icon: Edit },
  { name: '管理端', icon: Setting },
  { name: '校长办公会端', icon: Monitor }
])

const activeModule = ref(0)
const activeTab = ref(0)

// 每个模块的标签页
const moduleTabs = ref([
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

// 每个模块的功能列表
const moduleFunctions = ref([
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

// 当前选中模块的标签页
const currentTabs = computed(() => moduleTabs.value[activeModule.value])

// 当前选中标签页的功能列表
const currentFunctions = computed(() => {
  return moduleFunctions.value[activeModule.value][activeTab.value] || []
})

const selectModule = (index: number) => {
  activeModule.value = index
  activeTab.value = 0
}

const goToHome = () => {
  // 重置到默认状态
  activeModule.value = 0
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
  width: 200px;
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
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
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
  font-size: 1.5rem;
  margin-right: 0.5rem;
}

.user-name {
  font-size: 0.9rem;
}

/* 主内容区 */
.main-content {
  flex: 1;
  margin-left: 200px;
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
  .user-name {
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
