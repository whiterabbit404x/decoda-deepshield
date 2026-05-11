export interface HealthResponse {
  status: string;
  service?: string;
  version?: string;
  timestamp?: string;
}

export interface Alert {
  id: string;
  title: string;
  level: string;
  status?: string;
  source?: string;
  created_at?: string;
}

export interface Incident {
  id: string;
  title: string;
  severity?: string;
  status?: string;
  owner?: string;
  created_at?: string;
}

export interface RuntimeStatus {
  status?: string;
  last_sync_at?: string;
}

export interface EvidenceUploadResponse {
  evidence_id: string;
  uploaded_at: string;
}

export interface DetectionOutput {
  evidence_id: string;
  synthetic_risk_score: number;
  risk_level: "low" | "medium" | "high";
  reason_codes: string[];
  recommended_action: string;
  created_at: string;
  decision_support_disclaimer: string;
}

export type AnalyzeDetectionResponse = DetectionOutput;
