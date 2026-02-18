# 清除前端缓存并重启

Write-Host "清除前端缓存..." -ForegroundColor Green

# 删除node_modules和dist
if (Test-Path "frontend/node_modules") {
    Remove-Item -Recurse -Force "frontend/node_modules"
    Write-Host "已删除 node_modules" -ForegroundColor Green
}

if (Test-Path "frontend/dist") {
    Remove-Item -Recurse -Force "frontend/dist"
    Write-Host "已删除 dist" -ForegroundColor Green
}

# 重新安装依赖
Write-Host "重新安装前端依赖..." -ForegroundColor Green
cd frontend
npm install
cd ..

Write-Host "缓存清除完成！" -ForegroundColor Green
Write-Host "请手动重启前端服务：npm run dev" -ForegroundColor Yellow
