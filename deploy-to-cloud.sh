#!/bin/bash

# 教研室数据管理平台 - 腾讯云部署脚本
# 服务器IP: 101.33.211.98

echo "================================"
echo "教研室数据管理平台 - 部署脚本"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

echo -e "${YELLOW}步骤 1/6: 构建前端${NC}"
cd frontend
npm install
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}前端构建失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 前端构建完成${NC}"
cd ..

echo -e "${YELLOW}步骤 2/6: 准备后端环境${NC}"
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}后端依赖安装失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
cd ..

echo -e "${YELLOW}步骤 3/6: 配置环境变量${NC}"
# 复制生产环境配置
if [ ! -f "backend/.env" ]; then
    cp backend/.env.production backend/.env
    echo -e "${YELLOW}⚠ 请编辑 backend/.env 文件，配置数据库密码和API密钥${NC}"
fi
echo -e "${GREEN}✓ 环境变量配置完成${NC}"

echo -e "${YELLOW}步骤 4/6: 数据库迁移${NC}"
cd backend
# 运行数据库迁移
alembic upgrade head
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠ 数据库迁移失败，可能需要手动配置数据库${NC}"
fi
cd ..

echo -e "${YELLOW}步骤 5/6: 创建systemd服务文件${NC}"
cat > teaching-office-backend.service << 'EOF'
[Unit]
Description=Teaching Office Evaluation Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/teaching-office-platform/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ systemd服务文件已创建${NC}"
echo -e "${YELLOW}请将 teaching-office-backend.service 复制到 /etc/systemd/system/${NC}"

echo -e "${YELLOW}步骤 6/6: 创建Nginx配置${NC}"
cat > nginx-teaching-office.conf << 'EOF'
server {
    listen 80;
    server_name 101.33.211.98;

    # 前端静态文件
    location / {
        root /root/teaching-office-platform/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API文档
    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /root/teaching-office-platform/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

echo -e "${GREEN}✓ Nginx配置文件已创建${NC}"
echo -e "${YELLOW}请将 nginx-teaching-office.conf 复制到 /etc/nginx/sites-available/${NC}"

echo ""
echo "================================"
echo -e "${GREEN}部署准备完成！${NC}"
echo "================================"
echo ""
echo "后续步骤："
echo "1. 上传项目到服务器: scp -r . root@101.33.211.98:/root/teaching-office-platform"
echo "2. 在服务器上运行此脚本"
echo "3. 配置 backend/.env 文件（数据库密码、API密钥等）"
echo "4. 复制systemd服务文件: sudo cp teaching-office-backend.service /etc/systemd/system/"
echo "5. 启动后端服务: sudo systemctl start teaching-office-backend"
echo "6. 设置开机自启: sudo systemctl enable teaching-office-backend"
echo "7. 复制Nginx配置: sudo cp nginx-teaching-office.conf /etc/nginx/sites-available/teaching-office"
echo "8. 启用Nginx站点: sudo ln -s /etc/nginx/sites-available/teaching-office /etc/nginx/sites-enabled/"
echo "9. 测试Nginx配置: sudo nginx -t"
echo "10. 重启Nginx: sudo systemctl restart nginx"
echo ""
echo "访问地址: http://101.33.211.98"
echo ""
