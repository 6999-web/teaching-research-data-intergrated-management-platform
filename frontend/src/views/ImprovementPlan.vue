<template>
  <div class="improvement-plan">
    <PageHeader 
      title="整改措施填报" 
      subtitle="针对考评失分项制定改进计划" 
      :showBack="true"
    />
    
    <div v-if="loading" class="loading-state">
      <el-spin />
    </div>

    <el-card v-else>
      <template #header>
        <div class="card-header">
          <span>待整改列表</span>
          <el-button type="primary" @click="dialogVisible = true">新增整改计划</el-button>
        </div>
      </template>

      <el-table :data="plans" style="width: 100%">
        <el-table-column prop="indicator_item_id" label="指标项ID" width="100" />
        <el-table-column prop="target" label="整改目标" />
        <el-table-column prop="measures" label="措施" />
        <el-table-column prop="deadline" label="截止日期">
            <template #default="scope">
                {{ new Date(scope.row.deadline).toLocaleDateString() }}
            </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag>{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
           <template #default="scope">
             <el-button size="small" @click="editPlan(scope.row)">编辑</el-button>
           </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Dialog for Create/Edit -->
    <el-dialog v-model="dialogVisible" title="整改计划详情">
      <el-form :model="form" label-width="100px">
        <el-form-item label="指标项ID">
          <el-input-number v-model="form.indicator_item_id" />
        </el-form-item>
        <el-form-item label="整改目标">
          <el-input v-model="form.target" type="textarea" />
        </el-form-item>
        <el-form-item label="具体措施">
           <el-input v-model="form.measures" type="textarea" />
        </el-form-item>
        <el-form-item label="截止日期">
            <el-date-picker v-model="form.deadline" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPlan">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import { improvementApi, type ImprovementPlan, type ImprovementPlanCreate } from '@/api/improvement'
import { ElMessage } from 'element-plus'

const route = useRoute()
const evaluationId = route.params.id as string

const loading = ref(true)
const plans = ref<ImprovementPlan[]>([])
const dialogVisible = ref(false)

const form = ref<ImprovementPlanCreate>({
    evaluation_id: evaluationId,
    indicator_item_id: 1,
    target: '',
    measures: '',
    charger_id: '', // Should be current user or selected user
    deadline: ''
})

const loadPlans = async () => {
    loading.value = true
    try {
        const res = await improvementApi.getByEvaluation(evaluationId)
        plans.value = res.data
    } catch (e) {
        ElMessage.error('加载失败')
    } finally {
        loading.value = false
    }
}

const submitPlan = async () => {
    try {
        // Mock charger_id for now
        form.value.charger_id = '00000000-0000-0000-0000-000000000000' 
        form.value.evaluation_id = evaluationId
        
        await improvementApi.create(form.value)
        ElMessage.success('提交成功')
        dialogVisible.value = false
        loadPlans()
    } catch (e) {
        ElMessage.error('提交失败')
    }
}

const editPlan = (plan: ImprovementPlan) => {
    // Fill form and open dialog (Simplified for create only in this demo)
    ElMessage.info('编辑功能暂未开放')
}

onMounted(() => {
    if (evaluationId) {
        loadPlans()
    }
})
</script>
