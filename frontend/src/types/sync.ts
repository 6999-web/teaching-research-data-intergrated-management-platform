// Sync task status
export type SyncTaskStatus = 'pending' | 'syncing' | 'completed' | 'failed'

// Sync task interface
export interface SyncTask {
  id: string
  evaluation_ids: string[]
  status: SyncTaskStatus
  created_at: string
  completed_at?: string
  error_message?: string
}

// Sync request
export interface SyncToPresidentOfficeRequest {
  evaluation_ids: string[]
}

// Sync response
export interface SyncToPresidentOfficeResponse {
  sync_task_id: string
  status: SyncTaskStatus
}

// Evaluation for sync selection
export interface EvaluationForSync {
  id: string
  teaching_office_name: string
  evaluation_year: number
  status: string
  final_score?: number
  finalized_at?: string
  synced?: boolean
}
