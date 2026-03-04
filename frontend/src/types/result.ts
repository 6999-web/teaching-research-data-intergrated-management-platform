// Result viewing types for teaching office end

import type { AIScoreDetail, ManualScoreDetail, FinalScoreDetail } from './scoring'

export interface InsightSummary {
  id: string;
  evaluation_id: string;
  summary: string;
  generated_at: string;
}

export interface EvaluationResult {
  evaluation_id: string;
  teaching_office_id: string;
  teaching_office_name: string;
  evaluation_year: number;
  status: string;
  
  // Scoring details
  ai_score?: AIScoreDetail;
  manual_scores: ManualScoreDetail[];
  final_score?: FinalScoreDetail;
  
  // Insight summary
  insight_summary?: InsightSummary;
  
  // Publication info
  published_at?: string;
  distributed_at?: string;
}

export interface ResultDetailResponse {
  evaluation_id: string;
  teaching_office_name: string;
  evaluation_year: number;
  final_score: number;
  scoring_details: {
    ai_score?: AIScoreDetail;
    manual_scores: ManualScoreDetail[];
    final_score?: FinalScoreDetail;
  };
  insight_summary: string;
  publication_date: string;
}
