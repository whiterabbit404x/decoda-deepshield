from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

import uvicorn
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .analyzers.base import EvidenceAnalyzer
from .analyzers.simulated import SimulatedEvidenceAnalyzer
from .models import Alert, AnalysisJob, Detection, Evidence, Incident, Organization, Workspace
from .repositories import DBRepository
from .storage import LocalEvidenceStorage
from .schemas import AlertRecord, DetectionRequest, EvidenceRecord, IncidentRecord, UploadRequest, UploadResponse

app = FastAPI(title="DeepShield API", version="0.1.0")


def get_workspace_id(
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-Id"),
    db: Session = Depends(get_db),
) -> str:
    if not x_workspace_id:
        raise HTTPException(status_code=400, detail="X-Workspace-Id header is required")
    try:
        UUID(x_workspace_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-Workspace-Id must be a valid UUID") from exc

    workspace = db.query(Workspace).filter(Workspace.workspace_id == x_workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="workspace not found")
    return x_workspace_id


def get_default_analyzer() -> EvidenceAnalyzer:
    return SimulatedEvidenceAnalyzer()


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
def runtime_status(workspace_id: str = Depends(get_workspace_id), db: Session = Depends(get_db)) -> dict:
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

        status["evidence_count"] = db.query(Evidence).filter(Evidence.workspace_id == workspace_id).count()
        status["detection_count"] = (
            db.query(Detection)
            .join(Evidence, Evidence.evidence_id == Detection.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .count()
        )
        status["alert_count"] = (
            db.query(Alert)
            .join(Evidence, Evidence.evidence_id == Alert.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .count()
        )
        status["incident_count"] = (
            db.query(Incident)
            .join(Evidence, Evidence.evidence_id == Incident.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .count()
        )

        latest_evidence = db.query(func.max(Evidence.created_at)).filter(Evidence.workspace_id == workspace_id).scalar()
        latest_detection = (
            db.query(func.max(Detection.created_at))
            .join(Evidence, Evidence.evidence_id == Detection.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .scalar()
        )
        latest_alert = (
            db.query(func.max(Alert.created_at))
            .join(Evidence, Evidence.evidence_id == Alert.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .scalar()
        )
        latest_incident = (
            db.query(func.max(Incident.created_at))
            .join(Evidence, Evidence.evidence_id == Incident.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .scalar()
        )

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
async def upload_evidence(
    request: Request,
    file: UploadFile | None = File(default=None),
    filename: str | None = Form(default=None),
    content_type: str | None = Form(default=None),
    source: str | None = Form(default=None),
    workspace_id: str = Depends(get_workspace_id),
    db: Session = Depends(get_db),
) -> UploadResponse:
    upload_filename = filename
    upload_content_type = content_type
    storage_metadata = {
        "storage_backend": "test",
        "storage_path": source,
        "file_size_bytes": 0,
        "sha256_hash": None,
    }

    # Backward-compatible JSON fallback for tests/non-multipart callers.
    if file is None and request.headers.get("content-type", "").startswith("application/json"):
        payload = UploadRequest(**(await request.json()))
        upload_filename = payload.filename
        upload_content_type = payload.content_type
        source = payload.source
        storage_metadata["storage_backend"] = payload.storage_backend
        storage_metadata["storage_path"] = payload.storage_path or payload.source
        storage_metadata["file_size_bytes"] = payload.file_size_bytes
        storage_metadata["sha256_hash"] = payload.sha256_hash

    if file is not None:
        storage = LocalEvidenceStorage(Path(__file__).resolve().parents[1] / "uploads")
        saved = storage.persist_upload(file)
        upload_filename = saved["original_filename"]
        upload_content_type = saved["content_type"] or upload_content_type
        storage_metadata = {
            "storage_backend": saved["storage_backend"],
            "storage_path": saved["storage_path"],
            "file_size_bytes": saved["file_size_bytes"],
            "sha256_hash": saved["sha256_hash"],
        }
    elif not upload_filename:
        raise HTTPException(status_code=422, detail="multipart file is required unless test metadata fallback is provided")

    rec = DBRepository(db).create_evidence(
        EvidenceRecord(
            filename=upload_filename,
            original_filename=(payload.original_filename if file is None and 'payload' in locals() else upload_filename),
            content_type=upload_content_type,
            source=source,
            storage_backend=storage_metadata["storage_backend"],
            storage_path=storage_metadata["storage_path"],
            file_size_bytes=storage_metadata["file_size_bytes"],
            sha256_hash=storage_metadata["sha256_hash"],
            ingestion_status=(payload.ingestion_status if file is None and 'payload' in locals() else "ingested"),
            analysis_status=(payload.analysis_status if file is None and 'payload' in locals() else "pending"),
        ),
        workspace_id=workspace_id,
    )
    return UploadResponse(
        evidence_id=rec.evidence_id,
        uploaded_at=rec.uploaded_at,
        original_filename=rec.original_filename,
        sha256_hash=rec.sha256_hash,
        storage_backend=rec.storage_backend,
        storage_path=rec.storage_path,
        file_size_bytes=rec.file_size_bytes,
        ingestion_status=rec.ingestion_status,
        analysis_status=rec.analysis_status,
    )


@app.post("/detections/analyze")
def run_detection(
    payload: DetectionRequest,
    workspace_id: str = Depends(get_workspace_id),
    db: Session = Depends(get_db),
    analyzer: EvidenceAnalyzer = Depends(get_default_analyzer),
) -> dict:
    repo = DBRepository(db)
    evidence = repo.get_evidence(payload.evidence_id, workspace_id=workspace_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="evidence not found")

    job = repo.create_analysis_job(evidence_id=evidence.evidence_id, workspace_id=workspace_id)

    try:
        detection = repo.save_detection(analyzer.analyze(evidence), workspace_id=workspace_id)

        if detection.risk_level in {"medium", "high"}:
            alert = repo.create_alert(
                AlertRecord(
                    evidence_id=detection.evidence_id,
                    severity=detection.risk_level,
                    synthetic_risk_score=detection.synthetic_risk_score,
                    reason_codes=detection.reason_codes,
                    recommended_action=detection.recommended_action,
                ),
                workspace_id=workspace_id,
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
                ),
                workspace_id=workspace_id,
            )

        repo.complete_analysis_job(job.job_id, status="completed")
    except Exception as exc:
        repo.complete_analysis_job(job.job_id, status="failed", error_message=str(exc))
        raise

    return detection.model_dump()


@app.get("/alerts")
def list_alerts(workspace_id: str = Depends(get_workspace_id), db: Session = Depends(get_db)) -> list[dict]:
    return [a.model_dump() for a in DBRepository(db).list_alerts(workspace_id=workspace_id)]


@app.get("/incidents")
def list_incidents(workspace_id: str = Depends(get_workspace_id), db: Session = Depends(get_db)) -> list[dict]:
    return [i.model_dump() for i in DBRepository(db).list_incidents(workspace_id=workspace_id)]


@app.get("/evidence/{evidence_id}/export")
def export_evidence(evidence_id: str, workspace_id: str = Depends(get_workspace_id), db: Session = Depends(get_db)) -> dict:
    try:
        return DBRepository(db).export_evidence_package(evidence_id, workspace_id=workspace_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="evidence not found")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
