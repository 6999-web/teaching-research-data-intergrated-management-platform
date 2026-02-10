#!/bin/bash

# 教研室数据管理平台 - 简化部署脚本
# 服务器 IP: 101.33.211.98

set -e

echo "=================================="
echo "教研室数据管理平台 - 部署脚本"
echo "服务器 IP: 101.33.211.98"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}建议使用 root 用户运行此脚本${NC}"
    echo "或使用: sudo bash deploy-simple.sh"
fi

# 1. 更新系统包
echo -e "${GREEN}[1/6] 更新系统包...${NC}"
apt-get update -y

# 2. 安装必要的软件
echo -e "${GREEN}[2/6] 安装必要软件...${NC}"
apt-get install -y python3 python3-pip python3-venv nodejs npm nginx

# 3. 部署后端
echo -e "${GREEN}[3/6] 部署后端...${NC}"
cd backend

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt

# 初始化数据库
echo "初始化 SQLite 数据库..."
python init_sqlite.py

# 创建 systemd 服务文件
echo "创建后端服务..."
cat > /etc/systemd/system/teaching-office-backend.service << EOF
[Unit]
Description=Teaching Office Evaluation Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动后端服务
systemctl daemon-reload
systemctl enable teaching-office-backend
systemctl restart teaching-office-backend

cd ..

# 4. 部署前端
echo -e "${GREEN}[4/6] 部署前端...${NC}"
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

cd ..

# 5. 配置 Nginx
echo -e "${GREEN}[5/6] 配置 Nginx...${NC}"

# 创建 Nginx 配置
cat > /etc/nginx/sites-available/teaching-office << 'EOF'
server {
    listen 80;
    server_name 101.33.211.98;

    # 前端静态文件
    location / {
        root /var/www/teaching-office;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 文件上传
    location /api/teaching-office/attachments {
        client_max_body_size 500M;
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# 复制前端文件到 Nginx 目录
mkdir -p /var/www/teaching-office
cp -r frontend/dist/* /var/www/teaching-office/

# 启用站点
ln -sf /etc/nginx/sites-available/teaching-office /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
nginx -t

# 重启 Nginx
systemctl restart nginx

# 6. 配置防火墙
echo -e "${GREEN}[6/6] 配置防火墙...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 8000/tcp
    echo "防火墙规则已添加"
fi

echo ""
echo -e "${GREEN}=================================="
echo "部署完成！"
echo "==================================${NC}"
echo ""
echo "访问地址："
echo "  前端: http://101.33.211.98"
echo "  后端 API: http://101.33.211.98:8000"
echo "  API 文档: http://101.33.211.98:8000/docs"
echo ""
echo "服务管理命令："
echo "  查看后端状态: systemctl status teaching-office-backend"
echo "  重启后端: systemctl restart teaching-office-backend"
echo "  查看后端日志: journalctl -u teaching-office-backend -f"
echo "  重启 Nginx: systemctl restart nginx"
echo ""
echo "数据库文件位置："
echo "  $(pwd)/backend/teaching_office_evaluation.db"
echo ""
