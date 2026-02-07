import apiClient from './client'

export interface CollegeStats {
    avg_score: number
    rank_list: Array<{ name: string; score: number }>
    weakness_analysis: Array<{ indicator: string; avg_loss_rate: number }>
}

export const collegeApi = {
    getDashboardStats: () => {
        return apiClient.get<CollegeStats>('/college/dashboard/stats')
    }
}
