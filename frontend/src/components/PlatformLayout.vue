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
          :class="{ active: isModuleActive(module.path) }"
          @click="navigateTo(module.path)"
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
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Edit, Setting, Monitor } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const modules = [
  { name: '教研室端', icon: Edit, path: '/' },
  { name: '管理端', icon: Setting, path: '/' },
  { name: '校长办公会端', icon: Monitor, path: '/' }
]

const goToHome = () => {
  router.push('/')
}

const navigateTo = (path: string) => {
  router.push(path).catch(err => {
    console.error('导航失败:', err)
  })
}

const isModuleActive = (path: string) => {
  return route.path === path
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
  min-height: 100vh;
}

/* 响应式设计 */
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
}
</style>
