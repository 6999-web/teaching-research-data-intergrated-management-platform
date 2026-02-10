<template>
  <div class="improvement-plan">
    <PageHeader 
      title="下学期改进措施" 
      subtitle="查看下个学期所有老师的改进措施" 
      :showBack="true"
    />
    
    <div v-if="loading" class="loading-state">
      <el-spin />
    </div>

    <el-card v-else class="plan-card">
      <template #header>
        <div class="card-header">
          <span class="header-title">所有老师的改进措施列表</span>
          <div class="header-info">
            <el-tag type="info">共 {{ plans.length }} 条改进措施</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="plans" style="width: 100%" stripe>
        <el-table-column prop="teacher_name" label="教师姓名" width="120" />
        <el-table-column prop="indicator_item_id" label="考核指标" width="140">
          <template #default="scope">
            {{ getIndicatorName(scope.row.indicator_item_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="weakness_analysis" label="薄弱项分析" width="200" show-overflow-tooltip />
        <el-table-column prop="target" label="改进目标" width="180" show-overflow-tooltip />
        <el-table-column prop="measures" label="具体措施" width="200" show-overflow-tooltip />
        <el-table-column prop="expected_effect" label="预期效果" width="150" show-overflow-tooltip />
        <el-table-column prop="charger_id" label="责任人" width="100" />
        <el-table-column prop="deadline" label="完成时限" width="120">
            <template #default="scope">
                {{ formatDate(scope.row.deadline) }}
            </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
           <template #default="scope">
             <el-button size="small" type="primary" link @click="viewPlan(scope.row)">
               <el-icon><View /></el-icon>
               查看详情
             </el-button>
           </template>
        </el-table-column>
      </el-table>

      <div v-if="plans.length === 0" class="empty-state">
        <el-empty description="暂无改进措施记录" />
      </div>
    </el-card>

    <!-- View Dialog -->
    <el-dialog 
      v-model="viewDialogVisible" 
      title="改进措施详情"
      width="60%"
    >
      <div v-if="currentPlan" class="plan-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="教师姓名">
            {{ currentPlan.teacher_name }}
          </el-descriptions-item>
          <el-descriptions-item label="考核指标">
            {{ getIndicatorName(currentPlan.indicator_item_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentPlan.status)">
              {{ getStatusText(currentPlan.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="责任人">
            {{ currentPlan.charger_id }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时限" :span="2">
            {{ formatDate(currentPlan.deadline) }}
          </el-descriptions-item>
          <el-descriptions-item label="薄弱项分析" :span="2">
            {{ currentPlan.weakness_analysis }}
          </el-descriptions-item>
          <el-descriptions-item label="改进目标" :span="2">
            {{ currentPlan.target }}
          </el-descriptions-item>
          <el-descriptions-item label="具体措施" :span="2">
            {{ currentPlan.measures }}
          </el-descriptions-item>
          <el-descriptions-item label="预期效果" :span="2">
            {{ currentPlan.expected_effect }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { improvementApi, type ImprovementPlan } from '@/api/improvement'

const route = useRoute()
const evaluationId = route.params.id as string

const loading = ref(true)
const plans = ref<ImprovementPlan[]>([])
const viewDialogVisible = ref(false)
const currentPlan = ref<ImprovementPlan | null>(null)

// Mock data for demonstration - 模拟下学期所有老师的改进措施
const mockPlans: ImprovementPlan[] = [
  {
    id: '1',
    evaluation_id: evaluationId,
    teacher_name: '张三',
    indicator_item_id: 1,
    weakness_analysis: '教学过程管理方面存在课堂纪律管理不够严格的问题，部分学生上课玩手机现象较为普遍，影响了课堂教学效果。',
    target: '下学期将课堂纪律管理纳入日常教学考核，确保课堂秩序良好，学生专注度提升20%以上。',
    measures: '1. 制定明确的课堂纪律规范并在第一节课宣讲；2. 采用课堂互动教学法提高学生参与度；3. 建立课堂表现记录制度；4. 定期与学生沟通反馈。',
    expected_effect: '预计课堂纪律明显改善，学生专注度和学习效果显著提升，期末考试平均分提高5分以上。',
    charger_id: '张三',
    deadline: '2026-06-30',
    status: 'in_progress',
    created_at: '2026-02-10',
    updated_at: '2026-02-10'
  },
  {
    id: '2',
    evaluation_id: evaluationId,
    teacher_name: '李四',
    indicator_item_id: 2,
    weakness_analysis: '课程建设方面，教学资源更新不及时，部分课件内容陈旧，缺少最新的行业案例和技术发展动态。',
    target: '下学期完成课程资源全面更新，引入至少10个最新行业案例，确保教学内容与行业发展同步。',
    measures: '1. 每月关注行业最新动态和技术发展；2. 与企业建立合作关系获取一手案例；3. 重新制作核心章节课件；4. 建立课程资源定期更新机制。',
    expected_effect: '课程内容更加贴近行业实际，学生学习兴趣和就业竞争力明显提升。',
    charger_id: '李四',
    deadline: '2026-07-15',
    status: 'pending',
    created_at: '2026-02-10',
    updated_at: '2026-02-10'
  },
  {
    id: '3',
    evaluation_id: evaluationId,
    teacher_name: '王五',
    indicator_item_id: 3,
    weakness_analysis: '教学改革项目申报数量不足，缺乏对教学改革的系统性研究和实践探索。',
    target: '下学期至少申报2项校级教学改革项目，并完成1项项目的中期研究工作。',
    measures: '1. 组建教学改革研究小组；2. 定期开展教学研讨会；3. 学习借鉴其他院校成功经验；4. 积极参加教学改革培训。',
    expected_effect: '教学改革意识和能力显著提升，形成可推广的教学改革成果。',
    charger_id: '王五',
    deadline: '2026-08-30',
    status: 'pending',
    created_at: '2026-02-10',
    updated_at: '2026-02-10'
  },
  {
    id: '4',
    evaluation_id: evaluationId,
    teacher_name: '赵六',
    indicator_item_id: 5,
    weakness_analysis: '教学质量方面，学生评教分数偏低，主要反映在教学方法单一、师生互动不足等问题。',
    target: '下学期学生评教分数提升至90分以上，课堂互动频次增加50%。',
    measures: '1. 学习并应用多种教学方法；2. 增加课堂讨论和小组活动；3. 建立课后答疑机制；4. 定期收集学生反馈并改进。',
    expected_effect: '教学质量明显提升，学生满意度大幅提高，形成良好的师生互动氛围。',
    charger_id: '赵六',
    deadline: '2026-06-30',
    status: 'in_progress',
    created_at: '2026-02-10',
    updated_at: '2026-02-10'
  },
  {
    id: '5',
    evaluation_id: evaluationId,
    teacher_name: '孙七',
    indicator_item_id: 7,
    weakness_analysis: '科研工作方面，论文发表数量较少，科研成果转化率低，缺乏高水平科研项目支撑。',
    target: '下学期完成2篇核心期刊论文投稿，申报1项省级科研项目。',
    measures: '1. 制定详细的科研计划；2. 加强与科研团队的合作；3. 参加学术会议拓展视野；4. 每周安排固定时间进行科研工作。',
    expected_effect: '科研能力和水平显著提升，形成稳定的科研产出机制。',
    charger_id: '孙七',
    deadline: '2026-08-31',
    status: 'pending',
    created_at: '2026-02-10',
    updated_at: '2026-02-10'
  }
]

const loadPlans = async () => {
    loading.value = true
    try {
        // 使用模拟数据
        await new Promise(resolve => setTimeout(resolve, 500))
        plans.value = mockPlans
        
        // 如果需要从API加载，取消下面的注释
        // const res = await improvementApi.getByEvaluation(evaluationId)
        // plans.value = res.data
    } catch (e) {
        ElMessage.error('加载失败')
    } finally {
        loading.value = false
    }
}

const viewPlan = (plan: ImprovementPlan) => {
    currentPlan.value = plan
    viewDialogVisible.value = true
}

const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getStatusType = (status: string) => {
    const typeMap: Record<string, any> = {
        'pending': 'info',
        'in_progress': 'warning',
        'completed': 'success',
        'rejected': 'danger'
    }
    return typeMap[status] || 'info'
}

const getStatusText = (status: string) => {
    const textMap: Record<string, string> = {
        'pending': '待执行',
        'in_progress': '执行中',
        'completed': '已完成',
        'rejected': '已驳回'
    }
    return textMap[status] || status
}

const getIndicatorName = (id: number) => {
    const nameMap: Record<number, string> = {
        1: '教学过程管理',
        2: '课程建设',
        3: '教学改革项目',
        4: '荣誉表彰',
        5: '教学质量',
        6: '学生指导',
        7: '科研工作',
        8: '团队建设'
    }
    return nameMap[id] || `指标${id}`
}

onMounted(() => {
    loadPlans()
})
</script>


<style scoped>
.improvement-plan {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.plan-card {
  margin-top: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.empty-state {
  padding: 40px 0;
}

.field-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.field-hint .el-icon {
  font-size: 14px;
}

.plan-detail {
  padding: 20px 0;
}

:deep(.el-divider__text) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1a237e;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}
</style>
