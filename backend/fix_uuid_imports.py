"""
修复模型文件中的UUID导入

将所有模型文件中的 UUID 从 postgresql 特定类型改为自定义的跨平台类型
"""

import os
import re

# 模型文件目录
models_dir = "app/models"

# 需要替换的导入语句
old_import = "from sqlalchemy.dialects.postgresql import UUID"
new_import = "from app.db.types import UUID"

# 获取所有模型文件
model_files = [
    f for f in os.listdir(models_dir)
    if f.endswith('.py') and f != '__init__.py'
]

print("开始修复UUID导入...")
print("=" * 60)

for filename in model_files:
    filepath = os.path.join(models_dir, filename)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含旧的导入
    if old_import in content:
        # 替换导入语句
        new_content = content.replace(old_import, new_import)
        
        # 移除 ARRAY 导入（如果存在）
        new_content = re.sub(
            r'from sqlalchemy\.dialects\.postgresql import UUID, ARRAY\n',
            new_import + '\n',
            new_content
        )
        new_content = re.sub(
            r'from sqlalchemy\.dialects\.postgresql import ARRAY, UUID\n',
            new_import + '\n',
            new_content
        )
        
        # 写回文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ 已修复: {filename}")
    else:
        print(f"- 跳过: {filename} (无需修复)")

print("=" * 60)
print("UUID导入修复完成！")
