import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import ManagementResultView from '../ManagementResultView.vue'
import { managementResultApi } from '@/api/client'

// Mock the API
vi.mock('@/api/client', () => ({
  managementResultApi: {
    getAllResults: vi.fn(),
    getResultDetail: vi.fn()
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
      warning: vi.fn(),
      info: vi.fn()
    }
  }
})

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

describe('ManagementResultView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockResultsData = [
    {
      id: '1',
      teaching_office_id: 'to1',
      teaching_office_name: '计算机科学教研室',
      evaluation_year: 2024,
      final_score: 92.5,
      ai_score: 90.0,
      manual_score_avg: 93.5,
      approval_status: 'approved',
      status: 'published',
      summary: '该教研室在教学改革、课程建设等方面表现突出，综合评分优秀。',
      approved_at: '2024-01-25T10:30:00',
      published_at: '2024-01-26T09:00:00'
    },
    {
      id: '2',
      teaching_office_id: 'to2',
      teaching_office_name: '数学教研室',
      evaluation_year: 2024,
      final_score: 88.3,
      ai_score: 87.5,
      manual_score_avg: 89.0,
      approval_status: 'approved',
      status: 'published',
      summary: '该教研室整体表现良好，建议加强教学改革项目申报。',
      approved_at: '2024-01-25T14:20:00',
      published_at: '2024-01-26T09:00:00'
    },
    {
      id: '3',
      teaching_office_id: 'to3',
      teaching_office_name: '英语教研室',
      evaluation_year: 2024,
      final_score: 78.5,
      ai_score: 80.0,
      manual_score_avg: 77.5,
      approval_status: 'rejected',
      status: 'finalized',
      summary: '该教研室在多个考核指标上未达标。',
      approved_at: '2024-01-25T11:20:00',
      reject_reason: '教学改革项目数量不足，荣誉表彰材料存在疑问。'
    }
  ]

  it('renders management result view page correctly', () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    expect(wrapper.find('h1').text()).toBe('考评结果汇总')
  })

  it('displays all teaching offices results - Requirement 14.7', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Requirement 14.7: 管理端显示所有教研室最终得分
    expect(wrapper.vm.results).toHaveLength(3)
    expect(wrapper.vm.results[0].teaching_office_name).toBe('计算机科学教研室')
    expect(wrapper.vm.results[0].final_score).toBe(92.5)
    expect(wrapper.vm.results[1].teaching_office_name).toBe('数学教研室')
    expect(wrapper.vm.results[1].final_score).toBe(88.3)
  })

  it('displays approval results - Requirement 14.8', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Requirement 14.8: 管理端显示审定结果
    expect(wrapper.vm.results[0].approval_status).toBe('approved')
    expect(wrapper.vm.results[1].approval_status).toBe('approved')
    expect(wrapper.vm.results[2].approval_status).toBe('rejected')
    expect(wrapper.vm.results[2].reject_reason).toBeTruthy()
  })

  it('calculates statistics correctly', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.publishedCount).toBe(2)
    expect(wrapper.vm.averageScore).toBeCloseTo(86.43, 1)
    expect(wrapper.vm.highestScore).toBe(92.5)
  })

  it('filters results by year', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.filters.year = 2023
    await wrapper.vm.loadResults()

    expect(managementResultApi.getAllResults).toHaveBeenCalledWith({
      year: 2023,
      status: undefined
    })
  })

  it('filters results by status', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.filters.status = 'published'
    await wrapper.vm.loadResults()

    expect(managementResultApi.getAllResults).toHaveBeenCalledWith({
      year: expect.any(Number),
      status: 'published'
    })
  })

  it('sorts results correctly', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    // Default sort by final_score descending
    expect(wrapper.vm.sortedResults[0].final_score).toBe(92.5)
    expect(wrapper.vm.sortedResults[2].final_score).toBe(78.5)
  })

  it('paginates results correctly', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    wrapper.vm.pagination.pageSize = 2
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.paginatedResults).toHaveLength(2)
  })

  it('opens detail dialog when viewing detail', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    wrapper.vm.viewDetail(mockResultsData[0])
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.detailDialogVisible).toBe(true)
    expect(wrapper.vm.selectedResult?.id).toBe('1')
  })

  it('opens reject reason dialog for rejected results', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    wrapper.vm.viewRejectReason(mockResultsData[2])
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.rejectDialogVisible).toBe(true)
    expect(wrapper.vm.selectedResult?.reject_reason).toBeTruthy()
  })

  it('gets correct score tag type', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.getScoreTagType(92.5)).toBe('success')
    expect(wrapper.vm.getScoreTagType(85.0)).toBe('warning')
    expect(wrapper.vm.getScoreTagType(75.0)).toBe('danger')
  })

  it('gets correct approval labels', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.getApprovalLabel('approved')).toBe('已同意')
    expect(wrapper.vm.getApprovalLabel('rejected')).toBe('已驳回')
    expect(wrapper.vm.getApprovalLabel('pending')).toBe('待审定')
  })

  it('formats dates correctly', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    const formattedDate = wrapper.vm.formatDate('2024-01-25T10:30:00')
    expect(formattedDate).toContain('2024')
  })

  it('shows error message when loading fails', async () => {
    const mockError = {
      response: {
        data: {
          detail: '加载失败'
        }
      }
    }

    vi.mocked(managementResultApi.getAllResults).mockRejectedValue(mockError)

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(ElMessage.error).toHaveBeenCalled()
  })

  it('resets filters correctly', async () => {
    vi.mocked(managementResultApi.getAllResults).mockResolvedValue({ data: mockResultsData })

    const wrapper = mount(ManagementResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-select': true,
          'el-option': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-row': true,
          'el-col': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-divider': true,
          'el-alert': true,
          'el-empty': true,
          'el-pagination': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    wrapper.vm.filters.year = 2023
    wrapper.vm.filters.status = 'published'
    
    wrapper.vm.resetFilters()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.filters.year).toBe(new Date().getFullYear())
    expect(wrapper.vm.filters.status).toBe('')
  })
})
