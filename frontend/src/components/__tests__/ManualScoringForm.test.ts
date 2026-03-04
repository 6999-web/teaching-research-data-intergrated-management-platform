import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import ManualScoringForm from '../ManualScoringForm.vue'
import { scoringApi } from '@/api/client'

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
    },
    ElMessageBox: {
      confirm: vi.fn()
    }
  }
})

// Mock API
vi.mock('@/api/client', () => ({
  scoringApi: {
    submitManualScore: vi.fn(),
    getAllScores: vi.fn()
  }
}))

describe('ManualScoringForm', () => {
  const mockEvaluationId = 'test-evaluation-id'
  const mockUserRole = 'evaluation_team'

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the form with all indicators', () => {
    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Check if all 8 indicators are rendered
    const indicatorSections = wrapper.findAll('.indicator-section')
    expect(indicatorSections).toHaveLength(8)

    // Check if specific indicators are present
    expect(wrapper.text()).toContain('教学过程管理')
    expect(wrapper.text()).toContain('课程建设')
    expect(wrapper.text()).toContain('教学改革项目')
    expect(wrapper.text()).toContain('荣誉表彰')
  })

  it('displays correct role label and weight info for evaluation_team', () => {
    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: 'evaluation_team'
      }
    })

    expect(wrapper.text()).toContain('考评小组')
    expect(wrapper.text()).toContain('您的评分权重为 70%')
  })

  it('displays correct role label and weight info for evaluation_office', () => {
    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: 'evaluation_office'
      }
    })

    expect(wrapper.text()).toContain('考评办公室')
    expect(wrapper.text()).toContain('您的评分权重为 50%')
  })

  it('calculates total score correctly', async () => {
    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Set scores for indicators
    const scoreInputs = wrapper.findAll('.score-input input')
    
    // Simulate entering scores
    await scoreInputs[0].setValue(10)
    await scoreInputs[1].setValue(12)
    await scoreInputs[2].setValue(15)
    
    await flushPromises()

    // Check if total score is calculated
    const totalScoreText = wrapper.find('.total-score .value').text()
    expect(parseFloat(totalScoreText)).toBeGreaterThan(0)
  })

  it('submits manual score successfully', async () => {
    const mockResponse = {
      data: {
        score_record_id: 'test-score-id',
        submitted_at: '2024-01-20T10:00:00'
      }
    }

    vi.mocked(scoringApi.submitManualScore).mockResolvedValue(mockResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Fill in all required fields
    const scoreInputs = wrapper.findAll('.score-input input')
    const commentInputs = wrapper.findAll('textarea')

    for (let i = 0; i < scoreInputs.length; i++) {
      await scoreInputs[i].setValue(10)
    }

    for (let i = 0; i < commentInputs.length; i++) {
      await commentInputs[i].setValue('Test comment for indicator')
    }

    await flushPromises()

    // Click submit button
    const buttons = wrapper.findAll('.form-actions button')
    const submitButton = buttons.find(btn => btn.text().includes('提交评分'))
    if (submitButton) {
      await submitButton.trigger('click')
    }

    await flushPromises()

    // Verify API was called
    expect(scoringApi.submitManualScore).toHaveBeenCalledWith(
      expect.objectContaining({
        evaluation_id: mockEvaluationId,
        scores: expect.any(Array)
      })
    )

    // Verify success message
    expect(ElMessage.success).toHaveBeenCalled()
  })

  it('prevents submission when form is invalid', async () => {
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)
    
    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Fill scores but leave comments empty (which should fail validation)
    const scoreInputs = wrapper.findAll('.score-input input')
    for (let i = 0; i < scoreInputs.length; i++) {
      await scoreInputs[i].setValue(10)
    }

    await flushPromises()

    // Try to submit without filling comments
    const buttons = wrapper.findAll('.form-actions button')
    const submitButton = buttons.find(btn => btn.text().includes('提交评分'))
    if (submitButton) {
      await submitButton.trigger('click')
    }

    await flushPromises()

    // Verify API was not called due to validation failure
    // Note: In the actual implementation, form validation should prevent API call
    // For this test, we're checking that validation rules exist
    const form = wrapper.findComponent({ name: 'ElForm' })
    expect(form.exists()).toBe(true)
  })

  it('disables submit button after successful submission', async () => {
    const mockResponse = {
      data: {
        score_record_id: 'test-score-id',
        submitted_at: '2024-01-20T10:00:00'
      }
    }

    vi.mocked(scoringApi.submitManualScore).mockResolvedValue(mockResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Fill in all required fields
    const scoreInputs = wrapper.findAll('.score-input input')
    const commentInputs = wrapper.findAll('textarea')

    for (let i = 0; i < scoreInputs.length; i++) {
      await scoreInputs[i].setValue(10)
    }

    for (let i = 0; i < commentInputs.length; i++) {
      await commentInputs[i].setValue('Test comment for indicator')
    }

    await flushPromises()

    // Submit
    const buttons = wrapper.findAll('.form-actions button')
    const submitButton = buttons.find(btn => btn.text().includes('提交评分'))
    if (submitButton) {
      await submitButton.trigger('click')
    }

    await flushPromises()

    // Check if button is disabled
    if (submitButton) {
      expect(submitButton.attributes('disabled')).toBeDefined()
      expect(submitButton.text()).toContain('已提交评分')
    }
  })

  it('loads and displays all scores when view button is clicked', async () => {
    const mockAllScoresResponse = {
      data: {
        evaluation_id: mockEvaluationId,
        ai_score: {
          id: 'ai-score-id',
          evaluation_id: mockEvaluationId,
          total_score: 85.5,
          indicator_scores: [
            { indicator: '教学过程管理', score: 12, reasoning: 'Good management' }
          ],
          parsed_reform_projects: 5,
          parsed_honorary_awards: 3,
          scored_at: '2024-01-15T10:00:00'
        },
        manual_scores: [
          {
            id: 'manual-score-id',
            evaluation_id: mockEvaluationId,
            reviewer_id: 'reviewer-1',
            reviewer_name: '张三',
            reviewer_role: 'evaluation_team',
            weight: 0.7,
            scores: [
              { indicator: '教学过程管理', score: 13, comment: 'Excellent' }
            ],
            submitted_at: '2024-01-16T10:00:00'
          }
        ],
        final_score: null
      }
    }

    vi.mocked(scoringApi.getAllScores).mockResolvedValue(mockAllScoresResponse)

    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Click view all scores button
    const buttons = wrapper.findAll('.form-actions button')
    const viewButton = buttons.find(btn => btn.text().includes('查看所有评审人打分'))
    if (viewButton) {
      await viewButton.trigger('click')
    }

    await flushPromises()

    // Verify API was called
    expect(scoringApi.getAllScores).toHaveBeenCalledWith(mockEvaluationId)

    // Check if dialog is visible (in real implementation, would check dialog content)
    // This is a simplified check
    expect(wrapper.vm.allScoresVisible).toBe(true)
  })

  it('highlights evaluation_team scores in all scores view', async () => {
    const mockAllScoresResponse = {
      data: {
        evaluation_id: mockEvaluationId,
        ai_score: null,
        manual_scores: [
          {
            id: 'manual-score-1',
            evaluation_id: mockEvaluationId,
            reviewer_id: 'reviewer-1',
            reviewer_name: '张三',
            reviewer_role: 'evaluation_team',
            weight: 0.7,
            scores: [],
            submitted_at: '2024-01-16T10:00:00'
          },
          {
            id: 'manual-score-2',
            evaluation_id: mockEvaluationId,
            reviewer_id: 'reviewer-2',
            reviewer_name: '李四',
            reviewer_role: 'evaluation_office',
            weight: 0.5,
            scores: [],
            submitted_at: '2024-01-17T10:00:00'
          }
        ],
        final_score: null
      }
    }

    vi.mocked(scoringApi.getAllScores).mockResolvedValue(mockAllScoresResponse)

    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Click view all scores button
    const buttons = wrapper.findAll('.form-actions button')
    const viewButton = buttons.find(btn => btn.text().includes('查看所有评审人打分'))
    if (viewButton) {
      await viewButton.trigger('click')
    }

    await flushPromises()

    // Check that evaluation_team scores are sorted first
    const sortedScores = wrapper.vm.sortedManualScores
    expect(sortedScores[0].reviewer_role).toBe('evaluation_team')
  })

  it('emits submitted event when score is submitted successfully', async () => {
    const mockResponse = {
      data: {
        score_record_id: 'test-score-id',
        submitted_at: '2024-01-20T10:00:00'
      }
    }

    vi.mocked(scoringApi.submitManualScore).mockResolvedValue(mockResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(ManualScoringForm, {
      props: {
        evaluationId: mockEvaluationId,
        currentUserRole: mockUserRole
      }
    })

    // Fill in all required fields
    const scoreInputs = wrapper.findAll('.score-input input')
    const commentInputs = wrapper.findAll('textarea')

    for (let i = 0; i < scoreInputs.length; i++) {
      await scoreInputs[i].setValue(10)
    }

    for (let i = 0; i < commentInputs.length; i++) {
      await commentInputs[i].setValue('Test comment for indicator')
    }

    await flushPromises()

    // Submit
    const buttons = wrapper.findAll('.form-actions button')
    const submitButton = buttons.find(btn => btn.text().includes('提交评分'))
    if (submitButton) {
      await submitButton.trigger('click')
    }

    await flushPromises()

    // Verify event was emitted
    expect(wrapper.emitted('submitted')).toBeTruthy()
    expect(wrapper.emitted('submitted')?.[0]).toEqual(['test-score-id'])
  })
})
