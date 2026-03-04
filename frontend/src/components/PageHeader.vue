<template>
  <div class="page-header">
    <div class="header-left">
      <el-button 
        v-if="showBack"
        type="primary" 
        :icon="HomeFilled" 
        circle 
        @click="goToHome"
        class="home-button"
        title="返回首页"
      />
      <div class="header-content">
        <h1 class="page-title">{{ title }}</h1>
        <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
        <el-breadcrumb separator="/" v-if="breadcrumbs.length > 0" class="breadcrumb">
          <el-breadcrumb-item :to="{ path: '/' }">
            首页
          </el-breadcrumb-item>
          <el-breadcrumb-item 
            v-for="(item, index) in breadcrumbs" 
            :key="index"
            :to="item.path ? { path: item.path } : undefined"
          >
            {{ item.label }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>
    <div class="header-right">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { HomeFilled } from '@element-plus/icons-vue'

interface Breadcrumb {
  label: string
  path?: string
}

interface Props {
  title: string
  subtitle?: string
  showBack?: boolean
  breadcrumbs?: Breadcrumb[]
}

const props = withDefaults(defineProps<Props>(), {
  subtitle: '',
  showBack: true,
  breadcrumbs: () => []
})

const router = useRouter()

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.page-header {
  background: white;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.home-button {
  background: linear-gradient(135deg, #2c4a6d 0%, #1e3a5f 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(44, 74, 109, 0.3);
  transition: all 0.3s;
}

.home-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(44, 74, 109, 0.4);
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  font-size: 1rem;
  color: #666;
  margin: 0 0 0.5rem 0;
}

.breadcrumb {
  font-size: 0.9rem;
}

.header-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-left {
    width: 100%;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-end;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}
</style>
