<template>
  <div class="progress-indicator">
    <div
      v-if="title"
      class="progress-title"
    >
      {{ title }}
    </div>

    <div class="progress-bar-container">
      <el-progress
        :percentage="percentage"
        :status="status"
        :stroke-width="strokeWidth"
        :show-text="showText"
        :text-inside="textInside"
        :color="customColor"
      >
        <template
          v-if="$slots.default"
          #default
        >
          <slot />
        </template>
      </el-progress>
    </div>

    <div
      v-if="description"
      class="progress-description"
    >
      {{ description }}
    </div>

    <div
      v-if="showSteps && steps.length > 0"
      class="progress-steps"
    >
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="progress-step"
        :class="{
          'step-completed': index < currentStep,
          'step-active': index === currentStep,
          'step-pending': index > currentStep
        }"
      >
        <div class="step-icon">
          <el-icon v-if="index < currentStep">
            <CircleCheckFilled />
          </el-icon>
          <el-icon
            v-else-if="index === currentStep"
            class="is-loading"
          >
            <Loading />
          </el-icon>
          <span
            v-else
            class="step-number"
          >{{ index + 1 }}</span>
        </div>
        <div class="step-label">
          {{ step }}
        </div>
      </div>
    </div>

    <div
      v-if="showTime && estimatedTime"
      class="progress-time"
    >
      <el-icon><Clock /></el-icon>
      <span>预计剩余时间: {{ formatTime(estimatedTime) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheckFilled, Loading, Clock } from '@element-plus/icons-vue'

interface Props {
  percentage: number
  title?: string
  description?: string
  status?: 'success' | 'exception' | 'warning' | ''
  strokeWidth?: number
  showText?: boolean
  textInside?: boolean
  customColor?: string | ((percentage: number) => string)
  showSteps?: boolean
  steps?: string[]
  currentStep?: number
  showTime?: boolean
  estimatedTime?: number // in seconds
}

const props = withDefaults(defineProps<Props>(), {
  percentage: 0,
  title: '',
  description: '',
  status: '',
  strokeWidth: 6,
  showText: true,
  textInside: false,
  showSteps: false,
  steps: () => [],
  currentStep: 0,
  showTime: false,
  estimatedTime: 0
})

const formatTime = (seconds: number): string => {
  if (seconds < 60) {
    return `${seconds}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}分${remainingSeconds}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}小时${minutes}分`
  }
}
</script>

<style scoped>
.progress-indicator {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.progress-bar-container {
  margin-bottom: 12px;
}

.progress-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-top: 8px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  padding: 0 10px;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.progress-step:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 16px;
  left: 50%;
  right: -50%;
  height: 2px;
  background-color: #dcdfe6;
  z-index: 0;
}

.progress-step.step-completed:not(:last-child)::after {
  background-color: #67c23a;
}

.step-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #dcdfe6;
  color: white;
  font-size: 18px;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
  transition: all 0.3s;
}

.step-completed .step-icon {
  background-color: #67c23a;
}

.step-active .step-icon {
  background-color: #409eff;
  animation: pulse 1.5s ease-in-out infinite;
}

.step-pending .step-icon {
  background-color: #dcdfe6;
  color: #909399;
}

.step-number {
  font-size: 14px;
  font-weight: 600;
}

.step-label {
  font-size: 13px;
  color: #606266;
  text-align: center;
  max-width: 100px;
  line-height: 1.4;
}

.step-completed .step-label {
  color: #67c23a;
  font-weight: 500;
}

.step-active .step-label {
  color: #409eff;
  font-weight: 600;
}

.progress-time {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.7);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
}
</style>
