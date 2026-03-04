<template>
  <div class="platform-layout">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="sidebar-header" @click="goToHome">
        <img src="/school-logo.jpg" alt="校徽" class="sidebar-logo" />
        <h2 class="sidebar-title">管理端</h2>
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
        <p>© 2024 教研室数据管理平台 | 版本 2.0.0</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { 
  User,
  Monitor,
  Medal,
  Warning,
  Promotion,
  Connection,
  DataAnalysis,
  TrendCharts,
  CircleCheck,
  ArrowRight,
  Document,
  Checked,
  FolderOpened,
  View,
  SwitchButton,
  Setting
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const activeMenu = ref(0)
const activeTab = ref(0)

// 根据角色配置不同的菜单项
const menuItems = computed(() => {
  const role = authStore.userRole
  
  if (role === 'evaluation_team') {
    // 评教小组：手动评分相关功能
    return [
      { name: '评分管理', icon: Medal },
      { name: '异常处理', icon: Warning },
      { name: '评分记录', icon: Document }
    ]
  } else if (role === 'evaluation_office') {
    // 评教小组办公室：公示管理、数据同步功能
    return [
      { name: '公示管理', icon: Promotion },
      { name: '数据同步', icon: Connection },
      { name: '附件管理', icon: FolderOpened }
    ]
  } else if (role === 'president_office') {
    // 校长办公会：数据看板、最终结果查看功能
    return [
      { name: '数据看板', icon: Monitor },
      { name: '最终结果', icon: TrendCharts },
      { name: '审批中心', icon: CircleCheck }
    ]
  }
  
  return []
})

// 根据角色配置不同的标签页
const tabsConfig = computed(() => {
  const role = authStore.userRole
  
  if (role === 'evaluation_team') {
    return [
      // 评分管理
      [
        { name: '手动评分', icon: Checked, description: '对各个教研室上传的考评表进行手动评分' },
        { name: '最终得分', icon: Medal, description: '综合所有评分确定最终结果' }
      ],
      // 异常处理
      [
        { name: '异常数据', icon: Warning, description: '查看AI标记的异常数据' },
        { name: '处理记录', icon: Document, description: '查看异常数据处理记录' }
      ],
      // 评分记录
      [
        { name: '我的评分', icon: Document, description: '查看我的评分记录' },
        { name: '全部评分', icon: FolderOpened, description: '查看所有评审人打分记录' }
      ]
    ]
  } else if (role === 'evaluation_office') {
    return [
      // 公示管理
      [
        { name: '发起公示', icon: Promotion, description: '公示考评结果，透明公开' },
        { name: '公示状态', icon: View, description: '查看公示进度和状态' }
      ],
      // 数据同步
      [
        { name: '同步到校长办公会', icon: Connection, description: '将结果上传到校长办公会端' },
        { name: '同步记录', icon: Document, description: '查看数据同步历史记录' }
      ],
      // 附件管理
      [
        { name: '附件列表', icon: FolderOpened, description: '查看和管理所有附件' },
        { name: '附件审核', icon: Checked, description: '审核教研室提交的附件' }
      ]
    ]
  } else if (role === 'president_office') {
    return [
      // 数据看板
      [
        { name: '实时监控', icon: Monitor, description: '查看实时数据和排名对比' },
        { name: '数据分析', icon: DataAnalysis, description: '深度数据分析和趋势预测' }
      ],
      // 最终结果
      [
        { name: '考评结果', icon: TrendCharts, description: '查看评教的最终结果' },
        { name: '历史数据', icon: Document, description: '查看历年考评数据' }
      ],
      // 审批中心
      [
        { name: '结果审定', icon: CircleCheck, description: '审定考评结果' },
        { name: '公示审批', icon: Promotion, description: '决定是否公示结果' }
      ]
    ]
  }
  
  return []
})

// 根据角色配置不同的功能卡片
const functionsConfig = computed(() => {
  const role = authStore.userRole
  
  if (role === 'evaluation_team') {
    return [
      // 评分管理
      [
        [
          { name: '手动评分', description: '对各个教研室上传的考评表进行手动评分', icon: Checked, route: '/manual-scoring' },
          { name: '评分进度', description: '查看当前评分进度和待评分项', icon: TrendCharts, route: '/management-results' },
          { name: '评分规则', description: '查看评分标准和规则说明', icon: Document, route: '#' }
        ],
        [
          { name: '最终得分确定', description: '综合所有评分确定最终结果', icon: Medal, route: '/final-score' },
          { name: '得分统计', description: '查看各教研室得分统计', icon: DataAnalysis, route: '/management-results' }
        ]
      ],
      // 异常处理
      [
        [
          { name: '异常数据列表', description: '查看AI标记的异常数据', icon: Warning, route: '/anomaly-handling' },
          { name: '异常分析', description: '分析异常数据的原因和趋势', icon: TrendCharts, route: '#' }
        ],
        [
          { name: '处理记录', description: '查看异常数据处理记录', icon: Document, route: '/anomaly-handling' },
          { name: '处理统计', description: '统计异常处理情况', icon: DataAnalysis, route: '#' }
        ]
      ],
      // 评分记录
      [
        [
          { name: '我的评分记录', description: '查看我的所有评分记录', icon: Document, route: '/management-results' },
          { name: '评分详情', description: '查看每次评分的详细信息', icon: View, route: '/management-results' }
        ],
        [
          { name: '全部评分记录', description: '查看所有评审人打分记录', icon: FolderOpened, route: '/management-results' },
          { name: '评分对比', description: '对比不同评审人的评分差异', icon: TrendCharts, route: '#' }
        ]
      ]
    ]
  } else if (role === 'evaluation_office') {
    return [
      // 公示管理
      [
        [
          { name: '发起公示', description: '公示考评结果，透明公开', icon: Promotion, route: '/publication' },
          { name: '公示预览', description: '预览公示内容', icon: View, route: '/publication' },
          { name: '公示设置', description: '配置公示范围和时间', icon: Setting, route: '#' }
        ],
        [
          { name: '公示状态', description: '查看公示进度和状态', icon: View, route: '/publication' },
          { name: '公示反馈', description: '查看公示后的反馈意见', icon: Document, route: '#' }
        ]
      ],
      // 数据同步
      [
        [
          { name: '同步到校长办公会', description: '将结果上传到校长办公会端', icon: Connection, route: '/data-sync' },
          { name: '同步配置', description: '配置数据同步规则', icon: Setting, route: '#' }
        ],
        [
          { name: '同步记录', description: '查看数据同步历史记录', icon: Document, route: '/data-sync' },
          { name: '同步状态', description: '查看当前同步任务状态', icon: Monitor, route: '/data-sync' }
        ]
      ],
      // 附件管理
      [
        [
          { name: '附件列表', description: '查看和管理所有附件', icon: FolderOpened, route: '/attachment-management' },
          { name: '附件分类', description: '按类型查看附件', icon: Document, route: '/attachment-management' }
        ],
        [
          { name: '附件审核', description: '审核教研室提交的附件', icon: Checked, route: '/attachment-management' },
          { name: '附件统计', description: '统计附件提交情况', icon: DataAnalysis, route: '#' }
        ]
      ]
    ]
  } else if (role === 'president_office') {
    return [
      // 数据看板
      [
        [
          { name: '实时监控', description: '查看实时数据和排名对比', icon: Monitor, route: '/president-office-dashboard' },
          { name: '全校概览', description: '查看全校考评进度和数据', icon: DataAnalysis, route: '/president-office-dashboard' },
          { name: 'AI评分监控', description: '监控AI评分执行情况', icon: TrendCharts, route: '#' }
        ],
        [
          { name: '数据分析', description: '深度数据分析和趋势预测', icon: TrendCharts, route: '#' },
          { name: '对比分析', description: '对比不同教研室的表现', icon: DataAnalysis, route: '#' }
        ]
      ],
      // 最终结果
      [
        [
          { name: '考评结果', description: '查看评教的最终结果', icon: TrendCharts, route: '/management-results' },
          { name: '排名榜单', description: '查看教研室排名', icon: Medal, route: '/president-office-dashboard' },
          { name: '结果导出', description: '导出考评结果报告', icon: Document, route: '#' }
        ],
        [
          { name: '历史数据', description: '查看历年考评数据', icon: Document, route: '#' },
          { name: '趋势分析', description: '分析历年数据趋势', icon: TrendCharts, route: '#' }
        ]
      ],
      // 审批中心
      [
        [
          { name: '结果审定', description: '审定考评结果', icon: CircleCheck, route: '#' },
          { name: '待审批项', description: '查看待审批的项目', icon: Warning, route: '#' }
        ],
        [
          { name: '公示审批', description: '决定是否公示结果', icon: Promotion, route: '/publication' },
          { name: '审批记录', description: '查看审批历史记录', icon: Document, route: '#' }
        ]
      ]
    ]
  }
  
  return []
})

const currentTabs = computed(() => {
  return tabsConfig.value[activeMenu.value] || []
})

const currentFunctions = computed(() => {
  return functionsConfig.value[activeMenu.value]?.[activeTab.value] || []
})

const selectMenu = (index: number) => {
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
</script>

<style scoped>
/* 使用与 TeachingOfficeHome.vue 相同的样式 */
.platform-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 220px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  border-left-color: #fff;
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
  color: #667eea;
  background: #f5f7fa;
}

.tab-item.active {
  color: #667eea;
  border-bottom-color: #667eea;
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
  border-color: #667eea;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
}

.function-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  color: #667eea;
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
