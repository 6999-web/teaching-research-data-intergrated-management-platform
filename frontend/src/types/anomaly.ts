// Anomaly types for anomaly handling functionality

export interface AnomalyDetail {
  id: string;
  evaluation_id: string;
  type: 'count_mismatch' | 'missing_attachment' | 'invalid_data';
  indicator: string;
  declared_count?: number;
  parsed_count?: number;
  description: string;
  status: 'pending' | 'handled';
  handled_by?: string;
  handled_action?: 'reject' | 'correct';
  handled_at?: string;
}

export interface AnomalyListResponse {
  total: number;
  anomalies: AnomalyDetail[];
}

export interface HandleAnomalyRequest {
  anomaly_id: string;
  action: 'reject' | 'correct';
  corrected_data?: Record<string, any>;
  reject_reason?: string;
}

export interface HandleAnomalyResponse {
  anomaly_id: string;
  status: string;
  handled_at: string;
  message: string;
}

// Anomaly type labels
export const ANOMALY_TYPE_LABELS: Record<string, string> = {
  'count_mismatch': '数量不一致',
  'missing_attachment': '缺少附件',
  'invalid_data': '数据无效'
};

// Anomaly status labels
export const ANOMALY_STATUS_LABELS: Record<string, string> = {
  'pending': '待处理',
  'handled': '已处理'
};

// Anomaly action labels
export const ANOMALY_ACTION_LABELS: Record<string, string> = {
  'reject': '打回教研室',
  'correct': '直接修正'
};
