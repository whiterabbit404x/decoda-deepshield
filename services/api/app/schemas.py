from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


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


class AlertRecord(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    evidence_id: str
    risk_level: RiskLevel
    synthetic_risk_score: int
    status: Literal["open", "closed"] = "open"
    created_at: str = Field(default_factory=utcnow_iso)


class IncidentRecord(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid4()))
    alert_id: str
    evidence_id: str
    severity: RiskLevel
    title: str
    status: Literal["open", "investigating", "resolved"] = "open"
    created_at: str = Field(default_factory=utcnow_iso)
