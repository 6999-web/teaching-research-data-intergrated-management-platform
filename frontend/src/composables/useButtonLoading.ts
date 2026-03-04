/**
 * Composable for managing button loading states
 * Provides a consistent way to handle async button operations with loading feedback
 */

import { ref, type Ref } from 'vue'
import { showError, handleApiError } from '@/utils/feedback'

export interface ButtonLoadingState {
  loading: Ref<boolean>
  execute: <T>(
    operation: () => Promise<T>,
    options?: {
      onSuccess?: (result: T) => void
      onError?: (error: any) => void
      errorMessage?: string
    }
  ) => Promise<T | undefined>
}

/**
 * Create a button loading state manager
 */
export function useButtonLoading(initialState: boolean = false): ButtonLoadingState {
  const loading = ref(initialState)

  const execute = async <T>(
    operation: () => Promise<T>,
    options?: {
      onSuccess?: (result: T) => void
      onError?: (error: any) => void
      errorMessage?: string
    }
  ): Promise<T | undefined> => {
    loading.value = true

    try {
      const result = await operation()

      if (options?.onSuccess) {
        options.onSuccess(result)
      }

      return result
    } catch (error: any) {
      console.error('Button operation failed:', error)

      if (options?.onError) {
        options.onError(error)
      } else {
        handleApiError(error, options?.errorMessage)
      }

      return undefined
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    execute
  }
}

/**
 * Create multiple button loading states
 */
export function useMultipleButtonLoading(
  count: number
): Record<string, ButtonLoadingState> {
  const states: Record<string, ButtonLoadingState> = {}

  for (let i = 0; i < count; i++) {
    states[`button${i}`] = useButtonLoading()
  }

  return states
}

/**
 * Create named button loading states
 */
export function useNamedButtonLoading(
  names: string[]
): Record<string, ButtonLoadingState> {
  const states: Record<string, ButtonLoadingState> = {}

  names.forEach((name) => {
    states[name] = useButtonLoading()
  })

  return states
}
