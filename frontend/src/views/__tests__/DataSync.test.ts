import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import DataSync from '../DataSync.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn()
  }
}))

// Mock API client
vi.mock('@/api/client', () => ({
  reviewApi: {
    syncToPresidentOffice: vi.fn()
  }
}))

describe('DataSync', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the data sync page', () => {
    const wrapper = mount(DataSync)
    
    expect(wrapper.text()).toContain('数据同步至校长办公会')
    expect(wrapper.text()).toContain('选择待上传的教研室')
  })

  it('displays upload button', () => {
    const wrapper = mount(DataSync)
    
    expect(wrapper.text()).toContain('上传至校长办公会')
  })

  it('displays sync history section', () => {
    const wrapper = mount(DataSync)
    
    expect(wrapper.text()).toContain('同步历史')
  })

  it('disables upload button when no evaluations are selected', async () => {
    const wrapper = mount(DataSync)
    await wrapper.vm.$nextTick()
    
    const uploadButton = wrapper.find('button')
    expect(uploadButton.attributes('disabled')).toBeDefined()
  })
})
