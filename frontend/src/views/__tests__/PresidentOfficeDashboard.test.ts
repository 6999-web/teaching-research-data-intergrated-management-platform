import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PresidentOfficeDashboard from '../PresidentOfficeDashboard.vue'
import { ElMessage } from 'element-plus'

// Mock the API client
vi.mock('@/api/client', () => ({
  presidentOfficeApi: {
    getDashboardData: vi.fn(() => Promise.resolve({
      data: {
        teaching_office_scores: [
          {
            teaching_office_id: '1',
            teaching_office_name: '计算机教研室',
            evaluation_year: 2024,
            ai_score: 85.5,
            manual_scores: [
              {
                reviewer_name: '张三',
                reviewer_role: 'evaluation_team',
                total_score: 88.0
              }
            ],
            final_score: 87.0,
            status: 'finalized'
          },
          {
            teaching_office_id: '2',
            teaching_office_name: '数学教研室',
            evaluation_year: 2024,
            ai_score: 82.0,
            manual_scores: [],
            final_score: 83.5,
            status: 'finalized'
          }
        ],
        historical_scores: [],
        indicator_comparisons: []
      }
    })),
    getHistoricalScores: vi.fn(() => Promise.resolve({
      data: [
        {
          teaching_office_id: '1',
          teaching_office_name: '计算机教研室',
          scores: [
            { year: 2023, final_score: 85.0 },
            { year: 2024, final_score: 87.0 }
          ]
        }
      ]
    })),
    approveResults: vi.fn(() => Promise.resolve({
      data: {
        approval_id: 'approval-123',
        decision: 'approve',
        approved_at: '2024-01-01T12:00:00',
        message: 'Approval successful. Management office can now initiate publication.',
        synced_to_management: true
      }
    }))
  }
}))

// Mock ElMessage
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn()
    }
  }
})

