from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field


RiskLevel = Literal["low", "medium", "high"]

MVP_DISCLAIMER = (
    "DeepShield MVP provides deterministic decision-support only. "
    "It does not perform real biometric identification, face recognition matching, "
    "or production fraud adjudication."
)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EvidenceRecord(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    original_filename: str | None = None
    content_type: str | None = None
    source: str | None = None
    storage_backend: str = "local"
    storage_path: str | None = None
    file_size_bytes: int = 0
    sha256_hash: str | None = None
    ingestion_status: str = "ingested"
    analysis_status: str = "pending"
    uploaded_at: str = Field(default_factory=utcnow_iso)


class UploadRequest(BaseModel):
    filename: str
    original_filename: str | None = None
    content_type: str | None = None
    source: str | None = None
    storage_backend: str = "test"
    storage_path: str | None = None
    file_size_bytes: int = 0
    sha256_hash: str | None = None
    ingestion_status: str = "ingested"
    analysis_status: str = "pending"


class UploadResponse(BaseModel):
    evidence_id: str
    uploaded_at: str
    original_filename: str | None = None
    storage_backend: str
    storage_path: str | None = None
    file_size_bytes: int
    sha256_hash: str | None = None
    ingestion_status: str
    analysis_status: str


class DetectionRequest(BaseModel):
    evidence_id: str


class DetectionResult(BaseModel):
    evidence_id: str
    synthetic_risk_score: int
    risk_level: RiskLevel
    reason_codes: List[str]
    recommended_action: str
    created_at: str = Field(default_factory=utcnow_iso)
    analyzer_version: str = "sim-hash-v1"
    decision_support_disclaimer: str = MVP_DISCLAIMER

    @computed_field(return_type=str)
    @property
    def simulated_model_version(self) -> str:
        """Backward-compatible alias for legacy API clients/tests."""
        return self.analyzer_version


class AlertRecord(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    evidence_id: str
    severity: RiskLevel
    synthetic_risk_score: int
    reason_codes: List[str]
    recommended_action: str
    status: Literal["open", "closed"] = "open"
    created_at: str = Field(default_factory=utcnow_iso)


class IncidentRecord(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid4()))
    alert_id: str
    evidence_id: str
    status: Literal["open", "investigating", "resolved"] = "open"
    priority: Literal["medium", "high"] = "medium"
    summary: str
    created_at: str = Field(default_factory=utcnow_iso)
    audit_trail: List[str] = Field(default_factory=list)
