"""
替换剩余的附件上传区域
"""

# 读取文件
with open('frontend/src/components/NewSelfEvaluationForm.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义剩余的替换
remaining_replacements = [
    ('teachingHonorsFiles', 'teachingHonors', '荣誉表彰证明材料'),
    ('teachingCompetitionsFiles', 'teachingCompetitions', '教学比赛证明材料'),
    ('innovationCompetitionsFiles', 'innovationCompetitions', '创新创业比赛证明材料'),
    ('ethicsViolationsFiles', 'ethicsViolations', '相关说明材料'),
    ('teachingAccidentsFiles', 'teachingAccidents', '相关说明材料'),
    ('ideologyIssuesFiles', 'ideologyIssues', '相关说明材料'),
    ('workloadIncompleteFiles', 'workloadIncomplete', '相关说明材料'),
]

count = 0

for file_list, indicator, desc in remaining_replacements:
    # 旧的模板（highlight或negative）
    old_template1 = f'''<div class="highlight-attachment">
            <el-card class="mini-attachment-card" shadow="hover">
              <template #header>
                <div class="card-header-mini">
                  <span>📎 相关附件上传（可选）</span>
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
                    上传{desc}<br/>
                    支持 PDF、Word、Excel、图片 | 单个文件≤50MB，最多5个
                  </div>
                </template>
              </el-upload>
              
              <div v-if="{file_list}.length > 0" class="file-count">
                已选择 {{{{ {file_list}.length }}}} 个文件
              </div>
            </el-card>
          </div>'''
    
    old_template2 = f'''<div class="negative-attachment" style="margin-top: 15px;">
            <el-card class="mini-attachment-card" shadow="hover">
              <template #header>
                <div class="card-header-mini">
                  <span>📎 相关附件上传（可选）</span>
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
                    上传{desc}<br/>
                    支持 PDF、Word、Excel、图片 | 单个文件≤50MB，最多5个
                  </div>
                </template>
              </el-upload>
              
              <div v-if="{file_list}.length > 0" class="file-count">
                已选择 {{{{ {file_list}.length }}}} 个文件
              </div>
            </el-card>
          </div>'''
    
    # 新的模板（highlight）
    new_template1 = f'''<div class="highlight-attachment">
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
              <el-button type="primary" :icon="Upload" size="large">
                📎 上传{desc} ({{{{ {file_list}.length }}}})
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
              支持 PDF、Word、Excel、图片 | 单个≤50MB，最多5个
            </div>
          </div>'''
    
    # 新的模板（negative）
    new_template2 = f'''<div class="negative-attachment" style="margin-top: 15px;">
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
              <el-button type="warning" :icon="Upload" size="large">
                📎 上传{desc} ({{{{ {file_list}.length }}}})
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
              支持 PDF、Word、Excel、图片 | 单个≤50MB，最多5个
            </div>
          </div>'''
    
    # 尝试替换
    if old_template1 in content:
        content = content.replace(old_template1, new_template1)
        count += 1
        print(f"✓ 替换了 {file_list} ({indicator}) - highlight")
    elif old_template2 in content:
        content = content.replace(old_template2, new_template2)
        count += 1
        print(f"✓ 替换了 {file_list} ({indicator}) - negative")
    else:
        print(f"✗ 未找到 {file_list} ({indicator})")

# 保存文件
with open('frontend/src/components/NewSelfEvaluationForm.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n替换完成！共替换了 {count} 个附件上传区域")
