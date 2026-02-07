/**
 * User Feedback Utility
 * Provides standardized feedback messages and loading states across the application
 */

import { ElMessage, ElNotification, ElLoading, type LoadingInstance } from 'element-plus'

/**
 * Message types for consistent feedback
 */
export enum FeedbackType {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

/**
 * Standard message durations (in milliseconds)
 */
export const MESSAGE_DURATION = {
  SHORT: 2000,
  MEDIUM: 3000,
  LONG: 5000,
  PERSISTENT: 0 // Won't auto-close
}

/**
 * Show a success message
 */
export function showSuccess(message: string, duration: number = MESSAGE_DURATION.MEDIUM): void {
  ElMessage({
    message,
    type: 'success',
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show an error message
 */
export function showError(message: string, duration: number = MESSAGE_DURATION.LONG): void {
  ElMessage({
    message,
    type: 'error',
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show a warning message
 */
export function showWarning(message: string, duration: number = MESSAGE_DURATION.MEDIUM): void {
  ElMessage({
    message,
    type: 'warning',
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show an info message
 */
export function showInfo(message: string, duration: number = MESSAGE_DURATION.MEDIUM): void {
  ElMessage({
    message,
    type: 'info',
    duration,
    showClose: true,
    grouping: true
  })
}

/**
 * Show a notification (more prominent than message)
 */
export function showNotification(
  title: string,
  message: string,
  type: FeedbackType = FeedbackType.INFO,
  duration: number = MESSAGE_DURATION.LONG
): void {
  ElNotification({
    title,
    message,
    type,
    duration,
    showClose: true,
    position: 'top-right'
  })
}

/**
 * Show a loading overlay
 */
export function showLoading(text: string = '加载中...'): LoadingInstance {
  return ElLoading.service({
    lock: true,
    text,
    background: 'rgba(0, 0, 0, 0.7)',
    customClass: 'app-loading'
  })
}

/**
 * Hide a loading overlay
 */
export function hideLoading(loadingInstance: LoadingInstance): void {
  loadingInstance.close()
}

/**
 * Standard operation feedback messages
 */
export const FEEDBACK_MESSAGES = {
  // Save operations
  SAVE_SUCCESS: '保存成功',
  SAVE_ERROR: '保存失败，请重试',
  SAVE_LOADING: '正在保存...',

  // Submit operations
  SUBMIT_SUCCESS: '提交成功',
  SUBMIT_ERROR: '提交失败，请重试',
  SUBMIT_LOADING: '正在提交...',

  // Delete operations
  DELETE_SUCCESS: '删除成功',
  DELETE_ERROR: '删除失败，请重试',
  DELETE_LOADING: '正在删除...',

  // Upload operations
  UPLOAD_SUCCESS: '上传成功',
  UPLOAD_ERROR: '上传失败，请重试',
  UPLOAD_LOADING: '正在上传...',

  // Load operations
  LOAD_ERROR: '加载失败，请刷新重试',
  LOAD_LOADING: '正在加载...',

  // Update operations
  UPDATE_SUCCESS: '更新成功',
  UPDATE_ERROR: '更新失败，请重试',
  UPDATE_LOADING: '正在更新...',

  // Validation
  VALIDATION_ERROR: '请检查表单填写是否完整',
  VALIDATION_REQUIRED: '请填写必填项',

  // Network
  NETWORK_ERROR: '网络连接失败，请检查网络后重试',
  TIMEOUT_ERROR: '请求超时，请重试',

  // Permission
  PERMISSION_ERROR: '您没有权限执行此操作',

  // Generic
  OPERATION_SUCCESS: '操作成功',
  OPERATION_ERROR: '操作失败，请重试',
  OPERATION_LOADING: '正在处理...'
}

/**
 * Handle API errors with user-friendly messages
 */
export function handleApiError(error: any, defaultMessage: string = FEEDBACK_MESSAGES.OPERATION_ERROR): void {
  console.error('API Error:', error)

  let message = defaultMessage

  if (error.response) {
    // Server responded with error
    const status = error.response.status
    const detail = error.response.data?.detail

    if (detail) {
      message = detail
    } else if (status === 400) {
      message = '请求参数错误'
    } else if (status === 401) {
      message = '未登录或登录已过期，请重新登录'
    } else if (status === 403) {
      message = FEEDBACK_MESSAGES.PERMISSION_ERROR
    } else if (status === 404) {
      message = '请求的资源不存在'
    } else if (status === 500) {
      message = '服务器错误，请稍后重试'
    } else if (status === 503) {
      message = '服务暂时不可用，请稍后重试'
    }
  } else if (error.request) {
    // Request made but no response
    message = FEEDBACK_MESSAGES.NETWORK_ERROR
  } else if (error.code === 'ECONNABORTED') {
    // Timeout
    message = FEEDBACK_MESSAGES.TIMEOUT_ERROR
  }

  showError(message)
}

/**
 * Show validation error for form fields
 */
export function showValidationError(fieldName: string, errorMessage: string): void {
  showWarning(`${fieldName}: ${errorMessage}`)
}

/**
 * Show a progress notification that can be updated
 */
export function showProgressNotification(
  title: string,
  initialMessage: string,
  type: FeedbackType = FeedbackType.INFO
): { update: (message: string) => void; close: () => void } {
  const notification = ElNotification({
    title,
    message: initialMessage,
    type,
    duration: 0, // Don't auto-close
    showClose: true,
    position: 'top-right'
  })

  return {
    update: (message: string) => {
      // Close old and show new
      notification.close()
      ElNotification({
        title,
        message,
        type,
        duration: 0,
        showClose: true,
        position: 'top-right'
      })
    },
    close: () => notification.close()
  }
}

/**
 * Debounce function for form validation feedback
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function for preventing rapid button clicks
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}
