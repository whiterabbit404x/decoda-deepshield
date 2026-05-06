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

export interface EvidenceUploadResponse {
  upload_id?: string;
  filename?: string;
  status: string;
  message?: string;
}

export interface DetectionOutput {
  id?: string;
  label: string;
  confidence?: number;
  score?: number;
  details?: string;
  created_at?: string;
}

export interface AnalyzeDetectionResponse {
  status?: string;
  detections: DetectionOutput[];
  summary?: string;
}
