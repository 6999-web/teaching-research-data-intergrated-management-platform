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
const handleSubmit = async (formData: any) => {
  try {
    ElMessage.loading('正在提交自评表，请稍候...')
    
    // 一次性完成所有操作：保存 → 提交 → 锁定 → AI评分
    // Step 1: Save self-evaluation
    const saveResponse = await selfEvaluationApi.save({
      teaching_office_id: teachingOfficeId.value,
      evaluation_year: evaluationYear.value,
      content: formData
    })

    const evaluationId = saveResponse.data.evaluation_id

    // Step 2: Submit and lock (自动锁定，状态变为locked)
    await selfEvaluationApi.submit(evaluationId)

    // Step 3: Automatically trigger AI scoring (自动触发AI评分，状态变为ai_scored)
    try {
      await selfEvaluationApi.triggerAIScoring(evaluationId)
    } catch (aiError) {
      console.warn('AI评分触发失败，但不影响提交:', aiError)
      // AI评分失败不影响提交结果，继续执行
    }

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
