<template>
  <el-button
    :type="type"
    :size="size"
    :loading="isLoading"
    :disabled="disabled || isLoading"
    :icon="currentIcon"
    :plain="plain"
    :round="round"
    :circle="circle"
    :text="text"
    :link="link"
    @click="handleClick"
  >
    <slot>{{ label }}</slot>
  </el-button>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { showSuccess, showError, handleApiError } from '@/utils/feedback'
import type { Component } from 'vue'

interface Props {
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  size?: 'large' | 'default' | 'small'
  label?: string
  icon?: Component
  loadingIcon?: Component
  plain?: boolean
  round?: boolean
  circle?: boolean
  text?: boolean
  link?: boolean
  disabled?: boolean
  confirmMessage?: string
  confirmTitle?: string
  successMessage?: string
  errorMessage?: string
  onClick?: () => Promise<void> | void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'default',
  size: 'default',
  label: '',
  plain: false,
  round: false,
  circle: false,
  text: false,
  link: false,
  disabled: false
})

const emit = defineEmits<{
  click: []
  success: []
  error: [error: any]
}>()

const isLoading = ref(false)

const currentIcon = computed(() => {
  if (isLoading.value && props.loadingIcon) {
    return props.loadingIcon
  }
  return props.icon
})

const handleClick = async () => {
  // If confirm message is provided, show confirmation dialog
  if (props.confirmMessage) {
    const { ElMessageBox } = await import('element-plus')
    try {
      await ElMessageBox.confirm(
        props.confirmMessage,
        props.confirmTitle || '确认操作',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch {
      // User cancelled
      return
    }
  }

  // Execute onClick handler if provided
  if (props.onClick) {
    isLoading.value = true

    try {
      await props.onClick()

      if (props.successMessage) {
        showSuccess(props.successMessage)
      }

      emit('success')
      emit('click')
    } catch (error: any) {
      console.error('Button action failed:', error)

      if (props.errorMessage) {
        showError(props.errorMessage)
      } else {
        handleApiError(error)
      }

      emit('error', error)
    } finally {
      isLoading.value = false
    }
  } else {
    // Just emit click event
    emit('click')
  }
}

// Expose loading state for parent component
defineExpose({
  isLoading,
  setLoading: (loading: boolean) => {
    isLoading.value = loading
  }
})
</script>

<style scoped>
/* Additional button styles can be added here */
</style>
