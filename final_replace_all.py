"""
最终替换所有剩余的附件上传区域
"""
import re

# 读取文件
with open('frontend/src/components/NewSelfEvaluationForm.vue', 'r', encoding='utf-8') as f:
    content = f.read()

# 使用正则表达式查找所有mini-attachment-card模式
pattern = r'<el-card class="mini-attachment-card" shadow="hover">.*?</el-card>'

matches = re.findall(pattern, content, re.DOTALL)
print(f"找到 {len(matches)} 个需要替换的附件上传区域")

# 对每个匹配进行替换
for match in matches:
    # 提取file-list名称
    file_list_match = re.search(r':file-list="(\w+)"', match)
    if not file_list_match:
        continue
    
    file_list = file_list_match.group(1)
    
    # 提取indicator
    indicator_match = re.search(r"handleInlineFileChange\(file, fileList, '(\w+)'\)", match)
    if not indicator_match:
        continue
    
    indicator = indicator_match.group(1)
    
    # 提取描述文本（如果有）
    tip_match = re.search(r'<div class="el-upload__tip">\s*([^<]+)<br/>', match)
    desc = "附件"
    if tip_match:
        desc_text = tip_match.group(1).strip()
        if "荣誉" in desc_text:
            desc = "荣誉证书、表彰文件"
        elif "教学比赛" in desc_text or "比赛" in desc_text:
            desc = "比赛证明材料"
        elif "创新" in desc_text:
            desc = "创新创业比赛证明"
        elif "说明" in desc_text:
            desc = "相关说明材料"
        else:
            desc = "相关证明材料"
    
    # 判断是highlight还是negative
    is_negative = 'negative-attachment' in content[max(0, content.find(match)-200):content.find(match)]
    button_type = "warning" if is_negative else "primary"
    
    # 生成新的模板
    new_template = f'''<el-upload
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
              <el-button type="{button_type}" :icon="Upload" size="large">
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
            </div>'''
    
    # 替换
    content = content.replace(match, new_template)
    print(f"✓ 替换了 {file_list} ({indicator})")

# 保存文件
with open('frontend/src/components/NewSelfEvaluationForm.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n替换完成！")
