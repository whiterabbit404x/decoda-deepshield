export interface HealthResponse {
  status: string;
  service?: string;
  version?: string;
  timestamp?: string;
}

export interface Alert {
  alert_id: string;
  evidence_id: string;
  severity: "low" | "medium" | "high";
  synthetic_risk_score: number;
  reason_codes: string[];
  recommended_action: string;
  status: "open" | "closed";
  created_at: string;
}

export interface Incident {
  incident_id: string;
  alert_id: string;
  evidence_id: string;
  status: "open" | "investigating" | "resolved";
  priority: "medium" | "high";
  summary: string;
  created_at: string;
  audit_trail: string[];
}

export interface RuntimeStatus {
  api_status: string;
  database_status: string;
  evidence_count: number;
  detection_count: number;
  alert_count: number;
  incident_count: number;
  last_evidence_at: string | null;
  last_detection_at: string | null;
  last_alert_at: string | null;
  last_incident_at: string | null;
  last_sync_at: string | null;
  mode: "simulated_decision_support";
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
  simulated_model_version: string;
}

export type AnalyzeDetectionResponse = DetectionOutput;
