import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue')
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

export default router
