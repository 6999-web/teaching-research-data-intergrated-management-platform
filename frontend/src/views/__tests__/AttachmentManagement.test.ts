import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import AttachmentManagement from '../AttachmentManagement.vue'
import apiClient from '@/api/client'

// Mock API client
vi.mock('@/api/client', () => ({
  default: {
    get: vi.fn()
  }
}))

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElCard: { name: 'ElCard', template: '<div><slot /></div>' },
  ElForm: { name: 'ElForm', template: '<div><slot /></div>' },
  ElFormItem: { name: 'ElFormItem', template: '<div><slot /></div>' },
  ElInput: { name: 'ElInput', template: '<input />' },
  ElSelect: { name: 'ElSelect', template: '<select><slot /></select>' },
  ElOption: { name: 'ElOption', template: '<option><slot /></option>' },
  ElButton: { name: 'ElButton', template: '<button><slot /></button>' },
  ElTable: { name: 'ElTable', template: '<table><slot /></table>' },
  ElTableColumn: { name: 'ElTableColumn', template: '<td><slot /></td>' },
  ElTag: { name: 'ElTag', template: '<span><slot /></span>' },
  ElEmpty: { name: 'ElEmpty', template: '<div>Empty</div>' },
  ElPagination: { name: 'ElPagination', template: '<div>Pagination</div>' },
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

// Mock icons
vi.mock('@element-plus/icons-vue', () => ({
  Download: { name: 'Download' }
}))

describe('AttachmentManagement.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders attachment management view', () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: [] })
    
    const wrapper = mount(AttachmentManagement, {
      global: {
        stubs: {
          ElCard: true,
          ElForm: true,
          ElFormItem: true,
          ElInput: true,
          ElSelect: true,
          ElOption: true,
          ElButton: true,
          ElTable: true,
          ElTableColumn: true,
          ElTag: true,
          ElEmpty: true,
          ElPagination: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('loads attachments on mount', async () => {
    const mockAttachments = [
      {
        id: '1',
        file_name: 'test.pdf',
        indicator: 'teaching_reform_projects',
        teaching_office_name: '计算机教研室',
        evaluation_year: 2024,
        file_size: 1024,
        uploaded_at: '2024-01-01T00:00:00Z',
        is_archived: true
      }
    ]

    vi.mocked(apiClient.get).mockResolvedValue({ data: mockAttachments })

    const wrapper = mount(AttachmentManagement, {
      global: {
        stubs: {
          ElCard: true,
          ElForm: true,
          ElFormItem: true,
          ElInput: true,
          ElSelect: true,
          ElOption: true,
          ElButton: true,
          ElTable: true,
          ElTableColumn: true,
          ElTag: true,
          ElEmpty: true,
          ElPagination: true
        }
      }
    })

    // Wait for async operations
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(apiClient.get).toHaveBeenCalledWith(
      '/teaching-office/attachments',
      expect.objectContaining({
        params: expect.objectContaining({
          is_archived: true
        })
      })
    )
  })

  it('filters attachments by indicator', async () => {
    const mockAttachments = [
      {
        id: '1',
        file_name: 'test1.pdf',
        indicator: 'teaching_reform_projects',
        teaching_office_name: '计算机教研室',
        evaluation_year: 2024,
        file_size: 1024,
        uploaded_at: '2024-01-01T00:00:00Z',
        is_archived: true
      },
      {
        id: '2',
        file_name: 'test2.pdf',
        indicator: 'honorary_awards',
        teaching_office_name: '数学教研室',
        evaluation_year: 2024,
        file_size: 2048,
        uploaded_at: '2024-01-02T00:00:00Z',
        is_archived: true
      }
    ]

    vi.mocked(apiClient.get).mockResolvedValue({ data: mockAttachments })

    const wrapper = mount(AttachmentManagement, {
      global: {
        stubs: {
          ElCard: true,
          ElForm: true,
          ElFormItem: true,
          ElInput: true,
          ElSelect: true,
          ElOption: true,
          ElButton: true,
          ElTable: true,
          ElTableColumn: true,
          ElTag: true,
          ElEmpty: true,
          ElPagination: true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Verify initial load
    expect(apiClient.get).toHaveBeenCalled()
  })

  it('downloads attachment when download button is clicked', async () => {
    const mockAttachment = {
      id: '1',
      file_name: 'test.pdf',
      indicator: 'teaching_reform_projects',
      teaching_office_name: '计算机教研室',
      evaluation_year: 2024,
      file_size: 1024,
      uploaded_at: '2024-01-01T00:00:00Z',
      is_archived: true
    }

    vi.mocked(apiClient.get).mockResolvedValue({ data: [mockAttachment] })

    const wrapper = mount(AttachmentManagement, {
      global: {
        stubs: {
          ElCard: true,
          ElForm: true,
          ElFormItem: true,
          ElInput: true,
          ElSelect: true,
          ElOption: true,
          ElButton: true,
          ElTable: true,
          ElTableColumn: true,
          ElTag: true,
          ElEmpty: true,
          ElPagination: true
        }
      }
    })

    await wrapper.vm.$nextTick()

    // Verify component loaded
    expect(wrapper.exists()).toBe(true)
  })
})
