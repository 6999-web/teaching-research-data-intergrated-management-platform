<template>
  <div class="attachment-upload-view">
    <AttachmentUpload
      :evaluation-id="evaluationId"
      :evaluation-year="evaluationYear"
      :is-locked="isLocked"
      :initial-attachments="attachments"
      @submit="handleSubmit"
      @back="handleBack"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AttachmentUpload from '@/components/AttachmentUpload.vue'
import type { Attachment } from '@/types/attachment'
import apiClient from '@/api/client'

const router = useRouter()
const route = useRoute()

// State
const evaluationId = ref<string>('')
const evaluationYear = ref<number>(new Date().getFullYear())
const isLocked = ref<boolean>(false)
const attachments = ref<Attachment[]>([])

// Load evaluation data
onMounted(async () => {
  // Get evaluation ID from route params or query
  evaluationId.value = (route.params.id as string) || (route.query.evaluationId as string) || ''
  
  if (!evaluationId.value) {
    ElMessage.error('缺少评估ID')
    router.push('/self-evaluation')
    return
  }

  try {
    // Fetch evaluation details to check lock status
    const evalResponse = await apiClient.get(`/teaching-office/self-evaluation/${evaluationId.value}`)
    const evaluation = evalResponse.data
    
    evaluationYear.value = evaluation.evaluationYear
    isLocked.value = evaluation.status === 'submitted'

    // Fetch existing attachments
    const attachmentsResponse = await apiClient.get(`/teaching-office/attachments`, {
      params: { evaluationId: evaluationId.value }
    })
    attachments.value = attachmentsResponse.data || []
  } catch (error) {
    console.error('Failed to load evaluation data:', error)
    ElMessage.error('加载数据失败')
  }
})

// Handle submit
const handleSubmit = async () => {
  try {
    // Call API to submit attachments
    await apiClient.post(`/teaching-office/self-evaluation/${evaluationId.value}/submit`)
    
    ElMessage.success('提交成功')
    
    // Navigate back to self-evaluation page
    setTimeout(() => {
      router.push('/self-evaluation')
    }, 1500)
  } catch (error) {
    console.error('Failed to submit attachments:', error)
    ElMessage.error('提交失败，请重试')
  }
}

// Handle back
const handleBack = () => {
  router.push('/self-evaluation')
}
</script>

<style scoped>
.attachment-upload-view {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px 0;
}
</style>
