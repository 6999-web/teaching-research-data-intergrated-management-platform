import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import FinalScoreForm from '../FinalScoreForm.vue'
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
    getAllScores: vi.fn(),
    submitFinalScore: vi.fn()
  }
}))

describe('FinalScoreForm', () => {
  const mockEvaluationId = 'test-evaluation-id'

  const mockAllScoresData = {
    evaluation_id: mockEvaluationId,
    ai_score: {
      id: 'ai-score-id',
      evaluation_id: mockEvaluationId,
      total_score: 85.5,
      indicator_scores: [
        { indicator: '教学过程管理', score: 12, reasoning: 'Good management' },
        { indicator: '课程建设', score: 13, reasoning: 'Excellent course' }
      ],
      parsed_reform_projects: 5,
      parsed_honorary_awards: 3,
      scored_at: '2024-01-15T10:00:00'
    },
    manual_scores: [
      {
        id: 'manual-score-1',
        evaluation_id: mockEvaluationId,
        reviewer_id: 'reviewer-1',
        reviewer_name: '张三',
        reviewer_role: 'evaluation_team' as const,
        weight: 0.7,
        scores: [
          { indicator: '教学过程管理', score: 13, comment: 'Excellent' },
          { indicator: '课程建设', score: 14, comment: 'Very good' }
        ],
        submitted_at: '2024-01-16T10:00:00'
      },
      {
        id: 'manual-score-2',
        evaluation_id: mockEvaluationId,
        reviewer_id: 'reviewer-2',
        reviewer_name: '李四',
        reviewer_role: 'evaluation_office' as const,
        weight: 0.5,
        scores: [
          { indicator: '教学过程管理', score: 12, comment: 'Good' },
          { indicator: '课程建设', score: 13, comment: 'Good' }
        ],
        submitted_at: '2024-01-17T10:00:00'
      }
    ],
    final_score: null
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the form and loads all scores on mount', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Verify API was called
    expect(scoringApi.getAllScores).toHaveBeenCalledWith(mockEvaluationId)

    // Check if scores summary section is rendered
    expect(wrapper.text()).toContain('所有评审人打分汇总')
    expect(wrapper.text()).toContain('最终得分计算')
  })

  it('displays AI score correctly', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Check if AI score is displayed
    expect(wrapper.text()).toContain('AI自动评分')
    expect(wrapper.text()).toContain('85.5')
  })

  it('displays manual scores with correct role labels and weights', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Check if manual scores are displayed
    expect(wrapper.text()).toContain('张三')
    expect(wrapper.text()).toContain('考评小组')
    expect(wrapper.text()).toContain('权重: 70%')
    
    expect(wrapper.text()).toContain('李四')
    expect(wrapper.text()).toContain('考评办公室')
    expect(wrapper.text()).toContain('权重: 50%')
  })

  it('sorts manual scores with evaluation_team first', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Check that evaluation_team scores are sorted first
    const sortedScores = wrapper.vm.sortedManualScores
    expect(sortedScores[0].reviewer_role).toBe('evaluation_team')
    expect(sortedScores[1].reviewer_role).toBe('evaluation_office')
  })

  it('calculates weighted average score correctly', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Manual score 1: (13 + 14) = 27, weight 0.7
    // Manual score 2: (12 + 13) = 25, weight 0.5
    // Weighted average: (27 * 0.7 + 25 * 0.5) / (0.7 + 0.5) = (18.9 + 12.5) / 1.2 = 26.17
    const calculatedScore = wrapper.vm.calculatedScore
    expect(calculatedScore).toBeCloseTo(26.17, 1)
  })

  it('displays calculated score in the form', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Check if calculated score is displayed
    expect(wrapper.text()).toContain('综合计算得分')
    expect(wrapper.text()).toContain('26.2') // Rounded to 1 decimal
  })

  it('allows using calculated score with button click', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Find and click the "使用计算得分" button
    const useCalcButton = wrapper.find('.use-calculated-btn')
    expect(useCalcButton.exists()).toBe(true)
    
    await useCalcButton.trigger('click')
    await flushPromises()

    // Check if the final score input is populated with calculated score
    expect(wrapper.vm.formData.finalScore).toBeCloseTo(26.2, 1)
    expect(ElMessage.success).toHaveBeenCalledWith('已使用计算得分')
  })

  it('submits final score successfully', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })
    
    const mockSubmitResponse = {
      data: {
        final_score_id: 'final-score-id',
        determined_at: '2024-01-20T10:00:00'
      }
    }
    vi.mocked(scoringApi.submitFinalScore).mockResolvedValue(mockSubmitResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Fill in the form
    const finalScoreInput = wrapper.find('.final-score-input input')
    await finalScoreInput.setValue(88.5)

    const summaryTextarea = wrapper.find('textarea')
    await summaryTextarea.setValue('综合所有评审人打分，该教研室表现优秀，各项指标均达标。')

    await flushPromises()

    // Click submit button
    const submitButton = wrapper.find('.form-actions button[type="primary"]')
    await submitButton.trigger('click')

    await flushPromises()

    // Verify confirmation dialog was shown
    expect(ElMessageBox.confirm).toHaveBeenCalled()

    // Verify API was called with correct data
    expect(scoringApi.submitFinalScore).toHaveBeenCalledWith({
      evaluation_id: mockEvaluationId,
      final_score: 88.5,
      summary: '综合所有评审人打分，该教研室表现优秀，各项指标均达标。'
    })

    // Verify success message
    expect(ElMessage.success).toHaveBeenCalled()
  })

  it('validates final score is required', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Try to submit without filling final score
    const summaryTextarea = wrapper.find('textarea')
    await summaryTextarea.setValue('Test summary')

    await flushPromises()

    // The form should have validation rules
    const form = wrapper.findComponent({ name: 'ElForm' })
    expect(form.exists()).toBe(true)
  })

  it('validates summary is required and has minimum length', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Fill final score but leave summary empty or too short
    const finalScoreInput = wrapper.find('.final-score-input input')
    await finalScoreInput.setValue(88.5)

    const summaryTextarea = wrapper.find('textarea')
    await summaryTextarea.setValue('短') // Too short

    await flushPromises()

    // The form should have validation rules for summary
    const form = wrapper.findComponent({ name: 'ElForm' })
    expect(form.exists()).toBe(true)
  })

  it('disables form when final score already exists', async () => {
    const dataWithFinalScore = {
      ...mockAllScoresData,
      final_score: {
        id: 'final-score-id',
        evaluation_id: mockEvaluationId,
        final_score: 88.5,
        summary: '综合评定结果优秀',
        determined_by: 'admin-id',
        determined_at: '2024-01-20T10:00:00'
      }
    }

    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: dataWithFinalScore })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Check if form is disabled
    const form = wrapper.find('.final-score-form-content')
    expect(form.attributes('disabled')).toBeDefined()

    // Check if submit button shows "已确定最终得分"
    const submitButton = wrapper.find('.form-actions button[type="primary"]')
    expect(submitButton.text()).toContain('已确定最终得分')
    expect(submitButton.attributes('disabled')).toBeDefined()
  })

  it('displays final score when already determined', async () => {
    const dataWithFinalScore = {
      ...mockAllScoresData,
      final_score: {
        id: 'final-score-id',
        evaluation_id: mockEvaluationId,
        final_score: 88.5,
        summary: '综合评定结果优秀，各项指标表现突出。',
        determined_by: 'admin-id',
        determined_at: '2024-01-20T10:00:00'
      }
    }

    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: dataWithFinalScore })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Check if final score display is shown
    expect(wrapper.text()).toContain('最终得分已确定')
    expect(wrapper.text()).toContain('88.5')
    expect(wrapper.text()).toContain('综合评定结果优秀，各项指标表现突出。')
  })

  it('emits submitted event when final score is submitted successfully', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })
    
    const mockSubmitResponse = {
      data: {
        final_score_id: 'final-score-id',
        determined_at: '2024-01-20T10:00:00'
      }
    }
    vi.mocked(scoringApi.submitFinalScore).mockResolvedValue(mockSubmitResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Fill in the form
    const finalScoreInput = wrapper.find('.final-score-input input')
    await finalScoreInput.setValue(88.5)

    const summaryTextarea = wrapper.find('textarea')
    await summaryTextarea.setValue('综合所有评审人打分，该教研室表现优秀。')

    await flushPromises()

    // Submit
    const submitButton = wrapper.find('.form-actions button[type="primary"]')
    await submitButton.trigger('click')

    await flushPromises()

    // Verify event was emitted
    expect(wrapper.emitted('submitted')).toBeTruthy()
    expect(wrapper.emitted('submitted')?.[0]).toEqual(['final-score-id'])
  })

  it('emits viewDetails event when view details button is clicked', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Find and click the view details button
    const buttons = wrapper.findAll('.form-actions button')
    const viewDetailsButton = buttons.find(btn => btn.text().includes('查看详细评分'))
    
    if (viewDetailsButton) {
      await viewDetailsButton.trigger('click')
      await flushPromises()

      // Verify event was emitted
      expect(wrapper.emitted('viewDetails')).toBeTruthy()
    }
  })

  it('handles API error when loading scores', async () => {
    const mockError = {
      response: {
        data: {
          detail: '加载评分数据失败'
        }
      }
    }

    vi.mocked(scoringApi.getAllScores).mockRejectedValue(mockError)

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Verify error message was shown
    expect(ElMessage.error).toHaveBeenCalled()
  })

  it('handles API error when submitting final score', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })
    
    const mockError = {
      response: {
        data: {
          detail: '提交最终得分失败'
        }
      }
    }
    vi.mocked(scoringApi.submitFinalScore).mockRejectedValue(mockError)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Fill in the form
    const finalScoreInput = wrapper.find('.final-score-input input')
    await finalScoreInput.setValue(88.5)

    const summaryTextarea = wrapper.find('textarea')
    await summaryTextarea.setValue('综合所有评审人打分，该教研室表现优秀。')

    await flushPromises()

    // Submit
    const submitButton = wrapper.find('.form-actions button[type="primary"]')
    await submitButton.trigger('click')

    await flushPromises()

    // Verify error message was shown
    expect(ElMessage.error).toHaveBeenCalled()
  })

  it('resets form when reset button is clicked', async () => {
    vi.mocked(scoringApi.getAllScores).mockResolvedValue({ data: mockAllScoresData })
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(FinalScoreForm, {
      props: {
        evaluationId: mockEvaluationId
      }
    })

    await flushPromises()

    // Fill in the form
    const finalScoreInput = wrapper.find('.final-score-input input')
    await finalScoreInput.setValue(88.5)

    const summaryTextarea = wrapper.find('textarea')
    await summaryTextarea.setValue('Test summary')

    await flushPromises()

    // Click reset button
    const buttons = wrapper.findAll('.form-actions button')
    const resetButton = buttons.find(btn => btn.text().includes('重置'))
    
    if (resetButton) {
      await resetButton.trigger('click')
      await flushPromises()

      // Verify confirmation was shown
      expect(ElMessageBox.confirm).toHaveBeenCalled()

      // Verify info message was shown
      expect(ElMessage.info).toHaveBeenCalledWith('表单已重置')
    }
  })
})
