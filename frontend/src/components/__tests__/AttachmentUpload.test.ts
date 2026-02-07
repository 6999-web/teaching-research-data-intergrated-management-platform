import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import AttachmentUpload from '../AttachmentUpload.vue'
import { INDICATORS } from '@/types/attachment'

// Mock ElMessage and ElMessageBox
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

// Mock API client
vi.mock('@/api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn()
  }
}))

describe('AttachmentUpload', () => {
  const defaultProps = {
    evaluationId: 'test-eval-001',
    evaluationYear: 2024,
    isLocked: false,
    initialAttachments: []
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the attachment upload component', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    expect(wrapper.find('.attachment-upload').exists()).toBe(true)
    expect(wrapper.text()).toContain('附件上传')
    expect(wrapper.text()).toContain('2024年度')
  })

  it('displays the indicator table with all indicators', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    expect(wrapper.text()).toContain('考核指标对应表')
    
    // Check if all indicators are displayed
    INDICATORS.forEach(indicator => {
      expect(wrapper.text()).toContain(indicator.label)
      expect(wrapper.text()).toContain(indicator.description)
    })
  })

  it('shows certificate and project type tags in indicator table', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    // Check for certificate and project type tags
    expect(wrapper.text()).toContain('证书类')
    expect(wrapper.text()).toContain('项目类')
  })

  it('displays file type support information in indicator table', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    // Check if file types are displayed
    INDICATORS.forEach(indicator => {
      const fileTypesText = indicator.fileTypes.join(', ')
      expect(wrapper.text()).toContain(fileTypesText)
    })
  })

  it('has indicator selection dropdown', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    expect(wrapper.text()).toContain('选择考核指标')
  })

  it('has upload component with drag and drop support', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    expect(wrapper.text()).toContain('将文件拖到此处')
    expect(wrapper.text()).toContain('点击上传')
  })

  it('shows warning when no indicator is selected', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    expect(wrapper.text()).toContain('请先选择考核指标')
  })

  it('displays file size and count limits', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    expect(wrapper.text()).toContain('单个文件不超过50MB')
    expect(wrapper.text()).toContain('最多上传10个文件')
  })

  it('supports multiple file upload', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    // The upload component should have multiple attribute
    expect(wrapper.text()).toContain('支持多文件上传')
  })

  it('displays uploaded attachments list when attachments exist', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000,
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      },
      {
        id: 'att-002',
        evaluationId: 'test-eval-001',
        indicator: 'honorary_awards',
        fileName: 'award1.jpg',
        fileSize: 512000,
        fileType: 'jpg',
        uploadedAt: '2024-01-02T11:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        initialAttachments: attachments
      }
    })

    expect(wrapper.text()).toContain('已上传附件')
    expect(wrapper.text()).toContain('project1.pdf')
    expect(wrapper.text()).toContain('award1.jpg')
  })

  it('displays file size in human-readable format', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000, // 1000 KB
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        initialAttachments: attachments
      }
    })

    // Should display file size in KB or MB
    expect(wrapper.text()).toMatch(/KB|MB/)
  })

  it('displays formatted upload date', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000,
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        initialAttachments: attachments
      }
    })

    // Should display formatted date
    expect(wrapper.text()).toContain('2024')
  })

  it('has delete button for each uploaded attachment', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000,
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        initialAttachments: attachments
      }
    })

    expect(wrapper.text()).toContain('删除')
  })

  it('has back and submit buttons', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    const buttons = wrapper.findAll('button')
    const buttonTexts = buttons.map(btn => btn.text())

    expect(buttonTexts).toContain('返回')
    expect(buttonTexts).toContain('提交附件')
  })

  it('disables submit button when no attachments uploaded', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    const submitButton = wrapper.findAll('button').find(btn => btn.text() === '提交附件')
    expect(submitButton?.attributes('disabled')).toBeDefined()
  })

  it('enables submit button when attachments are uploaded', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000,
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        initialAttachments: attachments
      }
    })

    const submitButton = wrapper.findAll('button').find(btn => btn.text() === '提交附件')
    expect(submitButton?.attributes('disabled')).toBeUndefined()
  })

  it('shows lock alert when isLocked is true', () => {
    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        isLocked: true
      }
    })

    expect(wrapper.text()).toContain('附件已锁定')
    expect(wrapper.text()).toContain('表单和附件已提交并锁定')
  })

  it('disables delete buttons when locked', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000,
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        isLocked: true,
        initialAttachments: attachments
      }
    })

    const deleteButtons = wrapper.findAll('button').filter(btn => btn.text() === '删除')
    deleteButtons.forEach(btn => {
      expect(btn.attributes('disabled')).toBeDefined()
    })
  })

  it('disables submit button when locked', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000,
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        isLocked: true,
        initialAttachments: attachments
      }
    })

    const submitButton = wrapper.findAll('button').find(btn => btn.text() === '提交附件')
    expect(submitButton?.attributes('disabled')).toBeDefined()
  })

  it('emits back event when back button is clicked', async () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    const backButton = wrapper.findAll('button').find(btn => btn.text() === '返回')
    await backButton?.trigger('click')

    expect(wrapper.emitted('back')).toBeTruthy()
  })

  it('displays upload progress for uploading files', async () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    // Simulate uploading state by accessing component internals
    const component = wrapper.vm as any
    component.uploadingFiles = [
      {
        fileName: 'test.pdf',
        percentage: 50,
        status: 'uploading'
      }
    ]

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('上传进度')
    expect(wrapper.text()).toContain('test.pdf')
    expect(wrapper.text()).toContain('50%')
  })

  it('shows success status for completed uploads', async () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    const component = wrapper.vm as any
    component.uploadingFiles = [
      {
        fileName: 'test.pdf',
        percentage: 100,
        status: 'success'
      }
    ]

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('test.pdf')
    expect(wrapper.text()).toContain('100%')
  })

  it('shows error status for failed uploads', async () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    const component = wrapper.vm as any
    component.uploadingFiles = [
      {
        fileName: 'test.pdf',
        percentage: 50,
        status: 'error'
      }
    ]

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('test.pdf')
  })

  it('supports certificate type files', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    // Check that certificate indicators are present
    const certificateIndicators = INDICATORS.filter(i => i.category === 'certificate')
    certificateIndicators.forEach(indicator => {
      expect(wrapper.text()).toContain(indicator.label)
    })
  })

  it('supports project type files', () => {
    const wrapper = mount(AttachmentUpload, {
      props: defaultProps
    })

    // Check that project indicators are present
    const projectIndicators = INDICATORS.filter(i => i.category === 'project')
    projectIndicators.forEach(indicator => {
      expect(wrapper.text()).toContain(indicator.label)
    })
  })

  it('displays indicator label for uploaded attachments', () => {
    const attachments = [
      {
        id: 'att-001',
        evaluationId: 'test-eval-001',
        indicator: 'teaching_reform_projects',
        fileName: 'project1.pdf',
        fileSize: 1024000,
        fileType: 'pdf',
        uploadedAt: '2024-01-01T10:00:00Z'
      }
    ]

    const wrapper = mount(AttachmentUpload, {
      props: {
        ...defaultProps,
        initialAttachments: attachments
      }
    })

    expect(wrapper.text()).toContain('教学改革项目')
  })
})
