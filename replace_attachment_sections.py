"""
批量替换附件上传区域为简单按钮
"""
import re

# 读取文件
with open('frontend/src/components/NewSelfEvaluationForm.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义替换映射
replacements = [
    ('educationResearchFiles', 'educationResearch'),
    ('courseConstructionFiles', 'courseConstruction'),
    ('teacherTeamBuildingFiles', 'teacherTeamBuilding'),
    ('researchAndExchangeFiles', 'researchAndExchange'),
    ('archiveManagementFiles', 'archiveManagement'),
    ('reformProjectsFiles', 'reformProjects'),
    ('teachingHonorsFiles', 'teachingHonors'),
    ('teachingCompetitionsFiles', 'teachingCompetitions'),
    ('innovationCompetitionsFiles', 'innovationCompetitions'),
    ('ethicsViolationsFiles', 'ethicsViolations'),
    ('teachingAccidentsFiles', 'teachingAccidents'),
    ('ideologyIssuesFiles', 'ideologyIssues'),
    ('workloadIncompleteFiles', 'workloadIncomplete'),
]

# 旧的模板模式
old_pattern = r'<div class="attachment-section">\s*<el-card class="mini-attachment-card" shadow="hover">\s*<template #header>\s*<div class="card-header-mini">\s*<span>📎 附件上传（可选）</span>\s*</div>\s*</template>\s*<el-upload\s*:auto-upload="false"\s*:multiple="true"\s*:file-list="(\w+)"\s*:on-change="\(file: any, fileList: any\) => handleInlineFileChange\(file, fileList, \'(\w+)\'\)"\s*:on-remove="\(file: any, fileList: any\) => handleInlineFileRemove\(file, fileList, \'(\w+)\'\)"\s*accept="\.pdf,\.doc,\.docx,\.xls,\.xlsx,\.jpg,\.jpeg,\.png"\s*:limit="5"\s*:on-exceed="handleInlineExceed"\s*drag\s*class="mini-upload"\s*>\s*<el-icon class="el-icon--upload"><upload-filled /></el-icon>\s*<div class="el-upload__text">\s*拖拽或<em>点击上传</em>\s*</div>\s*<template #tip>\s*<div class="el-upload__tip">\s*支持 PDF、Word、Excel、图片<br/>\s*单个文件≤50MB，最多5个\s*</div>\s*</template>\s*</el-upload>\s*<div v-if="\1\.length > 0" class="file-count">\s*已选择 {{ \1\.length }} 个文件\s*</div>\s*</el-card>\s*</div>'

# 新的模板
def new_template(file_list, indicator):
    return f'''<div class="attachment-section">
              <el-upload
                :auto-upload="false"
                :multiple="true"
                :file-list="{file_list}"
                :on-change="(file: any, fileList: any) => handleInlineFileChange(file, fileList, '{indicator}')"
                :on-remove="(file: any, fileList: any) => handleInlineFileRemove(file, fileList, '{indicator}')"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
                :limit="5"
                :on-exceed="handleInlineExceed"
                :show-file-list="false"
              >
                <el-button type="primary" :icon="Upload">
                  附件上传 ({{{{ {file_list}.length }}}})
                </el-button>
              </el-upload>
              
              <div v-if="{file_list}.length > 0" class="uploaded-files-list">
                <div 
                  v-for="file in {file_list}" 
                  :key="file.uid"
                  class="file-item"
                >
                  <el-icon class="file-icon"><Document /></el-icon>
                  <span class="file-name">{{{{ file.name }}}}</span>
                  <el-button
                    type="danger"
                    :icon="Delete"
                    size="small"
                    link
                    @click="handleInlineFileRemove(file, {file_list}, '{indicator}')"
                  />
                </div>
              </div>
              
              <div class="upload-tip">
                支持 PDF、Word、Excel、图片<br/>
                单个≤50MB，最多5个
              </div>
            </div>'''

# 对每个文件列表进行替换
for file_list, indicator in replacements:
    # 构建特定的旧模式
    old_specific = f'''<div class="attachment-section">
              <el-card class="mini-attachment-card" shadow="hover">
                <template #header>
                  <div class="card-header-mini">
                    <span>📎 附件上传（可选）</span>
                  </div>
                </template>
                
                <el-upload
                  :auto-upload="false"
                  :multiple="true"
                  :file-list="{file_list}"
                  :on-change="(file: any, fileList: any) => handleInlineFileChange(file, fileList, '{indicator}')"
                  :on-remove="(file: any, fileList: any) => handleInlineFileRemove(file, fileList, '{indicator}')"
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
                
                <div v-if="{file_list}.length > 0" class="file-count">
                  已选择 {{{{ {file_list}.length }}}} 个文件
                </div>
              </el-card>
            </div>'''
    
    new_specific = new_template(file_list, indicator)
    
    if old_specific in content:
        content = content.replace(old_specific, new_specific)
        print(f"✓ 替换了 {file_list} ({indicator})")
    else:
        print(f"✗ 未找到 {file_list} ({indicator})")

# 保存文件
with open('frontend/src/components/NewSelfEvaluationForm.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n替换完成！")
