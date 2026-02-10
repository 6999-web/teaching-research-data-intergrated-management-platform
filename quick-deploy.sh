#!/bin/bash

# 快速部署脚本 - 在服务器上运行

echo "================================"
echo "教研室数据管理平台 - 快速部署"
echo "================================"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用root用户运行此脚本"
    exit 1
fi

# 设置项目路径
PROJECT_DIR="/root/teaching-office-platform"

# 1. 安装系统依赖
echo "步骤 1/8: 安装系统依赖..."
apt update
apt install -y python3 python3-pip nodejs npm nginx postgresql postgresql-contrib

# 2. 配置PostgreSQL
echo "步骤 2/8: 配置数据库..."
systemctl start postgresql
systemctl enable postgresql

# 创建数据库（如果不存在）
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'teaching_office_evaluation'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE DATABASE teaching_office_evaluation;"

# 创建用户（如果不存在）
sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'teaching_office_user'" | grep -q 1 || \
sudo -u postgres psql -c "CREATE USER teaching_office_user WITH PASSWORD 'teaching_office_2024';"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE teaching_office_evaluation TO teaching_office_user;"

# 3. 安装后端依赖
echo "步骤 3/8: 安装后端依赖..."
cd $PROJECT_DIR/backend
pip3 install -r requirements.txt

# 4. 配置环境变量
echo "步骤 4/8: 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    # 生成随机SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-production-secret-key-change-this-to-random-string/$SECRET_KEY/" .env
    sed -i "s/your_password_here/teaching_office_2024/" .env
    echo "环境变量已配置，请检查 backend/.env 文件"
fi

# 5. 运行数据库迁移
echo "步骤 5/8: 运行数据库迁移..."
alembic upgrade head

# 6. 构建前端
echo "步骤 6/8: 构建前端..."
cd $PROJECT_DIR/frontend
npm install
npm run build

# 7. 配置systemd服务
echo "步骤 7/8: 配置后端服务..."
cat > /etc/systemd/system/teaching-office-backend.service << EOF
[Unit]
Description=Teaching Office Evaluation Backend
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl start teaching-office-backend
systemctl enable teaching-office-backend

# 8. 配置Nginx
echo "步骤 8/8: 配置Nginx..."
cat > /etc/nginx/sites-available/teaching-office << 'EOF'
server {
    listen 80;
    server_name 101.33.211.98;

    location / {
        root /root/teaching-office-platform/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /root/teaching-office-platform/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 100M;
}
EOF

ln -sf /etc/nginx/sites-available/teaching-office /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
systemctl enable nginx

# 配置防火墙
echo "配置防火墙..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force enable

echo ""
echo "================================"
echo "部署完成！"
echo "================================"
echo ""
echo "服务状态："
systemctl status teaching-office-backend --no-pager
systemctl status nginx --no-pager
echo ""
echo "访问地址: http://101.33.211.98"
echo "API文档: http://101.33.211.98/docs"
echo ""
echo "查看后端日志: journalctl -u teaching-office-backend -f"
echo "查看Nginx日志: tail -f /var/log/nginx/error.log"
echo ""
