// Self-evaluation form types
export interface SelfEvaluationContent {
  teachingProcessManagement: string;
  courseConstruction: string;
  teachingReformProjects: number;
  honoraryAwards: number;
  teachingQuality: string;
  studentGuidance: string;
  scientificResearch: string;
  teamBuilding: string;
}

export interface SelfEvaluation {
  id?: string;
  teachingOfficeId: string;
  evaluationYear: number;
  content: SelfEvaluationContent;
  status: 'draft' | 'submitted' | 'locked' | 'ai_scored' | 'manually_scored' | 'ready_for_final' | 'finalized' | 'published';
  submittedAt?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface SelfEvaluationFormData {
  teachingOfficeId: string;
  evaluationYear: number;
  content: SelfEvaluationContent;
}
