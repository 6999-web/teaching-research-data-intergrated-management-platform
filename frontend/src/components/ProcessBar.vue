<template>
  <div class="process-bar">
    <div 
      v-for="(step, index) in steps" 
      :key="index"
      class="process-step"
      :class="{
        'active': currentStep === index + 1,
        'completed': currentStep > index + 1,
        'highlight': highlightSteps.includes(index + 1),
        'current-role': isCurrentRoleStep(index + 1)
      }"
    >
      <div class="step-circle">
        <span v-if="currentStep > index + 1" class="check-icon">✓</span>
        <span v-else class="step-number">{{ index + 1 }}</span>
      </div>
      <div class="step-label">{{ step.label }}</div>
      <div class="step-line" v-if="index < steps.length - 1"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Step {
  label: string
  roleSteps: string[]
}

const props = defineProps<{
  currentStep?: number
  userRole: 'director' | 'college_leader' | 'evaluation_team' | 'evaluation_office' | 'president_office'
}>()

const steps: Step[] = [
  { label: '自评填报', roleSteps: ['director'] },
  { label: '材料上传', roleSteps: ['director'] },
  { label: 'AI评分', roleSteps: ['evaluation_team'] },
  { label: '手动评分', roleSteps: ['evaluation_team'] },
  { label: '最终得分', roleSteps: ['evaluation_team'] },
  { label: '数据审定', roleSteps: ['evaluation_office'] },
  { label: '结果公示', roleSteps: ['evaluation_office'] },
  { label: '改进闭环', roleSteps: ['director', 'college_leader'] }
]

const highlightSteps = computed(() => {
  return steps
    .map((step, index) => step.roleSteps.includes(props.userRole) ? index + 1 : null)
    .filter(step => step !== null) as number[]
})

const isCurrentRoleStep = (stepNumber: number) => {
  return highlightSteps.value.includes(stepNumber)
}
</script>

<style scoped>
.process-bar {
  display: flex;
  justify-content: space-between;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.process-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 0.5rem;
  transition: all 0.3s;
  z-index: 2;
}

.process-step.completed .step-circle {
  background: #7cb342;
  color: white;
}

.process-step.active .step-circle {
  background: #2c4a6d;
  color: white;
  box-shadow: 0 0 0 4px rgba(44, 74, 109, 0.2);
}

.process-step.highlight .step-circle {
  border: 3px solid #ff9800;
}

.process-step.current-role.active .step-circle {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 4px rgba(44, 74, 109, 0.2);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(44, 74, 109, 0.1);
  }
}

.step-label {
  font-size: 0.9rem;
  color: #666;
  text-align: center;
}

.process-step.active .step-label {
  color: #2c4a6d;
  font-weight: 600;
}

.step-line {
  position: absolute;
  top: 20px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e0e0e0;
  z-index: 1;
}

.process-step.completed .step-line {
  background: #7cb342;
}

@media (max-width: 768px) {
  .process-bar {
    flex-direction: column;
    padding: 1rem;
  }
  
  .step-line {
    display: none;
  }
  
  .process-step {
    flex-direction: row;
    justify-content: flex-start;
    margin-bottom: 1rem;
  }
  
  .step-circle {
    margin-right: 1rem;
    margin-bottom: 0;
  }
}
</style>
