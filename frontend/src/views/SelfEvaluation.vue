<template>
  <div class="self-evaluation-page">
    <PageHeader 
      title="教研室工作自评" 
      :breadcrumbs="[
        { label: '教研室端' },
        { label: '自评表填写' }
      ]"
    />

    <NewSelfEvaluationForm
      :teaching-office-id="teachingOfficeId"
      :evaluation-year="evaluationYear"
      @submit="handleSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import NewSelfEvaluationForm from '@/components/NewSelfEvaluationForm.vue'
import { selfEvaluationApi } from '@/api/client'

const router = useRouter()

// Get teaching office ID from auth store or localStorage
const teachingOfficeId = ref(localStorage.getItem('teachingOfficeId') || 'teaching-office-001')
const evaluationYear = ref(new Date().getFullYear())

// Handle form submission
const handleSubmit = async (submitData: any) => {
  try {
    ElMessage.loading('正在提交自评表，请稍候...')
    
    // Extract form data and attachment upload function
    const { formData, attachments, uploadAttachments } = submitData
    
    // Step 1: Save self-evaluation
    const saveResponse = await selfEvaluationApi.save({
      teaching_office_id: teachingOfficeId.value,
      evaluation_year: evaluationYear.value,
      content: formData
    })

    const evaluationId = saveResponse.data.evaluation_id

    // Step 2: Upload attachments if any
    if (attachments && attachments.length > 0) {
      ElMessage.closeAll()
      ElMessage.loading('正在上传附件，请稍候...')
      
      const uploadSuccess = await uploadAttachments(evaluationId)
      if (!uploadSuccess) {
        ElMessage.closeAll()
        ElMessage.warning('附件上传失败，但表单已保存。您可以稍后单独上传附件。')
        // Continue with submission even if attachment upload fails
      }
    }

    // Step 3: Submit to evaluation team
    ElMessage.closeAll()
    ElMessage.loading('正在提交到考评小组，请稍候...')
    await selfEvaluationApi.submit(evaluationId)

    // 提交成功
    ElMessage.closeAll()
    ElMessage.success('提交成功！数据已上传到考评小组端')
    
    // 跳转到主页
    setTimeout(() => {
      router.push('/teaching-office-home')
    }, 1500)

  } catch (error: any) {
    ElMessage.closeAll()
    console.error('Failed to submit self-evaluation:', error)
    
    // 更详细的错误提示
    if (error.response?.status === 401) {
      ElMessage.error('请先登录后再提交')
    } else if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else {
      ElMessage.error('提交失败，请检查网络连接或联系管理员')
    }
  }
}
</script>

<style scoped>
.self-evaluation-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #303133;
}
</style>
