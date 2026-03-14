<template>
  <div class="scoring-rules-page">
    <div class="page-header">
      <h1>评分规则</h1>
      <p class="page-description">
        教研室工作考核评分标准与规则说明（依据《教研室工作考核评分表》）。
        <router-link to="/management-home" class="back-home-link">← 返回评教小组端首页</router-link>
      </p>
    </div>

    <el-card class="rules-card">
      <div class="rules-content">
        <h2>教研室工作考核评分表</h2>
        <p class="intro">被考核教研室：由各教研室填写自评表，以下为考核指标、观测点与得分说明。</p>

        <el-table :data="regularTeachingRows" border stripe class="rules-table">
          <el-table-column prop="category" label="类别" width="120" />
          <el-table-column prop="indicator" label="考核指标" width="140" />
          <el-table-column prop="observation" label="观测点" min-width="320" />
          <el-table-column prop="fullScore" label="满分" width="80" />
          <el-table-column prop="scoreNote" label="得分点" width="120" />
        </el-table>

        <h3>特色与亮点项目</h3>
        <el-table :data="highlightRows" border stripe class="rules-table">
          <el-table-column prop="indicator" label="考核指标" width="200" />
          <el-table-column prop="observation" label="观测点/得分说明" min-width="400" />
        </el-table>

        <h3>负面清单</h3>
        <el-table :data="negativeRows" border stripe class="rules-table">
          <el-table-column prop="indicator" label="项目" width="200" />
          <el-table-column prop="observation" label="说明/扣分" min-width="400" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// 依据《教研室工作考核评分表 (2).md》整理
const regularTeachingRows = [
  { category: '常规教学工作', indicator: '教学过程管理', observation: '制定年度教研室工作计划，并采取有效措施保证计划落实，各个教学环节的正常运转。落实集体备课制度，按规定选用教材，完成指导毕业生的毕业实习、毕业论文（设计）及答辩工作。', fullScore: '', scoreNote: '' },
  { category: '', indicator: '教学质量管理', observation: '了解教研室成员教学基本情况，不断改进教学。组织教师相互听课学习，开展教学评议活动积极配合学校及教学院部开展教学检查工作。', fullScore: '', scoreNote: '' },
  { category: '', indicator: '课程考核', observation: '试题无错漏并符合规范，课程考核能有效检测课程教学目标达成度，能体现能力评价和形成性评价导向。阅卷规范，做好试题库建设。', fullScore: '', scoreNote: '' },
  { category: '', indicator: '教育教学科研工作', observation: '组织教师开展教学方法、教学内容、教学手段的探索与实践。做好各级教育教学改革、教学成果项目的申报与组织实施和推广应用工作。指导学生开展创新创业项目，课外科技活动以及有关的学科竞赛活动。', fullScore: '', scoreNote: '' },
  { category: '', indicator: '课程建设', observation: '每门课程配备主讲教师，所有课程均有规范的教学大纲、教案和课件，课程定位准确，目标清晰合理，教学内容安排合理，能够有机融入课程思政元素，体现以学生发展为中心，能有效支撑课程目标。', fullScore: '', scoreNote: '' },
  { category: '', indicator: '教师队伍建设', observation: '制订有教师培养规划，有计划地安排青年教师的教学、教研和进修深造工作。', fullScore: '', scoreNote: '' },
  { category: '', indicator: '科学研究与学术交流', observation: '承担有科研项目，开展有计划、有组织的社会服务活动，参与校内外、国内外的学术交流活动，为学生举办学术讲座。', fullScore: '', scoreNote: '' },
  { category: '', indicator: '教学档案室管理与建设', observation: '各类教学档案齐全，教学管理档案归档及时。', fullScore: '', scoreNote: '' }
]

const highlightRows = [
  { indicator: '教学改革项目', observation: '教研室成员年度有新增教改项目立项（国家级重点项目10分、一般项目8分；自治区级本科教改重点项目6分，一般项目A类4分，一般项目B类2分，自治区级职业教改项目重点6分，一般3分；校级重点项目2分，一般项目1分）。' },
  { indicator: '年度获得教学相关荣誉表彰', observation: '包括但不限于以下荣誉：优秀教师、优秀辅导员、教学名师、教学新秀、教学能手等（国家级10分，省部级5分，市厅（校）级3分）。' },
  { indicator: '教学比赛', observation: '在厅（校）级以上各类教学比赛中获奖（国家级一等奖10分、二等奖8分，三等奖6分；省部级一等奖6分、二等奖5分、三等奖3分；市厅（校）级一等奖3、二等奖2分、三等奖1分）。' },
  { indicator: '指导创新创业比赛获奖情况', observation: '国家级金奖10分、银奖8分、铜奖6分、省部级金奖6分、银奖5分，铜奖3分，市厅（校）级一等奖3、二等奖2分、三等奖1分。' }
]

const negativeRows = [
  { indicator: '教师中有严重违反师德师风的行为，造成恶劣社会影响', observation: '每人/次减10分。' },
  { indicator: '出现教学（管理）事故', observation: '严重教学（管理）事故每人/次减5分。' },
  { indicator: '教学过程中出现意识形态问题', observation: '从事传教活动；传播错误思想观点；发表同中央精神相违背的言论；非议党的理论和路线方针政策及重大决策部署；散布传播政治谣言等等。每人/次减5分。' },
  { indicator: '教师未完成年度基本教学工作量', observation: '专任教师中未完成年度教学基本工作量人数占比超过10%的减2分，超20%的减5分，超30%减10分。' }
]
</script>

<style scoped>
.scoring-rules-page { min-height: 100vh; background: #f5f7fa; padding: 20px; }
.page-header { margin-bottom: 20px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.page-header h1 { margin: 0 0 8px 0; font-size: 24px; color: #303133; }
.page-description { margin: 0; color: #606266; font-size: 14px; }
.back-home-link { margin-left: 12px; color: #409eff; text-decoration: none; }
.back-home-link:hover { text-decoration: underline; }
.rules-card { max-width: 1100px; margin: 0 auto; }
.rules-content h2 { margin: 0 0 16px 0; font-size: 18px; color: #303133; }
.rules-content h3 { margin: 24px 0 12px 0; font-size: 16px; color: #409eff; }
.intro { margin: 0 0 16px 0; color: #606266; font-size: 14px; }
.rules-table { margin-bottom: 20px; }
</style>
