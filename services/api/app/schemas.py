from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


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
    content_type: str | None = None
    source: str | None = None
    uploaded_at: str = Field(default_factory=utcnow_iso)


class UploadRequest(BaseModel):
    filename: str
    content_type: str | None = None
    source: str | None = None


class DetectionRequest(BaseModel):
    evidence_id: str


class DetectionResult(BaseModel):
    evidence_id: str
    synthetic_risk_score: int
    risk_level: RiskLevel
    reason_codes: List[str]
    recommended_action: str
    created_at: str = Field(default_factory=utcnow_iso)
    decision_support_disclaimer: str = MVP_DISCLAIMER


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
