from __future__ import annotations

import os

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .detection import analyze_evidence
from .models import Alert, Detection, Evidence, Incident, Organization, Workspace
from .repositories import DBRepository
from .schemas import AlertRecord, DetectionRequest, EvidenceRecord, IncidentRecord, UploadRequest

app = FastAPI(title="DeepShield API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        if not db.query(Organization).filter(
            Organization.organization_id == DBRepository.DEFAULT_ORGANIZATION_ID
        ).first():
            db.add(
                Organization(
                    organization_id=DBRepository.DEFAULT_ORGANIZATION_ID,
                    name="Default Organization",
                )
            )
        if not db.query(Workspace).filter(
            Workspace.workspace_id == DBRepository.DEFAULT_WORKSPACE_ID
        ).first():
            db.add(
                Workspace(
                    workspace_id=DBRepository.DEFAULT_WORKSPACE_ID,
                    organization_id=DBRepository.DEFAULT_ORGANIZATION_ID,
                    name="Default Workspace",
                )
            )
        db.commit()
    finally:
        db.close()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "deepshield-api"}


@app.get("/runtime/status")
def runtime_status(db: Session = Depends(get_db)) -> dict:
    def _isoformat(value):
        return value.isoformat() if value else None

    status = {
        "api_status": "ok",
        "database_status": "degraded",
        "evidence_count": 0,
        "detection_count": 0,
        "alert_count": 0,
        "incident_count": 0,
        "last_evidence_at": None,
        "last_detection_at": None,
        "last_alert_at": None,
        "last_incident_at": None,
        "last_sync_at": None,
        "mode": "simulated_decision_support",
    }

    try:
        db.execute(text("SELECT 1"))
        status["database_status"] = "ok"

        status["evidence_count"] = db.query(Evidence).count()
        status["detection_count"] = db.query(Detection).count()
        status["alert_count"] = db.query(Alert).count()
        status["incident_count"] = db.query(Incident).count()

        latest_evidence = db.query(func.max(Evidence.created_at)).scalar()
        latest_detection = db.query(func.max(Detection.created_at)).scalar()
        latest_alert = db.query(func.max(Alert.created_at)).scalar()
        latest_incident = db.query(func.max(Incident.created_at)).scalar()

        status["last_evidence_at"] = _isoformat(latest_evidence)
        status["last_detection_at"] = _isoformat(latest_detection)
        status["last_alert_at"] = _isoformat(latest_alert)
        status["last_incident_at"] = _isoformat(latest_incident)

        sync_candidates = [latest_evidence, latest_detection, latest_alert, latest_incident]
        status["last_sync_at"] = _isoformat(max((ts for ts in sync_candidates if ts is not None), default=None))
    except SQLAlchemyError:
        status["api_status"] = "degraded"

    return status


@app.post("/evidence/upload")
def upload_evidence(payload: UploadRequest, db: Session = Depends(get_db)) -> dict:
    rec = DBRepository(db).create_evidence(EvidenceRecord(**payload.model_dump()))
    return {"evidence_id": rec.evidence_id, "uploaded_at": rec.uploaded_at}


@app.post("/detections/analyze")
def run_detection(payload: DetectionRequest, db: Session = Depends(get_db)) -> dict:
    repo = DBRepository(db)
    evidence = repo.get_evidence(payload.evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="evidence not found")

    detection = repo.save_detection(analyze_evidence(payload.evidence_id))

    if detection.risk_level in {"medium", "high"}:
        alert = repo.create_alert(
            AlertRecord(
                evidence_id=detection.evidence_id,
                severity=detection.risk_level,
                synthetic_risk_score=detection.synthetic_risk_score,
                reason_codes=detection.reason_codes,
                recommended_action=detection.recommended_action,
            )
        )
        repo.create_incident(
            IncidentRecord(
                alert_id=alert.alert_id,
                evidence_id=detection.evidence_id,
                priority="high" if detection.risk_level == "high" else "medium",
                summary=(
                    f"{detection.risk_level.title()} synthetic-risk evidence requires analyst review"
                ),
                audit_trail=[
                    "detection_result_generated",
                    "alert_auto_created",
                    "incident_auto_opened",
                ],
            )
        )

    return detection.model_dump()


@app.get("/alerts")
def list_alerts(db: Session = Depends(get_db)) -> list[dict]:
    return [a.model_dump() for a in DBRepository(db).list_alerts()]


@app.get("/incidents")
def list_incidents(db: Session = Depends(get_db)) -> list[dict]:
    return [i.model_dump() for i in DBRepository(db).list_incidents()]


@app.get("/evidence/{evidence_id}/export")
def export_evidence(evidence_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        return DBRepository(db).export_evidence_package(evidence_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="evidence not found")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
