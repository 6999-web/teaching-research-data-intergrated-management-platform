import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import ResultView from '../ResultView.vue'
import { resultApi } from '@/api/client'

// Mock the API
vi.mock('@/api/client', () => ({
  resultApi: {
    getResult: vi.fn(),
    getPublishedResults: vi.fn()
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
    }
  }
})

// Mock vue-router
vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: { id: 'eval-123' },
    query: {}
  })
}))

describe('ResultView.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const mockResultData = {
    evaluation_id: 'eval-123',
    teaching_office_id: 'office-001',
    teaching_office_name: '计算机教研室',
    evaluation_year: 2024,
    status: 'published',
    ai_score: {
      id: 'ai-001',
      evaluation_id: 'eval-123',
      total_score: 85.5,
      indicator_scores: [
        {
          indicator: 'teaching_process_management',
          score: 13,
          reasoning: '教学过程管理规范'
        },
        {
          indicator: 'course_construction',
          score: 14,
          reasoning: '课程建设成效显著'
        }
      ],
      parsed_reform_projects: 3,
      parsed_honorary_awards: 2,
      scored_at: '2024-01-20T10:00:00'
    },
    manual_scores: [
      {
        id: 'manual-001',
        evaluation_id: 'eval-123',
        reviewer_id: 'reviewer-001',
        reviewer_name: '张三',
        reviewer_role: 'evaluation_team',
        weight: 0.6,
        scores: [
          {
            indicator: 'teaching_process_management',
            score: 14,
            comment: '管理到位'
          }
        ],
        submitted_at: '2024-01-21T10:00:00'
      },
      {
        id: 'manual-002',
        evaluation_id: 'eval-123',
        reviewer_id: 'reviewer-002',
        reviewer_name: '李四',
        reviewer_role: 'evaluation_office',
        weight: 0.4,
        scores: [
          {
            indicator: 'teaching_process_management',
            score: 13,
            comment: '表现良好'
          }
        ],
        submitted_at: '2024-01-21T11:00:00'
      }
    ],
    final_score: {
      id: 'final-001',
      evaluation_id: 'eval-123',
      final_score: 87.5,
      summary: '综合各项评分，该教研室表现优秀',
      determined_by: 'admin-001',
      determined_at: '2024-01-22T10:00:00'
    },
    insight_summary: {
      id: 'insight-001',
      evaluation_id: 'eval-123',
      summary: '该教研室在教学过程管理、课程建设等方面表现突出，建议继续保持。',
      generated_at: '2024-01-23T10:00:00'
    },
    published_at: '2024-01-24T10:00:00',
    distributed_at: '2024-01-24T11:00:00'
  }

  it('renders result view page correctly', () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    expect(wrapper.find('h1').text()).toBe('考评结果查看')
  })

  it('displays final score correctly', async () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    // Wait for data to load
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.result?.final_score?.final_score).toBe(87.5)
    expect(wrapper.vm.result?.teaching_office_name).toBe('计算机教研室')
  })

  it('displays AI score details', async () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.result?.ai_score?.total_score).toBe(85.5)
    expect(wrapper.vm.result?.ai_score?.indicator_scores).toHaveLength(2)
  })

  it('displays all reviewer scores', async () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.result?.manual_scores).toHaveLength(2)
    expect(wrapper.vm.result?.manual_scores[0].reviewer_name).toBe('张三')
    expect(wrapper.vm.result?.manual_scores[1].reviewer_name).toBe('李四')
  })

  it('displays insight summary', async () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(wrapper.vm.result?.insight_summary?.summary).toContain('教学过程管理')
  })

  it('shows error message when loading fails', async () => {
    const mockError = {
      response: {
        data: {
          detail: '加载失败'
        }
      }
    }

    vi.mocked(resultApi.getResult).mockRejectedValue(mockError)

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(ElMessage.error).toHaveBeenCalled()
    expect(wrapper.vm.error).toBe('加载失败')
  })

  it('formats dates correctly', async () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    const formattedDate = wrapper.vm.formatDate('2024-01-24T10:00:00')
    expect(formattedDate).toContain('2024')
  })

  it('gets correct indicator labels', async () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    const label = wrapper.vm.getIndicatorLabel('teaching_process_management')
    expect(label).toBe('教学过程管理')
  })

  it('gets correct role labels', async () => {
    vi.mocked(resultApi.getResult).mockResolvedValue({ data: mockResultData })

    const wrapper = mount(ResultView, {
      global: {
        stubs: {
          'el-card': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-alert': true,
          'el-empty': true,
          'el-skeleton': true,
          'el-collapse': true,
          'el-collapse-item': true,
          'el-breadcrumb': true,
          'el-breadcrumb-item': true,
          'el-icon': true,
          'Document': true
        }
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.getRoleLabel('evaluation_team')).toBe('考评小组')
    expect(wrapper.vm.getRoleLabel('evaluation_office')).toBe('考评办公室')
  })
})
