<template>
  <transition-group
    name="feedback-list"
    tag="div"
    class="operation-feedback-container"
  >
    <div
      v-for="feedback in feedbacks"
      :key="feedback.id"
      class="feedback-item"
      :class="[`feedback-${feedback.type}`, { 'feedback-dismissible': feedback.dismissible }]"
    >
      <div class="feedback-icon">
        <el-icon :size="20">
          <SuccessFilled v-if="feedback.type === 'success'" />
          <CircleCloseFilled v-else-if="feedback.type === 'error'" />
          <WarningFilled v-else-if="feedback.type === 'warning'" />
          <InfoFilled v-else />
        </el-icon>
      </div>
      <div class="feedback-content">
        <div
          v-if="feedback.title"
          class="feedback-title"
        >
          {{ feedback.title }}
        </div>
        <div class="feedback-message">
          {{ feedback.message }}
        </div>
      </div>
      <div
        v-if="feedback.dismissible"
        class="feedback-close"
        @click="dismissFeedback(feedback.id)"
      >
        <el-icon :size="16">
          <Close />
        </el-icon>
      </div>
    </div>
  </transition-group>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  SuccessFilled,
  CircleCloseFilled,
  WarningFilled,
  InfoFilled,
  Close
} from '@element-plus/icons-vue'

interface Feedback {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  dismissible: boolean
  duration: number
}

const feedbacks = ref<Feedback[]>([])
let feedbackIdCounter = 0

/**
 * Add a feedback notification
 */
function addFeedback(
  type: 'success' | 'error' | 'warning' | 'info',
  message: string,
  options?: {
    title?: string
    dismissible?: boolean
    duration?: number
  }
): string {
  const id = `feedback-${++feedbackIdCounter}`
  const feedback: Feedback = {
    id,
    type,
    title: options?.title,
    message,
    dismissible: options?.dismissible ?? true,
    duration: options?.duration ?? 3000
  }

  feedbacks.value.push(feedback)

  // Auto-dismiss after duration
  if (feedback.duration > 0) {
    setTimeout(() => {
      dismissFeedback(id)
    }, feedback.duration)
  }

  return id
}

/**
 * Dismiss a feedback notification
 */
function dismissFeedback(id: string): void {
  const index = feedbacks.value.findIndex((f) => f.id === id)
  if (index > -1) {
    feedbacks.value.splice(index, 1)
  }
}

/**
 * Clear all feedback notifications
 */
function clearAll(): void {
  feedbacks.value = []
}

// Expose methods
defineExpose({
  addFeedback,
  dismissFeedback,
  clearAll
})
</script>

<style scoped>
.operation-feedback-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 2000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
}

.feedback-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  transition: all 0.3s ease;
}

.feedback-item:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  transform: translateX(-4px);
}

.feedback-success {
  border-left-color: #67c23a;
}

.feedback-error {
  border-left-color: #f56c6c;
}

.feedback-warning {
  border-left-color: #e6a23c;
}

.feedback-info {
  border-left-color: #409eff;
}

.feedback-icon {
  flex-shrink: 0;
  margin-right: 12px;
}

.feedback-success .feedback-icon {
  color: #67c23a;
}

.feedback-error .feedback-icon {
  color: #f56c6c;
}

.feedback-warning .feedback-icon {
  color: #e6a23c;
}

.feedback-info .feedback-icon {
  color: #409eff;
}

.feedback-content {
  flex: 1;
  min-width: 0;
}

.feedback-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.4;
}

.feedback-message {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  word-wrap: break-word;
}

.feedback-close {
  flex-shrink: 0;
  margin-left: 12px;
  cursor: pointer;
  color: #909399;
  transition: color 0.2s;
}

.feedback-close:hover {
  color: #303133;
}

/* Transition animations */
.feedback-list-enter-active,
.feedback-list-leave-active {
  transition: all 0.3s ease;
}

.feedback-list-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.feedback-list-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.feedback-list-move {
  transition: transform 0.3s ease;
}
</style>