describe('PresidentOfficeDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard title', () => {
    const wrapper = mount(PresidentOfficeDashboard)
    expect(wrapper.find('h1').text()).toBe('校长办公会 - 实时数据监控')
  })

  it('displays filter controls', () => {
    const wrapper = mount(PresidentOfficeDashboard)
    expect(wrapper.find('.filter-card').exists()).toBe(true)
  })

  it('loads dashboard data on mount', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(wrapper.vm.dashboardData.teaching_office_scores.length).toBeGreaterThan(0)
  })

  it('displays summary cards with statistics', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const summaryCards = wrapper.findAll('.stat-card')
    expect(summaryCards.length).toBe(4)
  })

  it('displays scores table', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(wrapper.find('.scores-table-card').exists()).toBe(true)
  })

  it('calculates average AI score correctly', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const avgAIScore = wrapper.vm.averageAIScore
    expect(avgAIScore).toBeGreaterThan(0)
  })

  it('calculates average final score correctly', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const avgFinalScore = wrapper.vm.averageFinalScore
    expect(avgFinalScore).toBeGreaterThan(0)
  })

  it('sorts scores based on selected criteria', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.filters.sortBy = 'final_score'
    wrapper.vm.filters.sortOrder = 'desc'
    await wrapper.vm.$nextTick()
    
    const sortedScores = wrapper.vm.sortedScores
    expect(sortedScores.length).toBeGreaterThan(0)
    
    // Verify descending order
    for (let i = 0; i < sortedScores.length - 1; i++) {
      const current = sortedScores[i].final_score || 0
      const next = sortedScores[i + 1].final_score || 0
      expect(current).toBeGreaterThanOrEqual(next)
    }
  })

  it('displays ranking chart', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const rankedScores = wrapper.vm.rankedScores
    expect(rankedScores.length).toBeGreaterThan(0)
  })

  it('filters data by year', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    wrapper.vm.filters.year = 2024
    await wrapper.vm.loadData()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.dashboardData.teaching_office_scores.length).toBeGreaterThan(0)
  })

  it('filters data by indicator', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    wrapper.vm.filters.indicator = 'teaching_reform_projects'
    await wrapper.vm.loadData()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.filters.indicator).toBe('teaching_reform_projects')
  })

  it('displays status labels correctly', () => {
    const wrapper = mount(PresidentOfficeDashboard)
    
    expect(wrapper.vm.getStatusLabel('draft')).toBe('草稿')
    expect(wrapper.vm.getStatusLabel('submitted')).toBe('已提交')
    expect(wrapper.vm.getStatusLabel('finalized')).toBe('已确定最终得分')
  })

  it('opens detail dialog when view details is clicked', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const testOffice = wrapper.vm.dashboardData.teaching_office_scores[0]
    wrapper.vm.viewDetails(testOffice)
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.detailDialogVisible).toBe(true)
    expect(wrapper.vm.selectedOffice).toEqual(testOffice)
  })

  it('loads historical data when office is selected', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.selectedOfficeForHistory = '1'
    await wrapper.vm.loadHistoricalData()
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.historicalData.length).toBeGreaterThan(0)
  })

  it('displays approval actions card', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(wrapper.find('.approval-actions-card').exists()).toBe(true)
  })

  it('shows only finalizable offices for approval', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const finalizableOffices = wrapper.vm.finalizableOffices
    expect(finalizableOffices.length).toBe(2)
    finalizableOffices.forEach((office: any) => {
      expect(office.final_score).toBeDefined()
      expect(office.status).toBe('finalized')
    })
  })

  it('disables approval buttons when no offices selected', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.selectedEvaluationIds = []
    await wrapper.vm.$nextTick()
    
    const approveButton = wrapper.findAll('.approval-buttons button')[0]
    const rejectButton = wrapper.findAll('.approval-buttons button')[1]
    
    expect(approveButton.attributes('disabled')).toBeDefined()
    expect(rejectButton.attributes('disabled')).toBeDefined()
  })

  it('opens approval dialog for approve decision', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.selectedEvaluationIds = ['1']
    wrapper.vm.openApprovalDialog('approve')
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.approvalDialogVisible).toBe(true)
    expect(wrapper.vm.approvalDecision).toBe('approve')
  })

  it('opens approval dialog for reject decision', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.selectedEvaluationIds = ['1']
    wrapper.vm.openApprovalDialog('reject')
    await wrapper.vm.$nextTick()
    
    expect(wrapper.vm.approvalDialogVisible).toBe(true)
    expect(wrapper.vm.approvalDecision).toBe('reject')
  })

  it('validates reject reason when rejecting', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.selectedEvaluationIds = ['1']
    wrapper.vm.approvalDecision = 'reject'
    wrapper.vm.approvalForm.rejectReason = ''
    
    await wrapper.vm.submitApproval()
    await wrapper.vm.$nextTick()
    
    expect(ElMessage.error).toHaveBeenCalledWith('请填写驳回原因')
  })

  it('submits approval successfully', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.selectedEvaluationIds = ['1', '2']
    wrapper.vm.approvalDecision = 'approve'
    wrapper.vm.approvalDialogVisible = true
    
    await wrapper.vm.submitApproval()
    await wrapper.vm.$nextTick()
    
    // Wait for async approval
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(ElMessage.success).toHaveBeenCalled()
    expect(wrapper.vm.approvalDialogVisible).toBe(false)
    expect(wrapper.vm.selectedEvaluationIds.length).toBe(0)
  })

  it('submits rejection with reason successfully', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    wrapper.vm.selectedEvaluationIds = ['1']
    wrapper.vm.approvalDecision = 'reject'
    wrapper.vm.approvalForm.rejectReason = '数据不完整，需要重新审核'
    wrapper.vm.approvalDialogVisible = true
    
    await wrapper.vm.submitApproval()
    await wrapper.vm.$nextTick()
    
    // Wait for async approval
    await new Promise(resolve => setTimeout(resolve, 100))
    
    expect(ElMessage.success).toHaveBeenCalled()
    expect(wrapper.vm.approvalDialogVisible).toBe(false)
  })

  it('gets office name by id correctly', async () => {
    const wrapper = mount(PresidentOfficeDashboard)
    await wrapper.vm.$nextTick()
    
    // Wait for async data loading
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const officeName = wrapper.vm.getOfficeName('1')
    expect(officeName).toBe('计算机教研室')
  })

  it('displays correct status labels for approved and rejected', () => {
    const wrapper = mount(PresidentOfficeDashboard)
    
    expect(wrapper.vm.getStatusLabel('approved')).toBe('已审定同意')
    expect(wrapper.vm.getStatusLabel('rejected_by_president')).toBe('已驳回')
  })
})

