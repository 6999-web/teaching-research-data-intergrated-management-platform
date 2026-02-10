import axios from 'axios'

// 根据环境变量设置API基础URL
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API methods for self-evaluation
export const selfEvaluationApi = {
  // Submit self-evaluation (lock form and attachments)
  submit: (evaluationId: string) => {
    return apiClient.post(`/teaching-office/self-evaluation/${evaluationId}/submit`)
  },
  
  // Trigger AI scoring
  triggerAIScoring: (evaluationId: string) => {
    return apiClient.post('/teaching-office/trigger-ai-scoring', {
      evaluation_id: evaluationId
    })
  },
  
  // Get self-evaluation status
  getStatus: (evaluationId: string) => {
    return apiClient.get(`/teaching-office/self-evaluation/${evaluationId}`)
  }
}

// API methods for scoring
export const scoringApi = {
  // Submit manual score
  submitManualScore: (data: any) => {
    return apiClient.post('/scoring/manual-score', data)
  },
  
  // Get all scores for an evaluation
  getAllScores: (evaluationId: string) => {
    return apiClient.get(`/scoring/all-scores/${evaluationId}`)
  },
  
  // Submit final score
  submitFinalScore: (data: any) => {
    return apiClient.post('/scoring/final-score', data)
  }
}

// API methods for review (anomaly handling, sync, approval)
export const reviewApi = {
  // Get anomalies list
  getAnomalies: (params?: { evaluation_id?: string; status?: string }) => {
    return apiClient.get('/review/anomalies', { params })
  },
  
  // Get anomaly detail
  getAnomalyDetail: (anomalyId: string) => {
    return apiClient.get(`/review/anomalies/${anomalyId}`)
  },
  
  // Handle anomaly (reject or correct)
  handleAnomaly: (data: any) => {
    return apiClient.post('/review/handle-anomaly', data)
  },
  
  // Sync to president office
  syncToPresidentOffice: (evaluationIds: string[]) => {
    return apiClient.post('/review/sync-to-president-office', {
      evaluation_ids: evaluationIds
    })
  },
  
  // Approve results
  approve: (data: any) => {
    return apiClient.post('/review/approve', data)
  }
}

// API methods for president office
export const presidentOfficeApi = {
  // Get dashboard data
  getDashboardData: (params?: { year?: number; indicator?: string }) => {
    return apiClient.get('/president-office/dashboard', { params })
  },
  
  // Get teaching office scores
  getTeachingOfficeScores: (params?: { year?: number }) => {
    return apiClient.get('/president-office/scores', { params })
  },
  
  // Get historical scores
  getHistoricalScores: (teachingOfficeId?: string) => {
    return apiClient.get('/president-office/historical-scores', {
      params: { teaching_office_id: teachingOfficeId }
    })
  },
  
  // Get indicator comparison
  getIndicatorComparison: (indicator: string, year?: number) => {
    return apiClient.get('/president-office/indicator-comparison', {
      params: { indicator, year }
    })
  },
  
  // Approve evaluation results
  approveResults: (data: any) => {
    return apiClient.post('/president-office/approve', data)
  }
}

// API methods for publication
export const publicationApi = {
  // Publish results (initiate publication)
  publish: (data: any) => {
    return apiClient.post('/publication/publish', data)
  },
  
  // Get publications list
  getPublications: () => {
    return apiClient.get('/publication/publications')
  },
  
  // Get publication detail
  getPublicationDetail: (publicationId: string) => {
    return apiClient.get(`/publication/publications/${publicationId}`)
  },
  
  // Distribute results
  distribute: (data: any) => {
    return apiClient.post('/publication/distribute', data)
  },
  
  // Get evaluations ready for publication (approved by president office)
  getEvaluationsForPublication: (params?: { year?: number }) => {
    return apiClient.get('/publication/evaluations-for-publication', { params })
  }
}

// API methods for teaching office results
export const resultApi = {
  // Get result for teaching office
  getResult: (evaluationId: string) => {
    return apiClient.get(`/teaching-office/result/${evaluationId}`)
  },
  
  // Get published results for teaching office
  getPublishedResults: (teachingOfficeId: string, year?: number) => {
    return apiClient.get('/teaching-office/published-results', {
      params: { teaching_office_id: teachingOfficeId, year }
    })
  }
}

// API methods for management results summary
export const managementResultApi = {
  // Get all teaching offices results summary for management
  getAllResults: (params?: { year?: number; status?: string }) => {
    return apiClient.get('/management/results', { params })
  },
  
  // Get detailed result for a specific teaching office
  getResultDetail: (evaluationId: string) => {
    return apiClient.get(`/management/results/${evaluationId}`)
  }
}

export default apiClient
