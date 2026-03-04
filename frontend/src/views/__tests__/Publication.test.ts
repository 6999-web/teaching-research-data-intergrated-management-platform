import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import Publication from '../Publication.vue'
import { publicationApi } from '@/api/client'

// Mock the API
vi.mock('@/api/client', () => ({
  publicationApi: {
    publish: vi.fn(),
    getPublications: vi.fn(() => Promise.resolve({ data: [] })),
    getEvaluationsForPublication: vi.fn()
  }
}))

// Mock Element Plus components
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn()
    },
    ElMessageBox: {
      confirm: vi.fn()
    }
  }
})

describe('Publication.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders publication page correctly', () => {
    const wrapper = mount(Publication, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-timeline': true,
          'el-timeline-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'el-checkbox-group': true
        }
      }
    })

    expect(wrapper.find('h1').text()).toBe('发起公示')
  })

  it('shows "发起公示" button only when evaluations are selected', async () => {
    const wrapper = mount(Publication, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-timeline': true,
          'el-timeline-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'el-checkbox-group': true
        }
      }
    })

    // Initially, no evaluations are selected
    expect(wrapper.vm.selectedEvaluationIds).toHaveLength(0)
    
    // Simulate selecting evaluations
    wrapper.vm.selectedEvaluationIds = ['1', '2']
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.selectedEvaluationIds).toHaveLength(2)
  })

  it('calls publish API when "发起公示" button is clicked', async () => {
    const mockPublishResponse = {
      data: {
        publication_id: 'pub-123',
        published_at: '2024-01-25T10:00:00',
        message: '公示已成功发起！'
      }
    }

    vi.mocked(publicationApi.publish).mockResolvedValue(mockPublishResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)
    vi.mocked(publicationApi.getPublications).mockResolvedValue({ data: [] })

    const wrapper = mount(Publication, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-timeline': true,
          'el-timeline-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'el-checkbox-group': true
        }
      }
    })

    // Set selected evaluations
    wrapper.vm.selectedEvaluationIds = ['1', '2']
    await wrapper.vm.$nextTick()

    // Call handlePublish
    await wrapper.vm.handlePublish()

    // Verify API was called
    expect(publicationApi.publish).toHaveBeenCalledWith({
      evaluation_ids: ['1', '2']
    })

    // Verify success message was shown
    expect(ElMessage.success).toHaveBeenCalledWith({
      message: '公示已成功发起！',
      duration: 3000
    })
  })

  it('shows error message when publish fails', async () => {
    const mockError = {
      response: {
        data: {
          detail: '发起公示失败'
        }
      }
    }

    vi.mocked(publicationApi.publish).mockRejectedValue(mockError)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(Publication, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-timeline': true,
          'el-timeline-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'el-checkbox-group': true
        }
      }
    })

    // Set selected evaluations
    wrapper.vm.selectedEvaluationIds = ['1']
    await wrapper.vm.$nextTick()

    // Call handlePublish
    await wrapper.vm.handlePublish()

    // Verify error message was shown
    expect(ElMessage.error).toHaveBeenCalledWith({
      message: '发起公示失败',
      duration: 5000,
      showClose: true
    })
  })

  it('only allows selection of approved evaluations', () => {
    const wrapper = mount(Publication, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-timeline': true,
          'el-timeline-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'el-checkbox-group': true
        }
      }
    })

    // Test isRowSelectable function
    const approvedEvaluation = { status: 'approved' }
    const publishedEvaluation = { status: 'published' }
    const finalizedEvaluation = { status: 'finalized' }

    expect(wrapper.vm.isRowSelectable(approvedEvaluation)).toBe(true)
    expect(wrapper.vm.isRowSelectable(publishedEvaluation)).toBe(false)
    expect(wrapper.vm.isRowSelectable(finalizedEvaluation)).toBe(false)
  })
})
