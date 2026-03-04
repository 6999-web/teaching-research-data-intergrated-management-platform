// President Office types for real-time data monitoring

export interface TeachingOfficeScore {
  teaching_office_id: string;
  teaching_office_name: string;
  evaluation_year: number;
  ai_score?: number;
  manual_scores: Array<{
    reviewer_name: string;
    reviewer_role: 'evaluation_team' | 'evaluation_office';
    total_score: number;
  }>;
  final_score?: number;
  status: string;
}

export interface TeachingOfficeHistoricalScore {
  teaching_office_id: string;
  teaching_office_name: string;
  scores: Array<{
    year: number;
    final_score: number;
  }>;
}

export interface IndicatorScoreComparison {
  indicator: string;
  indicator_label: string;
  teaching_offices: Array<{
    teaching_office_id: string;
    teaching_office_name: string;
    score: number;
  }>;
}

export interface DashboardData {
  teaching_office_scores: TeachingOfficeScore[];
  historical_scores: TeachingOfficeHistoricalScore[];
  indicator_comparisons: IndicatorScoreComparison[];
}

export interface DashboardFilters {
  year?: number;
  indicator?: string;
  sortBy?: 'ai_score' | 'final_score' | 'teaching_office_name';
  sortOrder?: 'asc' | 'desc';
}

export interface ApprovalRequest {
  evaluation_ids: string[];
  decision: 'approve' | 'reject';
  reject_reason?: string;
}

export interface ApprovalResponse {
  approval_id: string;
  decision: string;
  approved_at: string;
  message: string;
  synced_to_management: boolean;
}
