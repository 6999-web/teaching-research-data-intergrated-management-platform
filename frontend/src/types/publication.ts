// Publication types for result publication and distribution

export interface PublishRequest {
  evaluation_ids: string[];
}

export interface PublishResponse {
  publication_id: string;
  published_at: string;
  message: string;
}

export interface PublicationDetail {
  id: string;
  evaluation_ids: string[];
  published_by: string;
  published_at: string;
  distributed_at?: string;
}

export interface DistributeRequest {
  publication_id: string;
}

export interface DistributeResponse {
  distributed_count: number;
  distributed_at: string;
  message: string;
}

export interface EvaluationForPublication {
  id: string;
  teaching_office_name: string;
  evaluation_year: number;
  status: string;
  final_score?: number;
  approved_at?: string;
}
