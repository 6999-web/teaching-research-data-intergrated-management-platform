import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/teaching-office-home',
      name: 'teaching-office-home',
      component: () => import('@/views/TeachingOfficeHome.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/management-home',
      name: 'management-home',
      component: () => import('@/views/ManagementHome.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/data-dashboard',
      name: 'data-dashboard',
      component: () => import('@/views/DataDashboard.vue')
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/self-evaluation',
      name: 'self-evaluation',
      component: () => import('@/views/SelfEvaluation.vue')
    },
    {
      path: '/attachment-upload/:id?',
      name: 'attachment-upload',
      component: () => import('@/views/AttachmentUpload.vue')
    },
    {
      path: '/manual-scoring',
      name: 'manual-scoring',
      component: () => import('@/views/ManualScoring.vue')
    },
    {
      path: '/final-score',
      name: 'final-score',
      component: () => import('@/views/FinalScore.vue')
    },
    {
      path: '/data-sync',
      name: 'data-sync',
      component: () => import('@/views/DataSync.vue')
    },
    {
      path: '/publication',
      name: 'publication',
      component: () => import('@/views/Publication.vue')
    },
    {
      path: '/anomaly-handling',
      name: 'anomaly-handling',
      component: () => import('@/views/AnomalyHandling.vue')
    },
    {
      path: '/president-office-dashboard',
      name: 'president-office-dashboard',
      component: () => import('@/views/PresidentOfficeDashboard.vue')
    },
    {
      path: '/result/:id?',
      name: 'result-view',
      component: () => import('@/views/ResultView.vue')
    },
    {
      path: '/management-results',
      name: 'management-results',
      component: () => import('@/views/ManagementResultView.vue')
    },
    {
      path: '/scoring-progress',
      name: 'scoring-progress',
      component: () => import('@/views/ScoringProgress.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/submit-to-office',
      name: 'submit-to-office',
      component: () => import('@/views/SubmitToOffice.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/scoring-rules',
      name: 'scoring-rules',
      component: () => import('@/views/ScoringRules.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/my-scoring-records',
      name: 'my-scoring-records',
      component: () => import('@/views/MyScoringRecords.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/anomaly-records',
      name: 'anomaly-records',
      component: () => import('@/views/AnomalyRecords.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/all-scoring-records',
      name: 'all-scoring-records',
      component: () => import('@/views/AllScoringRecords.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/attachment-management',
      name: 'attachment-management',
      component: () => import('@/views/AttachmentManagement.vue')
    },
    {
      path: '/college-dashboard',
      name: 'college-dashboard',
      component: () => import('@/views/CollegeDashboard.vue')
    },
    {
      path: '/improvement-plan/:id',
      name: 'improvement-plan',
      component: () => import('@/views/ImprovementPlan.vue')
    }
  ]
})

// 进入需登录页面时从 localStorage 恢复 auth，解决刷新后空白
router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    const role = localStorage.getItem('userRole')
    if (token && role) {
      try {
        const authStore = useAuthStore()
        authStore.loadFromStorage()
      } catch {
        // ignore
      }
    }
  }
  next()
})

export default router
