from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException

from .detection import analyze_evidence
from .schemas import AlertRecord, DetectionRequest, EvidenceRecord, IncidentRecord, UploadRequest
from .storage import JsonStore

app = FastAPI(title="DeepShield API", version="0.1.0")
store = JsonStore(Path(__file__).resolve().parents[1] / "data")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "deepshield-api"}


@app.post("/evidence/upload")
def upload_evidence(payload: UploadRequest) -> dict:
    rec = store.create_evidence(EvidenceRecord(**payload.model_dump()))
    return {"evidence_id": rec.evidence_id, "uploaded_at": rec.uploaded_at}


@app.post("/detections/analyze")
def run_detection(payload: DetectionRequest) -> dict:
    evidence = store.get_evidence(payload.evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="evidence not found")

    detection = store.save_detection(analyze_evidence(payload.evidence_id))

    if detection.risk_level in {"medium", "high"}:
        alert = store.create_alert(
            AlertRecord(
                evidence_id=detection.evidence_id,
                risk_level=detection.risk_level,
                synthetic_risk_score=detection.synthetic_risk_score,
            )
        )
        store.create_incident(
            IncidentRecord(
                alert_id=alert.alert_id,
                evidence_id=detection.evidence_id,
                severity=detection.risk_level,
                title=f"Synthetic identity risk: {detection.risk_level}",
            )
        )

    return detection.model_dump()


@app.get("/alerts")
def list_alerts() -> list[dict]:
    return [a.model_dump() for a in store.list_alerts()]


@app.get("/incidents")
def list_incidents() -> list[dict]:
    return [i.model_dump() for i in store.list_incidents()]


@app.get("/evidence/{evidence_id}/export")
def export_evidence(evidence_id: str) -> dict:
    try:
        return store.export_evidence_package(evidence_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="evidence not found")
