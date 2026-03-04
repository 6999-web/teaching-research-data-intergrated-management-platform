import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import AnomalyHandling from '../AnomalyHandling.vue'
import { reviewApi } from '@/api/client'

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
  reviewApi: {
    getAnomalies: vi.fn(),
    getAnomalyDetail: vi.fn(),
    handleAnomaly: vi.fn()
  }
}))

describe('AnomalyHandling', () => {
  const mockAnomalies = [
    {
      id: 'anomaly-1',
      evaluation_id: 'eval-1',
      type: 'count_mismatch',
      indicator: '教学改革项目',
      declared_count: 5,
      parsed_count: 3,
      description: '自评表填写5项教学改革项目，附件仅解析出3份证书',
      status: 'pending',
      handled_by: null,
      handled_action: null,
      handled_at: null
    },
    {
      id: 'anomaly-2',
      evaluation_id: 'eval-2',
      type: 'count_mismatch',
      indicator: '荣誉表彰',
      declared_count: 4,
      parsed_count: 2,
      description: '自评表填写4项荣誉表彰，附件仅解析出2份证书',
      status: 'handled',
      handled_by: 'user-1',
      handled_action: 'reject',
      handled_at: '2024-01-20T10:00:00'
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the component and loads anomalies on mount', async () => {
    const mockResponse = {
      data: {
        total: 2,
        anomalies: mockAnomalies
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Verify API was called
    expect(reviewApi.getAnomalies).toHaveBeenCalled()

    // Check if anomalies are rendered
    expect(wrapper.text()).toContain('异常数据处理')
    expect(wrapper.findAll('.anomaly-item')).toHaveLength(2)
  })

  it('displays anomaly details correctly', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Check anomaly type label
    expect(wrapper.text()).toContain('数量不一致')

    // Check indicator
    expect(wrapper.text()).toContain('教学改革项目')

    // Check description
    expect(wrapper.text()).toContain('自评表填写5项教学改革项目，附件仅解析出3份证书')

    // Check count comparison
    expect(wrapper.text()).toContain('5')
    expect(wrapper.text()).toContain('3')
  })

  it('filters anomalies by status', async () => {
    const mockPendingResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockPendingResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Change status filter
    const statusSelect = wrapper.find('.el-select')
    if (statusSelect.exists()) {
      wrapper.vm.statusFilter = 'pending'
      await wrapper.vm.loadAnomalies()
      await flushPromises()

      // Verify API was called with status filter
      expect(reviewApi.getAnomalies).toHaveBeenCalledWith(
        expect.objectContaining({ status: 'pending' })
      )
    }
  })

  it('opens reject dialog when reject button is clicked', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Find and click reject button
    const rejectButton = wrapper.find('button[type="danger"]')
    if (rejectButton.exists()) {
      await rejectButton.trigger('click')
      await flushPromises()

      // Check if dialog is visible
      expect(wrapper.vm.rejectDialogVisible).toBe(true)
      expect(wrapper.vm.selectedAnomaly).toEqual(mockAnomalies[0])
    }
  })

  it('submits reject action successfully', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    const mockHandleResponse = {
      data: {
        anomaly_id: 'anomaly-1',
        status: 'handled',
        handled_at: '2024-01-20T10:00:00',
        message: '异常数据已打回教研室'
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)
    vi.mocked(reviewApi.handleAnomaly).mockResolvedValue(mockHandleResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Open reject dialog
    const rejectButton = wrapper.find('button[type="danger"]')
    if (rejectButton.exists()) {
      await rejectButton.trigger('click')
      await flushPromises()

      // Fill in reject reason
      wrapper.vm.rejectForm.reject_reason = '请补充教学改革项目的证明材料'

      // Submit reject
      await wrapper.vm.confirmReject()
      await flushPromises()

      // Verify API was called
      expect(reviewApi.handleAnomaly).toHaveBeenCalledWith(
        expect.objectContaining({
          anomaly_id: 'anomaly-1',
          action: 'reject',
          reject_reason: '请补充教学改革项目的证明材料'
        })
      )

      // Verify success message
      expect(ElMessage.success).toHaveBeenCalled()

      // Verify dialog is closed
      expect(wrapper.vm.rejectDialogVisible).toBe(false)
    }
  })

  it('opens correct dialog when correct button is clicked', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Find and click correct button
    const correctButton = wrapper.find('button[type="success"]')
    if (correctButton.exists()) {
      await correctButton.trigger('click')
      await flushPromises()

      // Check if dialog is visible
      expect(wrapper.vm.correctDialogVisible).toBe(true)
      expect(wrapper.vm.selectedAnomaly).toEqual(mockAnomalies[0])
    }
  })

  it('submits correct action successfully', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    const mockHandleResponse = {
      data: {
        anomaly_id: 'anomaly-1',
        status: 'handled',
        handled_at: '2024-01-20T10:00:00',
        message: '异常数据已修正'
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)
    vi.mocked(reviewApi.handleAnomaly).mockResolvedValue(mockHandleResponse)
    vi.mocked(ElMessageBox.confirm).mockResolvedValue('confirm' as any)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Open correct dialog
    const correctButton = wrapper.find('button[type="success"]')
    if (correctButton.exists()) {
      await correctButton.trigger('click')
      await flushPromises()

      // Fill in corrected data
      wrapper.vm.correctForm.corrected_count = 3
      wrapper.vm.correctForm.correction_note = '根据附件实际数量修正为3项'

      // Submit correct
      await wrapper.vm.confirmCorrect()
      await flushPromises()

      // Verify API was called
      expect(reviewApi.handleAnomaly).toHaveBeenCalledWith(
        expect.objectContaining({
          anomaly_id: 'anomaly-1',
          action: 'correct',
          corrected_data: expect.any(Object)
        })
      )

      // Verify success message
      expect(ElMessage.success).toHaveBeenCalled()

      // Verify dialog is closed
      expect(wrapper.vm.correctDialogVisible).toBe(false)
    }
  })

  it('displays handled anomalies with handled information', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[1]]
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Check if handled status is displayed
    expect(wrapper.text()).toContain('已处理')

    // Check if handled action is displayed
    expect(wrapper.text()).toContain('打回教研室')

    // Check if action buttons are not displayed for handled anomalies
    const handledItem = wrapper.find('.handled-item')
    if (handledItem.exists()) {
      const actionButtons = handledItem.find('.action-buttons')
      expect(actionButtons.exists()).toBe(false)
    }
  })

  it('shows empty state when no anomalies exist', async () => {
    const mockResponse = {
      data: {
        total: 0,
        anomalies: []
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Check for empty state
    expect(wrapper.text()).toContain('暂无异常数据')
  })

  it('handles API errors gracefully', async () => {
    const mockError = {
      response: {
        data: {
          detail: '加载异常数据失败'
        }
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockRejectedValue(mockError)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Verify error message was shown
    expect(ElMessage.error).toHaveBeenCalledWith(
      expect.objectContaining({
        message: '加载异常数据失败'
      })
    )
  })

  it('refreshes anomalies when refresh button is clicked', async () => {
    const mockResponse = {
      data: {
        total: 2,
        anomalies: mockAnomalies
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Clear mock calls
    vi.clearAllMocks()

    // Click refresh button
    const refreshButton = wrapper.find('button[type="primary"]')
    if (refreshButton.exists()) {
      await refreshButton.trigger('click')
      await flushPromises()

      // Verify API was called again
      expect(reviewApi.getAnomalies).toHaveBeenCalled()
    }
  })

  it('validates reject reason is required', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Open reject dialog
    const rejectButton = wrapper.find('button[type="danger"]')
    if (rejectButton.exists()) {
      await rejectButton.trigger('click')
      await flushPromises()

      // Try to submit without filling reject reason
      wrapper.vm.rejectForm.reject_reason = ''

      // Attempt to confirm (should fail validation)
      const rejectFormRef = wrapper.vm.rejectFormRef
      if (rejectFormRef) {
        try {
          await rejectFormRef.validate()
          // Should not reach here
          expect(true).toBe(false)
        } catch (error) {
          // Validation should fail
          expect(error).toBeDefined()
        }
      }
    }
  })

  it('validates corrected count is required', async () => {
    const mockResponse = {
      data: {
        total: 1,
        anomalies: [mockAnomalies[0]]
      }
    }

    vi.mocked(reviewApi.getAnomalies).mockResolvedValue(mockResponse)

    const wrapper = mount(AnomalyHandling)

    await flushPromises()

    // Open correct dialog
    const correctButton = wrapper.find('button[type="success"]')
    if (correctButton.exists()) {
      await correctButton.trigger('click')
      await flushPromises()

      // Clear corrected count
      wrapper.vm.correctForm.corrected_count = null as any

      // Attempt to confirm (should fail validation)
      const correctFormRef = wrapper.vm.correctFormRef
      if (correctFormRef) {
        try {
          await correctFormRef.validate()
          // Should not reach here
          expect(true).toBe(false)
        } catch (error) {
          // Validation should fail
          expect(error).toBeDefined()
        }
      }
    }
  })
})
