<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="loading-overlay"
      :class="{ fullscreen }"
    >
      <div class="loading-content">
        <el-icon
          class="loading-icon is-loading"
          :size="iconSize"
        >
          <Loading />
        </el-icon>
        <div
          v-if="text"
          class="loading-text"
        >
          {{ text }}
        </div>
        <div
          v-if="description"
          class="loading-description"
        >
          {{ description }}
        </div>
        <el-progress
          v-if="showProgress && progress !== null"
          :percentage="progress"
          :status="progressStatus"
          class="loading-progress"
        />
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

interface Props {
  visible: boolean
  text?: string
  description?: string
  fullscreen?: boolean
  iconSize?: number
  showProgress?: boolean
  progress?: number | null
  progressStatus?: 'success' | 'exception' | 'warning' | ''
}

withDefaults(defineProps<Props>(), {
  visible: false,
  text: '加载中...',
  description: '',
  fullscreen: false,
  iconSize: 48,
  showProgress: false,
  progress: null,
  progressStatus: ''
})
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.loading-overlay.fullscreen {
  position: fixed;
  background-color: rgba(0, 0, 0, 0.7);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 200px;
}

.fullscreen .loading-content {
  background-color: transparent;
  box-shadow: none;
}

.loading-icon {
  color: #409eff;
  margin-bottom: 16px;
}

.fullscreen .loading-icon {
  color: white;
}

.loading-text {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 8px;
}

.fullscreen .loading-text {
  color: white;
}

.loading-description {
  font-size: 14px;
  color: #606266;
  text-align: center;
  line-height: 1.5;
  max-width: 300px;
}

.fullscreen .loading-description {
  color: rgba(255, 255, 255, 0.9);
}

.loading-progress {
  margin-top: 20px;
  width: 300px;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
