import apiClient from './client'

export interface ImprovementPlan {
  id: string
  evaluation_id: string
  indicator_item_id: number
  target: string
  measures: string
  charger_id: string
  deadline: string
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'COMPLETED'
  supervisor_comment?: string
  created_at: string
  updated_at: string
}

export interface ImprovementPlanCreate {
  evaluation_id: string
  indicator_item_id: number
  target: string
  measures: string
  charger_id: string
  deadline: string
}

export interface ImprovementPlanReview {
  status: 'APPROVED' | 'REJECTED'
  supervisor_comment?: string
}

export const improvementApi = {
  create: (data: ImprovementPlanCreate) => {
    return apiClient.post<ImprovementPlan>('/improvements/', data)
  },
  
  getByEvaluation: (evaluationId: string) => {
    return apiClient.get<ImprovementPlan[]>(`/improvements/evaluation/${evaluationId}`)
  },
  
  update: (id: string, data: Partial<ImprovementPlanCreate>) => {
    return apiClient.put<ImprovementPlan>(`/improvements/${id}`, data)
  },
  
  review: (id: string, data: ImprovementPlanReview) => {
    return apiClient.post<ImprovementPlan>(`/improvements/${id}/review`, data)
  }
}
