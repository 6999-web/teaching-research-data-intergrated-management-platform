import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import SelfEvaluationForm from '../SelfEvaluationForm.vue'

// Mock ElMessage
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

describe('SelfEvaluationForm', () => {
  const defaultProps = {
    teachingOfficeId: 'test-office-001',
    evaluationYear: 2024
  }

  it('renders the form with all required fields', () => {
    const wrapper = mount(SelfEvaluationForm, {
      props: defaultProps
    })

    // Check if form is rendered
    expect(wrapper.find('.self-evaluation-form').exists()).toBe(true)
    expect(wrapper.find('.evaluation-form').exists()).toBe(true)

    // Check if all form fields exist
    expect(wrapper.text()).toContain('教学过程管理')
    expect(wrapper.text()).toContain('课程建设')
    expect(wrapper.text()).toContain('教学改革项目个数')
    expect(wrapper.text()).toContain('荣誉表彰个数')
    expect(wrapper.text()).toContain('教学质量')
    expect(wrapper.text()).toContain('学生指导')
    expect(wrapper.text()).toContain('科研工作')
    expect(wrapper.text()).toContain('团队建设')
  })

  it('displays the evaluation year in the header', () => {
    const wrapper = mount(SelfEvaluationForm, {
      props: defaultProps
    })

    expect(wrapper.text()).toContain('2024年度')
  })

  it('has save, preview, and reset buttons', () => {
    const wrapper = mount(SelfEvaluationForm, {
      props: defaultProps
    })

    const buttons = wrapper.findAll('button')
    const buttonTexts = buttons.map(btn => btn.text())

    expect(buttonTexts).toContain('保存')
    expect(buttonTexts).toContain('预览')
    expect(buttonTexts).toContain('重置')
  })

  it('initializes with provided initial data', () => {
    const initialData = {
      teachingOfficeId: 'test-office-001',
      evaluationYear: 2024,
      content: {
        teachingProcessManagement: '测试教学过程管理内容',
        courseConstruction: '测试课程建设内容',
        teachingReformProjects: 5,
        honoraryAwards: 3,
        teachingQuality: '测试教学质量内容',
        studentGuidance: '测试学生指导内容',
        scientificResearch: '测试科研工作内容',
        teamBuilding: '测试团队建设内容'
      }
    }

    const wrapper = mount(SelfEvaluationForm, {
      props: {
        ...defaultProps,
        initialData
      }
    })

    // Verify the form is populated with initial data
    const textareas = wrapper.findAll('textarea')
    expect(textareas[0].element.value).toBe('测试教学过程管理内容')
    expect(textareas[1].element.value).toBe('测试课程建设内容')
  })

  it('validates required fields', async () => {
    const wrapper = mount(SelfEvaluationForm, {
      props: defaultProps
    })

    // Try to save without filling required fields
    const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
    await saveButton?.trigger('click')

    // Form validation should prevent save
    // The component should show validation errors
    expect(wrapper.vm).toBeDefined()
  })

  it('emits save event with form data when save button is clicked', async () => {
    const wrapper = mount(SelfEvaluationForm, {
      props: defaultProps
    })

    // Fill in all required fields with valid data
    const formData = {
      teachingOfficeId: 'test-office-001',
      evaluationYear: 2024,
      content: {
        teachingProcessManagement: '测试教学过程管理内容，至少十个字符',
        courseConstruction: '测试课程建设内容，至少十个字符',
        teachingReformProjects: 5,
        honoraryAwards: 3,
        teachingQuality: '测试教学质量内容，至少十个字符',
        studentGuidance: '测试学生指导内容，至少十个字符',
        scientificResearch: '测试科研工作内容，至少十个字符',
        teamBuilding: '测试团队建设内容，至少十个字符'
      }
    }

    // Set form data
    await wrapper.setProps({ initialData: formData })

    // Click save button
    const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
    await saveButton?.trigger('click')

    // Wait for validation and emit
    await wrapper.vm.$nextTick()

    // Check if save event was emitted
    expect(wrapper.emitted('save')).toBeTruthy()
  })

  it('shows preview dialog when preview button is clicked', async () => {
    const formData = {
      teachingOfficeId: 'test-office-001',
      evaluationYear: 2024,
      content: {
        teachingProcessManagement: '测试教学过程管理内容，至少十个字符',
        courseConstruction: '测试课程建设内容，至少十个字符',
        teachingReformProjects: 5,
        honoraryAwards: 3,
        teachingQuality: '测试教学质量内容，至少十个字符',
        studentGuidance: '测试学生指导内容，至少十个字符',
        scientificResearch: '测试科研工作内容，至少十个字符',
        teamBuilding: '测试团队建设内容，至少十个字符'
      }
    }

    const wrapper = mount(SelfEvaluationForm, {
      props: {
        ...defaultProps,
        initialData: formData
      }
    })

    // Click preview button
    const previewButton = wrapper.findAll('button').find(btn => btn.text() === '预览')
    await previewButton?.trigger('click')

    // Wait for dialog to open
    await wrapper.vm.$nextTick()

    // Check if preview event was emitted
    expect(wrapper.emitted('preview')).toBeTruthy()
  })

  it('supports teaching reform projects number input', () => {
    const wrapper = mount(SelfEvaluationForm, {
      props: defaultProps
    })

    // Find the teaching reform projects input
    expect(wrapper.text()).toContain('教学改革项目个数')
    expect(wrapper.text()).toContain('请填写本年度教学改革项目的总数量')
  })

  it('supports honorary awards number input', () => {
    const wrapper = mount(SelfEvaluationForm, {
      props: defaultProps
    })

    // Find the honorary awards input
    expect(wrapper.text()).toContain('荣誉表彰个数')
    expect(wrapper.text()).toContain('请填写本年度获得的荣誉表彰总数量')
  })

  describe('Form Validation', () => {
    it('validates required text fields', async () => {
      const wrapper = mount(SelfEvaluationForm, {
        props: defaultProps
      })

      // Try to save without filling required fields
      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message
      expect(ElMessage.error).toHaveBeenCalledWith('请检查表单填写是否完整')
    })

    it('validates minimum text length for text fields', async () => {
      const wrapper = mount(SelfEvaluationForm, {
        props: {
          ...defaultProps,
          initialData: {
            teachingOfficeId: 'test-office-001',
            evaluationYear: 2024,
            content: {
              teachingProcessManagement: '短文本', // Less than 10 characters
              courseConstruction: '测试课程建设内容，至少十个字符',
              teachingReformProjects: 5,
              honoraryAwards: 3,
              teachingQuality: '测试教学质量内容，至少十个字符',
              studentGuidance: '测试学生指导内容，至少十个字符',
              scientificResearch: '测试科研工作内容，至少十个字符',
              teamBuilding: '测试团队建设内容，至少十个字符'
            }
          }
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message due to validation failure
      expect(ElMessage.error).toHaveBeenCalledWith('请检查表单填写是否完整')
    })

    it('validates maximum text length for text fields', async () => {
      const longText = 'a'.repeat(1001) // More than 1000 characters

      const wrapper = mount(SelfEvaluationForm, {
        props: {
          ...defaultProps,
          initialData: {
            teachingOfficeId: 'test-office-001',
            evaluationYear: 2024,
            content: {
              teachingProcessManagement: longText,
              courseConstruction: '测试课程建设内容，至少十个字符',
              teachingReformProjects: 5,
              honoraryAwards: 3,
              teachingQuality: '测试教学质量内容，至少十个字符',
              studentGuidance: '测试学生指导内容，至少十个字符',
              scientificResearch: '测试科研工作内容，至少十个字符',
              teamBuilding: '测试团队建设内容，至少十个字符'
            }
          }
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message due to validation failure
      expect(ElMessage.error).toHaveBeenCalledWith('请检查表单填写是否完整')
    })

    it('rejects text fields with only whitespace', async () => {
      const wrapper = mount(SelfEvaluationForm, {
        props: {
          ...defaultProps,
          initialData: {
            teachingOfficeId: 'test-office-001',
            evaluationYear: 2024,
            content: {
              teachingProcessManagement: '            ', // Only whitespace
              courseConstruction: '测试课程建设内容，至少十个字符',
              teachingReformProjects: 5,
              honoraryAwards: 3,
              teachingQuality: '测试教学质量内容，至少十个字符',
              studentGuidance: '测试学生指导内容，至少十个字符',
              scientificResearch: '测试科研工作内容，至少十个字符',
              teamBuilding: '测试团队建设内容，至少十个字符'
            }
          }
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message due to validation failure
      expect(ElMessage.error).toHaveBeenCalledWith('请检查表单填写是否完整')
    })

    it('validates number fields are non-negative', async () => {
      const wrapper = mount(SelfEvaluationForm, {
        props: {
          ...defaultProps,
          initialData: {
            teachingOfficeId: 'test-office-001',
            evaluationYear: 2024,
            content: {
              teachingProcessManagement: '测试教学过程管理内容，至少十个字符',
              courseConstruction: '测试课程建设内容，至少十个字符',
              teachingReformProjects: -1, // Negative number
              honoraryAwards: 3,
              teachingQuality: '测试教学质量内容，至少十个字符',
              studentGuidance: '测试学生指导内容，至少十个字符',
              scientificResearch: '测试科研工作内容，至少十个字符',
              teamBuilding: '测试团队建设内容，至少十个字符'
            }
          }
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message due to validation failure
      expect(ElMessage.error).toHaveBeenCalledWith('请检查表单填写是否完整')
    })

    it('validates number fields do not exceed maximum', async () => {
      const wrapper = mount(SelfEvaluationForm, {
        props: {
          ...defaultProps,
          initialData: {
            teachingOfficeId: 'test-office-001',
            evaluationYear: 2024,
            content: {
              teachingProcessManagement: '测试教学过程管理内容，至少十个字符',
              courseConstruction: '测试课程建设内容，至少十个字符',
              teachingReformProjects: 101, // Exceeds maximum of 100
              honoraryAwards: 3,
              teachingQuality: '测试教学质量内容，至少十个字符',
              studentGuidance: '测试学生指导内容，至少十个字符',
              scientificResearch: '测试科研工作内容，至少十个字符',
              teamBuilding: '测试团队建设内容，至少十个字符'
            }
          }
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message due to validation failure
      expect(ElMessage.error).toHaveBeenCalledWith('请检查表单填写是否完整')
    })

    it('validates number fields are integers', async () => {
      const wrapper = mount(SelfEvaluationForm, {
        props: {
          ...defaultProps,
          initialData: {
            teachingOfficeId: 'test-office-001',
            evaluationYear: 2024,
            content: {
              teachingProcessManagement: '测试教学过程管理内容，至少十个字符',
              courseConstruction: '测试课程建设内容，至少十个字符',
              teachingReformProjects: 5.5, // Not an integer
              honoraryAwards: 3,
              teachingQuality: '测试教学质量内容，至少十个字符',
              studentGuidance: '测试学生指导内容，至少十个字符',
              scientificResearch: '测试科研工作内容，至少十个字符',
              teamBuilding: '测试团队建设内容，至少十个字符'
            }
          }
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show error message due to validation failure
      expect(ElMessage.error).toHaveBeenCalledWith('请检查表单填写是否完整')
    })

    it('accepts valid form data', async () => {
      const validData = {
        teachingOfficeId: 'test-office-001',
        evaluationYear: 2024,
        content: {
          teachingProcessManagement: '测试教学过程管理内容，至少十个字符',
          courseConstruction: '测试课程建设内容，至少十个字符',
          teachingReformProjects: 5,
          honoraryAwards: 3,
          teachingQuality: '测试教学质量内容，至少十个字符',
          studentGuidance: '测试学生指导内容，至少十个字符',
          scientificResearch: '测试科研工作内容，至少十个字符',
          teamBuilding: '测试团队建设内容，至少十个字符'
        }
      }

      const wrapper = mount(SelfEvaluationForm, {
        props: {
          ...defaultProps,
          initialData: validData
        }
      })

      const saveButton = wrapper.findAll('button').find(btn => btn.text() === '保存')
      await saveButton?.trigger('click')
      await wrapper.vm.$nextTick()

      // Should show success message
      expect(ElMessage.success).toHaveBeenCalledWith('保存成功')
      // Should emit save event
      expect(wrapper.emitted('save')).toBeTruthy()
    })
  })
})
