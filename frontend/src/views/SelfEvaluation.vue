<template>
  <div class="self-evaluation-page">
    <PageHeader 
      title="教研室工作自评" 
      :breadcrumbs="[
        { label: '教研室端' },
        { label: '自评表填写' }
      ]"
    />

    <SelfEvaluationForm
      :teaching-office-id="teachingOfficeId"
      :evaluation-year="evaluationYear"
      :initial-data="initialData"
      @save="handleSave"
      @preview="handlePreview"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import SelfEvaluationForm from '@/components/SelfEvaluationForm.vue'
import type { SelfEvaluationFormData } from '@/types/selfEvaluation'

// Mock data - in real app, this would come from authentication/API
const teachingOfficeId = ref('teaching-office-001')
const evaluationYear = ref(new Date().getFullYear())
const initialData = ref<SelfEvaluationFormData | undefined>(undefined)

// Load existing data if available
onMounted(async () => {
  try {
    // TODO: Load existing self-evaluation data from API
    // const response = await api.getSelfEvaluation(teachingOfficeId.value, evaluationYear.value)
    // initialData.value = response.data
  } catch (error) {
    console.error('Failed to load self-evaluation data:', error)
  }
})

// Handle save
const handleSave = async (data: SelfEvaluationFormData) => {
  try {
    // TODO: Call API to save self-evaluation
    // await api.saveSelfEvaluation(data)
    console.log('Saving self-evaluation:', data)
    ElMessage.success('自评表保存成功')
  } catch (error) {
    console.error('Failed to save self-evaluation:', error)
    ElMessage.error('保存失败，请重试')
  }
}

// Handle preview
const handlePreview = (data: SelfEvaluationFormData) => {
  console.log('Previewing self-evaluation:', data)
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
