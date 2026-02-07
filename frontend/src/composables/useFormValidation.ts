/**
 * Composable for enhanced form validation with real-time feedback
 */

import { ref, type Ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { showValidationError, showWarning, showSuccess } from '@/utils/feedback'

export interface FormValidationState {
  validating: Ref<boolean>
  errors: Ref<Record<string, string>>
  validate: (formRef: FormInstance | undefined) => Promise<boolean>
  validateField: (
    formRef: FormInstance | undefined,
    field: string
  ) => Promise<boolean>
  clearValidation: (formRef: FormInstance | undefined) => void
  clearFieldError: (field: string) => void
  setFieldError: (field: string, error: string) => void
  hasErrors: () => boolean
}

/**
 * Create a form validation state manager
 */
export function useFormValidation(): FormValidationState {
  const validating = ref(false)
  const errors = ref<Record<string, string>>({})

  const validate = async (
    formRef: FormInstance | undefined
  ): Promise<boolean> => {
    if (!formRef) {
      showWarning('表单引用未找到')
      return false
    }

    validating.value = true
    errors.value = {}

    try {
      await formRef.validate()
      return true
    } catch (error: any) {
      console.error('Form validation failed:', error)

      // Extract validation errors
      if (error && typeof error === 'object') {
        Object.keys(error).forEach((field) => {
          const fieldErrors = error[field]
          if (Array.isArray(fieldErrors) && fieldErrors.length > 0) {
            errors.value[field] = fieldErrors[0].message
          }
        })
      }

      showWarning('请检查表单填写是否完整')
      return false
    } finally {
      validating.value = false
    }
  }

  const validateField = async (
    formRef: FormInstance | undefined,
    field: string
  ): Promise<boolean> => {
    if (!formRef) {
      return false
    }

    try {
      await formRef.validateField(field)
      // Clear error for this field
      delete errors.value[field]
      return true
    } catch (error: any) {
      console.error(`Field validation failed for ${field}:`, error)

      // Set error for this field
      if (error && error.message) {
        errors.value[field] = error.message
      }

      return false
    }
  }

  const clearValidation = (formRef: FormInstance | undefined): void => {
    if (formRef) {
      formRef.clearValidate()
    }
    errors.value = {}
  }

  const clearFieldError = (field: string): void => {
    delete errors.value[field]
  }

  const setFieldError = (field: string, error: string): void => {
    errors.value[field] = error
    showValidationError(field, error)
  }

  const hasErrors = (): boolean => {
    return Object.keys(errors.value).length > 0
  }

  return {
    validating,
    errors,
    validate,
    validateField,
    clearValidation,
    clearFieldError,
    setFieldError,
    hasErrors
  }
}

/**
 * Create a form submission handler with validation
 */
export function useFormSubmission<T>(
  formRef: Ref<FormInstance | undefined>,
  submitFn: (data: T) => Promise<void>,
  options?: {
    successMessage?: string
    errorMessage?: string
    onSuccess?: () => void
    onError?: (error: any) => void
  }
) {
  const submitting = ref(false)
  const validation = useFormValidation()

  const submit = async (data: T): Promise<boolean> => {
    // Validate form first
    const isValid = await validation.validate(formRef.value)
    if (!isValid) {
      return false
    }

    submitting.value = true

    try {
      await submitFn(data)

      if (options?.successMessage) {
        showSuccess(options.successMessage)
      }

      if (options?.onSuccess) {
        options.onSuccess()
      }

      return true
    } catch (error: any) {
      console.error('Form submission failed:', error)

      if (options?.onError) {
        options.onError(error)
      }

      return false
    } finally {
      submitting.value = false
    }
  }

  return {
    submitting,
    validation,
    submit
  }
}
