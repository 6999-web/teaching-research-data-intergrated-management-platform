// Scoring types for manual scoring functionality

export interface IndicatorScore {
  indicator: string;
  score: number;
  comment: string;
}

export interface ManualScoreCreate {
  evaluation_id: string;
  scores: IndicatorScore[];
}

export interface ManualScoreResponse {
  score_record_id: string;
  submitted_at: string;
}

export interface ManualScoreDetail {
  id: string;
  evaluation_id: string;
  reviewer_id: string;
  reviewer_name: string;
  reviewer_role: 'evaluation_team' | 'evaluation_office';
  weight: number;
  scores: IndicatorScore[];
  submitted_at: string;
}

export interface AIScoreDetail {
  id: string;
  evaluation_id: string;
  total_score: number;
  indicator_scores: Array<{
    indicator: string;
    score: number;
    reasoning: string;
  }>;
  parsed_reform_projects: number;
  parsed_honorary_awards: number;
  scored_at: string;
}

export interface FinalScoreDetail {
  id: string;
  evaluation_id: string;
  final_score: number;
  summary?: string;
  determined_by: string;
  determined_at: string;
}

export interface FinalScoreCreate {
  evaluation_id: string;
  final_score: number;
  summary: string;
}

export interface FinalScoreResponse {
  final_score_id: string;
  determined_at: string;
}

export interface AllScoresResponse {
  evaluation_id: string;
  ai_score?: AIScoreDetail;
  manual_scores: ManualScoreDetail[];
  final_score?: FinalScoreDetail;
}

// Predefined evaluation indicators
export const EVALUATION_INDICATORS = [
  { key: 'teaching_process_management', label: '教学过程管理', maxScore: 15 },
  { key: 'course_construction', label: '课程建设', maxScore: 15 },
  { key: 'teaching_reform_projects', label: '教学改革项目', maxScore: 20 },
  { key: 'honorary_awards', label: '荣誉表彰', maxScore: 15 },
  { key: 'teaching_quality', label: '教学质量', maxScore: 15 },
  { key: 'student_guidance', label: '学生指导', maxScore: 10 },
  { key: 'scientific_research', label: '科研工作', maxScore: 5 },
  { key: 'team_building', label: '团队建设', maxScore: 5 }
] as const;

export const TOTAL_MAX_SCORE = EVALUATION_INDICATORS.reduce((sum, ind) => sum + ind.maxScore, 0);
