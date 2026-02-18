<template>
  <div class="new-self-evaluation-form">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h2>教研室工作考核评分表</h2>
          <span class="evaluation-year">{{ formData.evaluationYear }}年度</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="200px"
        label-position="left"
        class="evaluation-form"
      >
        <!-- 一、常规教学工作 -->
        <el-divider content-position="left">
          <h3 class="section-title">一、常规教学工作</h3>
        </el-divider>

        <!-- 1. 教学过程管理 -->
        <el-form-item
          label="1. 教学过程管理"
          prop="regularTeaching.teachingProcessManagement.content"
        >
          <el-input
            v-model="formData.regularTeaching.teachingProcessManagement.content"
            type="textarea"
            :rows="4"
            placeholder="制定年度教研室工作计划，并采取有效措施保证计划落实，各个教学环节的正常运转。落实集体备课制度，按规定选用教材，完成指导毕业生的毕业实习、毕业论文（设计）及答辩工作。"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.teachingProcessManagement.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 2. 教学质量管理 -->
        <el-form-item
          label="2. 教学质量管理"
          prop="regularTeaching.teachingQualityManagement.content"
        >
          <el-input
            v-model="formData.regularTeaching.teachingQualityManagement.content"
            type="textarea"
            :rows="4"
            placeholder="了解教研室成员教学基本情况，不断改进教学。组织教师相互听课学习，开展教学评议活动积极配合学校及教学院部开展教学检查工作。"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.teachingQualityManagement.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 3. 课程考核 -->
        <el-form-item
          label="3. 课程考核"
          prop="regularTeaching.courseAssessment.content"
        >
          <el-input
            v-model="formData.regularTeaching.courseAssessment.content"
            type="textarea"
            :rows="4"
            placeholder="试题无错漏并符合规范，课程考核能有效检测课程教学目标达成度，能体现能力评价和形成性评价导向。阅卷规范，做好试题库建设。"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.courseAssessment.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 4. 教育教学科研工作 -->
        <el-form-item
          label="4. 教育教学科研工作"
          prop="regularTeaching.educationResearch.content"
        >
          <el-input
            v-model="formData.regularTeaching.educationResearch.content"
            type="textarea"
            :rows="4"
            placeholder="组织教师开展教学方法、教学内容、教学手段的探索与实践。做好各级教育教学改革、教学成果项目的申报与组织实施和推广应用工作。指导学生开展创新创业项目，课外科技活动以及有关的学科竞赛活动。"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.educationResearch.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 5. 课程建设 -->
        <el-form-item
          label="5. 课程建设"
          prop="regularTeaching.courseConstruction.content"
        >
          <el-input
            v-model="formData.regularTeaching.courseConstruction.content"
            type="textarea"
            :rows="4"
            placeholder="每门课程配备主讲教师，所有课程均有规范的教学大纲、教案和课件，课程定位准确，目标清晰合理，教学内容安排合理，能够有机融入课程思政元素，体现以学生发展为中心，能有效支撑课程目标。"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.courseConstruction.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 6. 教师队伍建设 -->
        <el-form-item
          label="6. 教师队伍建设"
          prop="regularTeaching.teacherTeamBuilding.content"
        >
          <el-input
            v-model="formData.regularTeaching.teacherTeamBuilding.content"
            type="textarea"
            :rows="4"
            placeholder="制订有教师培养规划，有计划地安排青年教师的教学、教研和进修深造工作"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.teacherTeamBuilding.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 7. 科学研究与学术交流 -->
        <el-form-item
          label="7. 科学研究与学术交流"
          prop="regularTeaching.researchAndExchange.content"
        >
          <el-input
            v-model="formData.regularTeaching.researchAndExchange.content"
            type="textarea"
            :rows="4"
            placeholder="承担有科研项目，开展有计划、有组织的社会服务活动，参与校内外、国内外的学术交流活动，为学生举办学术讲座。"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.researchAndExchange.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 8. 教学档案室管理与建设 -->
        <el-form-item
          label="8. 教学档案室管理与建设"
          prop="regularTeaching.archiveManagement.content"
        >
          <el-input
            v-model="formData.regularTeaching.archiveManagement.content"
            type="textarea"
            :rows="4"
            placeholder="各类教学档案齐全，教学管理档案归档及时。"
            maxlength="1000"
            show-word-limit
          />
          <div class="score-input-row">
            <span class="score-label">自评分：</span>
            <el-input-number
              v-model="formData.regularTeaching.archiveManagement.selfScore"
              :min="0"
              :max="10"
              :step="0.5"
              :precision="1"
            />
            <span class="max-score">/ 10分</span>
          </div>
        </el-form-item>

        <!-- 常规教学工作小计 -->
        <div class="subtotal-row">
          <span class="subtotal-label">常规教学工作小计：</span>
          <span class="subtotal-value">{{ calculateRegularTeachingTotal() }}</span>
          <span class="subtotal-unit">分</span>
        </div>

        <!-- 二、特色与亮点项目 -->
        <el-divider content-position="left">
          <h3 class="section-title">二、特色与亮点项目</h3>
        </el-divider>

        <!-- 1. 教学改革项目 -->
        <div class="highlight-section">
          <h4 class="highlight-title">1. 教学改革项目</h4>
          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="scoring-rules-alert"
          >
            <template #title>
              <div class="scoring-rules">
                <strong>评分标准：</strong>
                <span>国家级重点10分/一般8分 | 省级重点6分/一般A类4分/一般B类2分 | 省级职教重点6分/一般3分 | 校级重点2分/一般1分</span>
              </div>
            </template>
          </el-alert>

          <el-button
            type="primary"
            icon="Plus"
            size="small"
            @click="addReformProject"
            style="margin: 10px 0;"
          >
            添加教改项目
          </el-button>

          <el-table
            :data="formData.highlights.teachingReformProjects.items"
            border
            style="margin-top: 10px;"
            v-if="formData.highlights.teachingReformProjects.items.length > 0"
          >
            <el-table-column label="序号" type="index" width="60" align="center" />
            <el-table-column label="项目名称" min-width="200">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="请输入项目名称" />
              </template>
            </el-table-column>
            <el-table-column label="项目级别" width="180">
              <template #default="{ row }">
                <el-select v-model="row.level" placeholder="请选择级别" @change="updateReformProjectScore(row)">
                  <el-option label="国家级重点" value="national_key" />
                  <el-option label="国家级一般" value="national_general" />
                  <el-option label="省级重点" value="provincial_key" />
                  <el-option label="省级一般A类" value="provincial_general_a" />
                  <el-option label="省级一般B类" value="provincial_general_b" />
                  <el-option label="省级职教重点" value="provincial_vocational_key" />
                  <el-option label="省级职教一般" value="provincial_vocational_general" />
                  <el-option label="校级重点" value="school_key" />
                  <el-option label="校级一般" value="school_general" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="得分" width="80" align="center">
              <template #default="{ row }">
                <span class="score-value">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  size="small"
                  @click="removeReformProject($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="item-total">
            教学改革项目总分：<span class="total-value">{{ calculateReformProjectsTotal() }}</span> 分
          </div>
        </div>

        <!-- 2. 年度获得教学相关荣誉表彰 -->
        <div class="highlight-section">
          <h4 class="highlight-title">2. 年度获得教学相关荣誉表彰</h4>
          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="scoring-rules-alert"
          >
            <template #title>
              <div class="scoring-rules">
                <strong>评分标准：</strong>
                <span>国家级10分 | 省部级5分 | 市厅（校）级3分</span>
              </div>
            </template>
          </el-alert>

          <el-button
            type="primary"
            icon="Plus"
            size="small"
            @click="addHonor"
            style="margin: 10px 0;"
          >
            添加荣誉表彰
          </el-button>

          <el-table
            :data="formData.highlights.teachingHonors.items"
            border
            style="margin-top: 10px;"
            v-if="formData.highlights.teachingHonors.items.length > 0"
          >
            <el-table-column label="序号" type="index" width="60" align="center" />
            <el-table-column label="荣誉名称" min-width="200">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="请输入荣誉名称" />
              </template>
            </el-table-column>
            <el-table-column label="荣誉级别" width="150">
              <template #default="{ row }">
                <el-select v-model="row.level" placeholder="请选择级别" @change="updateHonorScore(row)">
                  <el-option label="国家级" value="national" />
                  <el-option label="省部级" value="provincial" />
                  <el-option label="市厅（校）级" value="school" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="得分" width="80" align="center">
              <template #default="{ row }">
                <span class="score-value">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  size="small"
                  @click="removeHonor($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="item-total">
            荣誉表彰总分：<span class="total-value">{{ calculateHonorsTotal() }}</span> 分
          </div>
        </div>

        <!-- 3. 教学比赛 -->
        <div class="highlight-section">
          <h4 class="highlight-title">3. 教学比赛</h4>
          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="scoring-rules-alert"
          >
            <template #title>
              <div class="scoring-rules">
                <strong>评分标准：</strong>
                <span>国家级一等奖10分/二等奖8分/三等奖6分 | 省部级一等奖6分/二等奖5分/三等奖3分 | 市厅（校）级一等奖3分/二等奖2分/三等奖1分</span>
              </div>
            </template>
          </el-alert>

          <el-button
            type="primary"
            icon="Plus"
            size="small"
            @click="addCompetition"
            style="margin: 10px 0;"
          >
            添加教学比赛
          </el-button>

          <el-table
            :data="formData.highlights.teachingCompetitions.items"
            border
            style="margin-top: 10px;"
            v-if="formData.highlights.teachingCompetitions.items.length > 0"
          >
            <el-table-column label="序号" type="index" width="60" align="center" />
            <el-table-column label="比赛名称" min-width="200">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="请输入比赛名称" />
              </template>
            </el-table-column>
            <el-table-column label="比赛级别和奖项" width="200">
              <template #default="{ row }">
                <el-select v-model="row.levelPrize" placeholder="请选择" @change="updateCompetitionScore(row)">
                  <el-option label="国家级一等奖" value="national_first" />
                  <el-option label="国家级二等奖" value="national_second" />
                  <el-option label="国家级三等奖" value="national_third" />
                  <el-option label="省部级一等奖" value="provincial_first" />
                  <el-option label="省部级二等奖" value="provincial_second" />
                  <el-option label="省部级三等奖" value="provincial_third" />
                  <el-option label="市厅（校）级一等奖" value="school_first" />
                  <el-option label="市厅（校）级二等奖" value="school_second" />
                  <el-option label="市厅（校）级三等奖" value="school_third" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="得分" width="80" align="center">
              <template #default="{ row }">
                <span class="score-value">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  size="small"
                  @click="removeCompetition($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="item-total">
            教学比赛总分：<span class="total-value">{{ calculateCompetitionsTotal() }}</span> 分
          </div>
        </div>

        <!-- 4. 指导创新创业比赛获奖情况 -->
        <div class="highlight-section">
          <h4 class="highlight-title">4. 指导创新创业比赛获奖情况</h4>
          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="scoring-rules-alert"
          >
            <template #title>
              <div class="scoring-rules">
                <strong>评分标准：</strong>
                <span>国家级金奖10分/银奖8分/铜奖6分 | 省部级金奖6分/银奖5分/铜奖3分 | 市厅（校）级一等奖3分/二等奖2分/三等奖1分</span>
              </div>
            </template>
          </el-alert>

          <el-button
            type="primary"
            icon="Plus"
            size="small"
            @click="addInnovation"
            style="margin: 10px 0;"
          >
            添加创新创业比赛
          </el-button>

          <el-table
            :data="formData.highlights.innovationCompetitions.items"
            border
            style="margin-top: 10px;"
            v-if="formData.highlights.innovationCompetitions.items.length > 0"
          >
            <el-table-column label="序号" type="index" width="60" align="center" />
            <el-table-column label="比赛名称" min-width="200">
              <template #default="{ row }">
                <el-input v-model="row.name" placeholder="请输入比赛名称" />
              </template>
            </el-table-column>
            <el-table-column label="比赛级别和奖项" width="200">
              <template #default="{ row }">
                <el-select v-model="row.levelPrize" placeholder="请选择" @change="updateInnovationScore(row)">
                  <el-option label="国家级金奖" value="national_gold" />
                  <el-option label="国家级银奖" value="national_silver" />
                  <el-option label="国家级铜奖" value="national_bronze" />
                  <el-option label="省部级金奖" value="provincial_gold" />
                  <el-option label="省部级银奖" value="provincial_silver" />
                  <el-option label="省部级铜奖" value="provincial_bronze" />
                  <el-option label="市厅（校）级一等奖" value="school_first" />
                  <el-option label="市厅（校）级二等奖" value="school_second" />
                  <el-option label="市厅（校）级三等奖" value="school_third" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="得分" width="80" align="center">
              <template #default="{ row }">
                <span class="score-value">{{ row.score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ $index }">
                <el-button
                  type="danger"
                  size="small"
                  @click="removeInnovation($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="item-total">
            创新创业比赛总分：<span class="total-value">{{ calculateInnovationsTotal() }}</span> 分
          </div>
        </div>

        <!-- 特色与亮点项目小计 -->
        <div class="subtotal-row highlights-subtotal">
          <span class="subtotal-label">特色与亮点项目小计：</span>
          <span class="subtotal-value">{{ calculateHighlightsTotal() }}</span>
          <span class="subtotal-unit">分</span>
        </div>

        <!-- 三、负面清单 -->
        <el-divider content-position="left">
          <h3 class="section-title negative-title">三、负面清单</h3>
        </el-divider>

        <el-alert
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 20px;"
        >
          以下情况将扣分，请如实填写
        </el-alert>

        <!-- 1. 师德师风违规 -->
        <div class="negative-item">
          <h4 class="negative-item-title">1. 教师中有严重违反师德师风的行为</h4>
          <p class="deduction-rule">造成恶劣社会影响，每人/次减10分</p>
          <div class="negative-input-row">
            <span>违规次数：</span>
            <el-input-number
              v-model="formData.negativeList.ethicsViolations.count"
              :min="0"
              :max="10"
              @change="updateEthicsDeduction"
            />
            <span style="margin-left: 10px;">起</span>
            <span class="deduction-display">扣分：<span class="deduction-value">{{ formData.negativeList.ethicsViolations.deduction }}</span> 分</span>
          </div>
        </div>

        <!-- 2. 教学事故 -->
        <div class="negative-item">
          <h4 class="negative-item-title">2. 出现教学（管理）事故</h4>
          <p class="deduction-rule">严重教学（管理）事故每人/次减5分</p>
          <div class="negative-input-row">
            <span>事故次数：</span>
            <el-input-number
              v-model="formData.negativeList.teachingAccidents.count"
              :min="0"
              :max="10"
              @change="updateAccidentsDeduction"
            />
            <span style="margin-left: 10px;">起</span>
            <span class="deduction-display">扣分：<span class="deduction-value">{{ formData.negativeList.teachingAccidents.deduction }}</span> 分</span>
          </div>
        </div>

        <!-- 3. 意识形态问题 -->
        <div class="negative-item">
          <h4 class="negative-item-title">3. 教学过程中出现意识形态问题</h4>
          <p class="deduction-rule">
            从事传教活动；传播错误思想观点；发表同中央精神相违背的言论；
            非议党的理论和路线方针政策及重大决策部署；散布传播政治谣言等等。每人/次减5分。
          </p>
          <div class="negative-input-row">
            <span>问题次数：</span>
            <el-input-number
              v-model="formData.negativeList.ideologyIssues.count"
              :min="0"
              :max="10"
              @change="updateIdeologyDeduction"
            />
            <span style="margin-left: 10px;">起</span>
            <span class="deduction-display">扣分：<span class="deduction-value">{{ formData.negativeList.ideologyIssues.deduction }}</span> 分</span>
          </div>
        </div>

        <!-- 4. 工作量未完成 -->
        <div class="negative-item">
          <h4 class="negative-item-title">4. 教师未完成年度基本教学工作量</h4>
          <p class="deduction-rule">
            专任教师中未完成年度教学基本工作量人数占比超过10%的减2分，超20%的减5分，超30%减10分。
          </p>
          <div class="negative-input-row">
            <span>未完成比例：</span>
            <el-input-number
              v-model="formData.negativeList.workloadIncomplete.percentage"
              :min="0"
              :max="100"
              :step="1"
              @change="updateWorkloadDeduction"
            />
            <span style="margin-left: 10px;">%</span>
            <span class="deduction-display">扣分：<span class="deduction-value">{{ formData.negativeList.workloadIncomplete.deduction }}</span> 分</span>
          </div>
        </div>

        <!-- 负面清单小计 -->
        <div class="subtotal-row negative-subtotal">
          <span class="subtotal-label">负面清单总扣分：</span>
          <span class="subtotal-value negative-value">{{ calculateNegativeTotal() }}</span>
          <span class="subtotal-unit">分</span>
        </div>

        <!-- 总分汇总 -->
        <el-divider content-position="left">
          <h3 class="section-title">评分汇总</h3>
        </el-divider>

        <el-card class="summary-card">
          <el-descriptions :column="2" border size="large">
            <el-descriptions-item label="常规教学工作总分" label-class-name="summary-label">
              <span class="summary-score">{{ calculateRegularTeachingTotal() }}</span> 分
            </el-descriptions-item>
            
            <el-descriptions-item label="特色与亮点项目总分" label-class-name="summary-label">
              <span class="summary-score">{{ calculateHighlightsTotal() }}</span> 分
            </el-descriptions-item>
            
            <el-descriptions-item label="负面清单扣分" label-class-name="summary-label">
              <span class="summary-score negative">-{{ calculateNegativeTotal() }}</span> 分
            </el-descriptions-item>
            
            <el-descriptions-item label="最终得分" label-class-name="summary-label">
              <span class="final-score">{{ calculateFinalScore() }}</span> 分
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 附件上传区域 -->
        <el-divider content-position="left">
          <h3 class="section-title">附件上传（可选）</h3>
        </el-divider>

        <el-card class="attachment-card">
          <el-alert
            title="提示"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            您可以在填写表单的同时上传相关附件。附件上传是可选的，也可以稍后单独上传。
          </el-alert>

          <el-form-item label="选择考核指标" required>
            <el-select
              v-model="attachmentForm.indicator"
              placeholder="请选择考核指标"
              style="width: 100%"
              @change="handleIndicatorChange"
            >
              <el-option
                v-for="indicator in attachmentIndicators"
                :key="indicator.key"
                :label="indicator.label"
                :value="indicator.key"
              >
                <span>{{ indicator.label }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">
                  {{ indicator.category === 'certificate' ? '证书类' : '项目类' }}
                </span>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="上传文件">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :multiple="true"
              :file-list="attachmentFileList"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :accept="acceptedFileTypes"
              :limit="10"
              :on-exceed="handleExceed"
              drag
              class="upload-component"
            >
              <el-icon class="el-icon--upload">
                <upload-filled />
              </el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击选择</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  <p v-if="attachmentForm.indicator" style="color: #409EFF; font-weight: 500;">
                    当前指标：{{ getIndicatorLabel(attachmentForm.indicator) }} | 支持格式：{{ currentIndicatorFileTypes }}
                  </p>
                  <p v-else class="warning-text">
                    ⚠️ 请先在上方选择考核指标，然后再上传文件
                  </p>
                  <p>支持多文件上传，单个文件不超过50MB，最多上传10个文件</p>
                  <p v-if="attachmentFileList.length > 0" style="color: #67C23A; font-weight: 500;">
                    ✓ 已选择 {{ attachmentFileList.length }} 个文件，提交表单时将自动上传
                  </p>
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <!-- 已选择的文件列表 -->
          <div v-if="attachmentFileList.length > 0" class="selected-files">
            <h4>已选择的文件（{{ attachmentFileList.length }}）</h4>
            <el-table :data="attachmentFileList" border stripe size="small">
              <el-table-column label="文件名" prop="name" />
              <el-table-column label="大小" width="120">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column label="考核指标" width="150">
                <template #default="{ row }">
                  {{ getIndicatorLabel(row.indicator) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row, $index }">
                  <el-button
                    type="danger"
                    size="small"
                    link
                    @click="removeFile($index)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- 操作按钮 -->
        <el-form-item class="form-actions">
          <el-button
            type="primary"
            size="large"
            :disabled="isSubmitted"
            :loading="isSubmitting"
            @click="handleSubmit"
          >
            {{ isSubmitted ? '已提交' : (attachmentFileList.length > 0 ? '提交表单并上传附件' : '提交表单') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadInstance, type UploadUserFile } from 'element-plus'
import type { IndicatorType } from '@/types/attachment'
import { INDICATORS } from '@/types/attachment'
import apiClient from '@/api/client'

// Props
interface Props {
  teachingOfficeId: string
  evaluationYear?: number
  evaluationId?: string
}

const props = withDefaults(defineProps<Props>(), {
  evaluationYear: () => new Date().getFullYear()
})

// Emits
const emit = defineEmits<{
  submit: [data: any]
}>()

// Form reference
const formRef = ref<FormInstance>()

// Upload reference
const uploadRef = ref<UploadInstance>()

// Attachment form data
const attachmentForm = reactive({
  indicator: '' as IndicatorType | ''
})

// Attachment state
const attachmentFileList = ref<UploadUserFile[]>([])
const isSubmitting = ref(false)

// Attachment indicators
const attachmentIndicators = INDICATORS

// Form data structure
const formData = reactive({
  teachingOfficeId: props.teachingOfficeId,
  evaluationYear: props.evaluationYear,
  regularTeaching: {
    teachingProcessManagement: {
      content: '',
      selfScore: 0,
      maxScore: 10
    },
    teachingQualityManagement: {
      content: '',
      selfScore: 0,
      maxScore: 10
    },
    courseAssessment: {
      content: '',
      selfScore: 0,
      maxScore: 10
    },
    educationResearch: {
      content: '',
      selfScore: 0,
      maxScore: 10
    },
    courseConstruction: {
      content: '',
      selfScore: 0,
      maxScore: 10
    },
    teacherTeamBuilding: {
      content: '',
      selfScore: 0,
      maxScore: 10
    },
    researchAndExchange: {
      content: '',
      selfScore: 0,
      maxScore: 10
    },
    archiveManagement: {
      content: '',
      selfScore: 0,
      maxScore: 10
    }
  },
  highlights: {
    teachingReformProjects: {
      items: [] as Array<{
        name: string
        level: string
        score: number
      }>,
      totalScore: 0
    },
    teachingHonors: {
      items: [] as Array<{
        name: string
        level: string
        score: number
      }>,
      totalScore: 0
    },
    teachingCompetitions: {
      items: [] as Array<{
        name: string
        levelPrize: string
        score: number
      }>,
      totalScore: 0
    },
    innovationCompetitions: {
      items: [] as Array<{
        name: string
        levelPrize: string
        score: number
      }>,
      totalScore: 0
    }
  },
  negativeList: {
    ethicsViolations: {
      count: 0,
      deduction: 0
    },
    teachingAccidents: {
      count: 0,
      deduction: 0
    },
    ideologyIssues: {
      count: 0,
      deduction: 0
    },
    workloadIncomplete: {
      percentage: 0,
      deduction: 0
    }
  }
})

// State
const isSubmitted = ref(false)

// Computed properties for attachment upload
const currentIndicatorFileTypes = computed(() => {
  if (!attachmentForm.indicator) return ''
  const indicator = attachmentIndicators.find(i => i.key === attachmentForm.indicator)
  return indicator ? indicator.fileTypes.join(', ') : ''
})

const acceptedFileTypes = computed(() => {
  if (!attachmentForm.indicator) return ''
  const indicator = attachmentIndicators.find(i => i.key === attachmentForm.indicator)
  if (!indicator) return ''
  return indicator.fileTypes.map(type => `.${type}`).join(',')
})

// Validation rules
const rules = reactive<FormRules>({
  'regularTeaching.teachingProcessManagement.content': [
    { required: true, message: '请填写教学过程管理内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ],
  'regularTeaching.teachingQualityManagement.content': [
    { required: true, message: '请填写教学质量管理内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ],
  'regularTeaching.courseAssessment.content': [
    { required: true, message: '请填写课程考核内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ],
  'regularTeaching.educationResearch.content': [
    { required: true, message: '请填写教育教学科研工作内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ],
  'regularTeaching.courseConstruction.content': [
    { required: true, message: '请填写课程建设内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ],
  'regularTeaching.teacherTeamBuilding.content': [
    { required: true, message: '请填写教师队伍建设内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ],
  'regularTeaching.researchAndExchange.content': [
    { required: true, message: '请填写科学研究与学术交流内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ],
  'regularTeaching.archiveManagement.content': [
    { required: true, message: '请填写教学档案室管理与建设内容', trigger: 'blur' },
    { min: 10, max: 1000, message: '内容长度应在10-1000个字符之间', trigger: 'blur' }
  ]
})

// Calculate regular teaching total score
const calculateRegularTeachingTotal = () => {
  const items = formData.regularTeaching
  return Object.values(items).reduce((total, item) => total + (item.selfScore || 0), 0)
}

// Scoring rules for reform projects
const reformProjectScoringRules: Record<string, number> = {
  national_key: 10,
  national_general: 8,
  provincial_key: 6,
  provincial_general_a: 4,
  provincial_general_b: 2,
  provincial_vocational_key: 6,
  provincial_vocational_general: 3,
  school_key: 2,
  school_general: 1
}

// Scoring rules for honors
const honorScoringRules: Record<string, number> = {
  national: 10,
  provincial: 5,
  school: 3
}

// Scoring rules for competitions
const competitionScoringRules: Record<string, number> = {
  national_first: 10,
  national_second: 8,
  national_third: 6,
  provincial_first: 6,
  provincial_second: 5,
  provincial_third: 3,
  school_first: 3,
  school_second: 2,
  school_third: 1
}

// Scoring rules for innovation competitions
const innovationScoringRules: Record<string, number> = {
  national_gold: 10,
  national_silver: 8,
  national_bronze: 6,
  provincial_gold: 6,
  provincial_silver: 5,
  provincial_bronze: 3,
  school_first: 3,
  school_second: 2,
  school_third: 1
}

// Add reform project
const addReformProject = () => {
  formData.highlights.teachingReformProjects.items.push({
    name: '',
    level: '',
    score: 0
  })
}

// Remove reform project
const removeReformProject = (index: number) => {
  formData.highlights.teachingReformProjects.items.splice(index, 1)
}

// Update reform project score
const updateReformProjectScore = (row: any) => {
  row.score = reformProjectScoringRules[row.level] || 0
}

// Calculate reform projects total
const calculateReformProjectsTotal = () => {
  return formData.highlights.teachingReformProjects.items.reduce(
    (total, item) => total + (item.score || 0),
    0
  )
}

// Add honor
const addHonor = () => {
  formData.highlights.teachingHonors.items.push({
    name: '',
    level: '',
    score: 0
  })
}

// Remove honor
const removeHonor = (index: number) => {
  formData.highlights.teachingHonors.items.splice(index, 1)
}

// Update honor score
const updateHonorScore = (row: any) => {
  row.score = honorScoringRules[row.level] || 0
}

// Calculate honors total
const calculateHonorsTotal = () => {
  return formData.highlights.teachingHonors.items.reduce(
    (total, item) => total + (item.score || 0),
    0
  )
}

// Add competition
const addCompetition = () => {
  formData.highlights.teachingCompetitions.items.push({
    name: '',
    levelPrize: '',
    score: 0
  })
}

// Remove competition
const removeCompetition = (index: number) => {
  formData.highlights.teachingCompetitions.items.splice(index, 1)
}

// Update competition score
const updateCompetitionScore = (row: any) => {
  row.score = competitionScoringRules[row.levelPrize] || 0
}

// Calculate competitions total
const calculateCompetitionsTotal = () => {
  return formData.highlights.teachingCompetitions.items.reduce(
    (total, item) => total + (item.score || 0),
    0
  )
}

// Add innovation competition
const addInnovation = () => {
  formData.highlights.innovationCompetitions.items.push({
    name: '',
    levelPrize: '',
    score: 0
  })
}

// Remove innovation competition
const removeInnovation = (index: number) => {
  formData.highlights.innovationCompetitions.items.splice(index, 1)
}

// Update innovation competition score
const updateInnovationScore = (row: any) => {
  row.score = innovationScoringRules[row.levelPrize] || 0
}

// Calculate innovations total
const calculateInnovationsTotal = () => {
  return formData.highlights.innovationCompetitions.items.reduce(
    (total, item) => total + (item.score || 0),
    0
  )
}

// Calculate highlights total
const calculateHighlightsTotal = () => {
  return (
    calculateReformProjectsTotal() +
    calculateHonorsTotal() +
    calculateCompetitionsTotal() +
    calculateInnovationsTotal()
  )
}

// Update ethics violations deduction
const updateEthicsDeduction = () => {
  formData.negativeList.ethicsViolations.deduction = 
    formData.negativeList.ethicsViolations.count * 10
}

// Update teaching accidents deduction
const updateAccidentsDeduction = () => {
  formData.negativeList.teachingAccidents.deduction = 
    formData.negativeList.teachingAccidents.count * 5
}

// Update ideology issues deduction
const updateIdeologyDeduction = () => {
  formData.negativeList.ideologyIssues.deduction = 
    formData.negativeList.ideologyIssues.count * 5
}

// Update workload incomplete deduction
const updateWorkloadDeduction = () => {
  const percentage = formData.negativeList.workloadIncomplete.percentage
  if (percentage > 30) {
    formData.negativeList.workloadIncomplete.deduction = 10
  } else if (percentage > 20) {
    formData.negativeList.workloadIncomplete.deduction = 5
  } else if (percentage > 10) {
    formData.negativeList.workloadIncomplete.deduction = 2
  } else {
    formData.negativeList.workloadIncomplete.deduction = 0
  }
}

// Calculate negative list total
const calculateNegativeTotal = () => {
  return (
    formData.negativeList.ethicsViolations.deduction +
    formData.negativeList.teachingAccidents.deduction +
    formData.negativeList.ideologyIssues.deduction +
    formData.negativeList.workloadIncomplete.deduction
  )
}

// Calculate final score
const calculateFinalScore = () => {
  return (
    calculateRegularTeachingTotal() +
    calculateHighlightsTotal() -
    calculateNegativeTotal()
  )
}

// Attachment upload methods
const handleIndicatorChange = () => {
  // Don't clear files, just update their indicator
  // This allows users to select indicator after adding files
  if (attachmentFileList.value.length > 0) {
    ElMessage.info('已更新所有文件的考核指标')
    // Update indicator for all existing files
    attachmentFileList.value.forEach(file => {
      (file as any).indicator = attachmentForm.indicator
    })
  }
}

const handleFileChange = (file: UploadUserFile, fileList: UploadUserFile[]) => {
  // Validate indicator is selected
  if (!attachmentForm.indicator) {
    ElMessage.warning('请先选择考核指标')
    return
  }
  
  // Validate file size (50MB)
  const maxSize = 50 * 1024 * 1024
  if (file.size && file.size > maxSize) {
    ElMessage.error(`文件 ${file.name} 大小超过50MB限制`)
    return
  }
  
  // Validate file type
  const indicator = attachmentIndicators.find(i => i.key === attachmentForm.indicator)
  if (indicator) {
    const fileExt = file.name.split('.').pop()?.toLowerCase()
    if (fileExt && !indicator.fileTypes.includes(fileExt)) {
      ElMessage.error(`文件 ${file.name} 格式不支持，请上传 ${indicator.fileTypes.join(', ')} 格式的文件`)
      return
    }
  }
  
  // Add indicator to file metadata
  (file as any).indicator = attachmentForm.indicator
  attachmentFileList.value = fileList
}

const handleFileRemove = (file: UploadUserFile, fileList: UploadUserFile[]) => {
  attachmentFileList.value = fileList
}

const handleExceed = (files: File[]) => {
  ElMessage.warning(`最多只能上传10个文件，当前选择了 ${files.length} 个文件`)
}

const removeFile = (index: number) => {
  attachmentFileList.value.splice(index, 1)
}

const getIndicatorLabel = (key: string): string => {
  const indicator = attachmentIndicators.find(i => i.key === key)
  return indicator ? indicator.label : key
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Upload attachments to backend
const uploadAttachments = async (evaluationId: string): Promise<boolean> => {
  if (attachmentFileList.value.length === 0) {
    return true // No files to upload
  }

  try {
    let successCount = 0
    let failCount = 0

    // Upload each file
    for (const file of attachmentFileList.value) {
      try {
        const indicator = (file as any).indicator || attachmentForm.indicator
        if (!indicator) {
          console.warn('File missing indicator:', file.name)
          failCount++
          continue
        }

        // Create FormData
        const formData = new FormData()
        formData.append('evaluation_id', evaluationId)
        formData.append('indicator', indicator)
        formData.append('files', file.raw as File)

        // Get token
        const token = localStorage.getItem('token')

        // Upload file
        const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
        const response = await fetch(`${baseURL}/teaching-office/attachments`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        })

        if (response.ok) {
          successCount++
        } else {
          console.error('Upload failed for file:', file.name)
          failCount++
        }
      } catch (error) {
        console.error('Error uploading file:', file.name, error)
        failCount++
      }
    }

    if (failCount > 0) {
      ElMessage.warning(`${successCount} 个文件上传成功，${failCount} 个文件上传失败`)
      return false
    } else {
      ElMessage.success(`${successCount} 个附件上传成功`)
      return true
    }
  } catch (error) {
    console.error('Upload attachments error:', error)
    ElMessage.error('附件上传失败')
    return false
  }
}

// Handle submit
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    // 验证表单
    await formRef.value.validate()
    
    // 标记为提交中
    isSubmitting.value = true
    
    // 触发提交事件，传递表单数据和附件上传函数
    emit('submit', {
      formData: { ...formData },
      attachments: attachmentFileList.value,
      uploadAttachments
    })
    
    // 标记为已提交
    isSubmitted.value = true
    
  } catch (error: any) {
    console.error('Submit failed:', error)
    ElMessage.error('请填写所有必填项')
    isSubmitting.value = false
  }
}

// Expose methods
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  getFormData: () => ({ ...formData })
})
</script>

<style scoped>
.new-self-evaluation-form {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.form-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.evaluation-year {
  font-size: 14px;
  color: #909399;
}

.evaluation-form {
  padding: 20px 0;
}

.section-title {
  margin: 0;
  font-size: 18px;
  color: #409EFF;
  font-weight: bold;
}

.score-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.score-label {
  font-weight: 500;
  color: #606266;
}

.max-score {
  color: #909399;
  font-size: 14px;
}

.subtotal-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 15px 20px;
  margin: 20px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.subtotal-label {
  font-size: 16px;
  font-weight: bold;
  color: #ffffff;
  margin-right: 10px;
}

.subtotal-value {
  font-size: 24px;
  font-weight: bold;
  color: #ffffff;
  margin-right: 5px;
}

.subtotal-unit {
  font-size: 14px;
  color: #ffffff;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.form-actions :deep(.el-form-item__content) {
  justify-content: center;
}

/* Highlight sections */
.highlight-section {
  margin: 20px 0;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.highlight-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.scoring-rules-alert {
  margin-bottom: 15px;
}

.scoring-rules {
  font-size: 13px;
  line-height: 1.6;
}

.scoring-rules strong {
  margin-right: 8px;
  color: #409EFF;
}

.score-value {
  font-weight: bold;
  color: #67C23A;
  font-size: 16px;
}

.item-total {
  margin-top: 15px;
  padding: 10px 15px;
  background-color: #ecf5ff;
  border-radius: 4px;
  text-align: right;
  font-size: 15px;
  font-weight: 500;
  color: #606266;
}

.total-value {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  margin: 0 5px;
}

.highlights-subtotal {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* Negative list styles */
.negative-title {
  color: #F56C6C !important;
}

.negative-item {
  margin: 20px 0;
  padding: 20px;
  background-color: #fef0f0;
  border-radius: 8px;
  border: 1px solid #fde2e2;
}

.negative-item-title {
  margin: 0 0 10px 0;
  font-size: 15px;
  font-weight: bold;
  color: #F56C6C;
}

.deduction-rule {
  margin: 0 0 15px 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.6;
}

.negative-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.deduction-display {
  margin-left: 20px;
  font-size: 15px;
  font-weight: 500;
  color: #606266;
}

.deduction-value {
  font-size: 18px;
  font-weight: bold;
  color: #F56C6C;
  margin: 0 5px;
}

.negative-subtotal {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.negative-value {
  color: #ffffff !important;
}

/* Summary card */
.summary-card {
  margin: 20px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.summary-card :deep(.el-descriptions__label) {
  font-weight: bold;
  font-size: 15px;
}

.summary-score {
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
}

.summary-score.negative {
  color: #F56C6C;
}

.final-score {
  font-size: 28px;
  font-weight: bold;
  color: #67C23A;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

/* Attachment upload styles */
.attachment-card {
  margin: 20px 0;
  background-color: #f9f9f9;
  border: 1px solid #e4e7ed;
}

.upload-component {
  width: 100%;
}

.upload-component :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px;
}

.el-upload__tip {
  margin-top: 10px;
  line-height: 1.6;
}

.el-upload__tip p {
  margin: 5px 0;
  font-size: 13px;
  color: #606266;
}

.warning-text {
  color: #e6a23c;
  font-weight: 500;
}

.selected-files {
  margin-top: 20px;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.selected-files h4 {
  margin: 0 0 15px 0;
  font-size: 15px;
  color: #303133;
}
</style>
