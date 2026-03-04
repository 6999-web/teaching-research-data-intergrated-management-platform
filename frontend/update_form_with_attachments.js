// 这个脚本用于批量更新表单字段，为每个字段添加附件上传功能

const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'src/components/NewSelfEvaluationForm.vue');
let content = fs.readFileSync(filePath, 'utf-8');

// 定义所有需要添加附件上传的字段
const fields = [
  {
    key: 'teachingQualityManagement',
    label: '教学质量管理',
    number: '2'
  },
  {
    key: 'courseAssessment',
    label: '课程考核',
    number: '3'
  },
  {
    key: 'educationResearch',
    label: '教育教学科研工作',
    number: '4'
  },
  {
    key: 'courseConstruction',
    label: '课程建设',
    number: '5'
  },
  {
    key: 'teacherTeamBuilding',
    label: '教师队伍建设',
    number: '6'
  },
  {
    key: 'researchAndExchange',
    label: '科学研究与学术交流',
    number: '7'
  },
  {
    key: 'archiveManagement',
    label: '教学档案室管理与建设',
    number: '8'
  }
];

// 为每个字段生成附件上传组件的模板
function generateAttachmentSection(key, label) {
  return `
            <!-- 右侧附件上传区域 -->
            <div class="attachment-section">
              <el-card class="mini-attachment-card" shadow="hover">
                <template #header>
                  <div class="card-header-mini">
                    <span>📎 附件上传（可选）</span>
                  </div>
                </template>
                
                <el-upload
                  :auto-upload="false"
                  :multiple="true"
                  :file-list="${key}Files"
                  :on-change="(file: any, fileList: any) => handleInlineFileChange(file, fileList, '${key}')"
                  :on-remove="(file: any, fileList: any) => handleInlineFileRemove(file, fileList, '${key}')"
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                  :limit="5"
                  :on-exceed="handleInlineExceed"
                  drag
                  class="mini-upload"
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽或<em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 PDF、Word、Excel、图片<br/>
                      单个文件≤50MB，最多5个
                    </div>
                  </template>
                </el-upload>
                
                <div v-if="${key}Files.length > 0" class="file-count">
                  已选择 {{ ${key}Files.length }} 个文件
                </div>
              </el-card>
            </div>
          </div>`;
}

console.log('字段配置:', fields);
console.log('准备更新文件...');
