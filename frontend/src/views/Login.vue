<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 主内容 -->
    <div class="login-content">
      <!-- 顶部Logo和标题 -->
      <div class="header">
        <img src="/school-logo.jpg" alt="校徽" class="logo" />
        <h1 class="title">教研室数据管理平台</h1>
        <p class="subtitle">Teaching Office Data Management Platform</p>
      </div>

      <!-- 入口选择卡片 -->
      <div class="portal-cards">
        <!-- 教研室端 -->
        <div class="portal-card" @click="selectPortal('teaching-office')">
          <div class="card-icon teaching-office">
            <el-icon><Edit /></el-icon>
          </div>
          <h3 class="card-title">教研室端</h3>
          <p class="card-desc">教研室</p>
          <div class="card-features">
            <span class="feature-tag">自评填报</span>
            <span class="feature-tag">材料提交</span>
            <span class="feature-tag">改进措施</span>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <!-- 管理端 -->
        <div class="portal-card" @click="selectPortal('management')">
          <div class="card-icon management">
            <el-icon><Setting /></el-icon>
          </div>
          <h3 class="card-title">管理端</h3>
          <p class="card-desc">评教小组、评教小组办公室、校长办公会</p>
          <div class="card-features">
            <span class="feature-tag">评分管理</span>
            <span class="feature-tag">数据审核</span>
            <span class="feature-tag">系统配置</span>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>

        <!-- 数据大屏 -->
        <div class="portal-card" @click="goToDashboard">
          <div class="card-icon dashboard">
            <el-icon><Monitor /></el-icon>
          </div>
          <h3 class="card-title">数据大屏</h3>
          <p class="card-desc">公开展示，无需登录</p>
          <div class="card-features">
            <span class="feature-tag">实时数据</span>
            <span class="feature-tag">可视化</span>
            <span class="feature-tag">排名对比</span>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </div>

      <!-- 页脚 -->
      <div class="footer">
        <p>© 2024 教研室数据管理平台 | 版本 2.0.0</p>
      </div>
    </div>

    <!-- 登录对话框 -->
    <el-dialog
      v-model="showLoginDialog"
      :title="loginDialogTitle"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item v-if="selectedPortal === 'management'" label="角色" prop="role">
          <el-select v-model="loginForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="评教小组" value="evaluation_team" />
            <el-option label="评教小组办公室" value="evaluation_office" />
            <el-option label="校长办公会" value="president_office" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showLoginDialog = false">取消</el-button>
          <el-button type="primary" @click="handleLogin" :loading="loginLoading">
            登录
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Edit, Setting, Monitor, ArrowRight } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const showLoginDialog = ref(false)
const selectedPortal = ref<'teaching-office' | 'management' | ''>('')
const loginLoading = ref(false)
const loginFormRef = ref()

const loginForm = ref({
  username: '',
  password: '',
  role: ''
})

const loginRules = computed(() => {
  const rules: any = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
    ]
  }
  
  // 只有管理端需要选择角色
  if (selectedPortal.value === 'management') {
    rules.role = [
      { required: true, message: '请选择角色', trigger: 'change' }
    ]
  }
  
  return rules
})

const loginDialogTitle = computed(() => {
  if (selectedPortal.value === 'teaching-office') {
    return '教研室端登录'
  } else if (selectedPortal.value === 'management') {
    return '管理端登录'
  }
  return '登录'
})

const selectPortal = (portal: 'teaching-office' | 'management') => {
  selectedPortal.value = portal
  loginForm.value = {
    username: '',
    password: '',
    role: ''
  }
  showLoginDialog.value = true
}

const goToDashboard = () => {
  router.push('/data-dashboard')
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loginLoading.value = true
      
      try {
        // 调用真实的登录API
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: loginForm.value.username,
            password: loginForm.value.password,
            role: selectedPortal.value === 'teaching-office' ? 'teaching_office' : loginForm.value.role
          })
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || '登录失败')
        }
        
        const data = await response.json()
        
        // 构造用户对象
        const user = {
          id: data.userId,
          name: loginForm.value.username,
          role: data.role,
          teaching_office_id: data.teachingOfficeId || ''
        }
        
        // 保存认证信息到store
        authStore.setAuth({
          token: data.token,
          user: user
        })
        
        ElMessage.success('登录成功！')
        showLoginDialog.value = false
        
        // 根据端口跳转
        if (selectedPortal.value === 'teaching-office') {
          router.push('/teaching-office-home')
        } else if (selectedPortal.value === 'management') {
          router.push('/management-home')
        }
      } catch (error: any) {
        console.error('Login error:', error)
        ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      } finally {
        loginLoading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  right: -50px;
  animation-delay: 5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 10%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

/* 主内容 */
.login-content {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1200px;
  padding: 2rem;
}

/* 头部 */
.header {
  text-align: center;
  margin-bottom: 3rem;
  animation: fadeInDown 0.8s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logo {
  width: 100px;
  height: 100px;
  object-fit: contain;
  border-radius: 20px;
  margin-bottom: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  background: white;
  padding: 10px;
}

.title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 2px;
}

/* 入口卡片 */
.portal-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.portal-card {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.8s ease-out;
  animation-fill-mode: both;
}

.portal-card:nth-child(1) {
  animation-delay: 0.1s;
}

.portal-card:nth-child(2) {
  animation-delay: 0.2s;
}

.portal-card:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.portal-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, transparent 0%, rgba(102, 126, 234, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.4s;
}

.portal-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.portal-card:hover::before {
  opacity: 1;
}

.card-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  color: white;
  margin-bottom: 1.5rem;
  transition: all 0.4s;
}

.portal-card:hover .card-icon {
  transform: scale(1.1) rotate(5deg);
}

.card-icon.teaching-office {
  background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
}

.card-icon.management {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-icon.dashboard {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.card-desc {
  font-size: 0.95rem;
  color: #666;
  margin-bottom: 1rem;
}

.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.feature-tag {
  padding: 0.25rem 0.75rem;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 0.85rem;
  color: #666;
  transition: all 0.3s;
}

.portal-card:hover .feature-tag {
  background: #667eea;
  color: white;
}

.card-arrow {
  position: absolute;
  bottom: 1.5rem;
  right: 1.5rem;
  font-size: 1.5rem;
  color: #667eea;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.4s;
}

.portal-card:hover .card-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* 页脚 */
.footer {
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  animation: fadeIn 1s ease-out 0.5s both;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .title {
    font-size: 1.8rem;
  }
  
  .portal-cards {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .portal-card {
    padding: 1.5rem;
  }
}

/* 对话框样式 */
:deep(.el-dialog) {
  border-radius: 20px;
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px 20px 0 0;
  padding: 1.5rem;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 2rem;
}
</style>
