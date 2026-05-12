from __future__ import annotations

import hashlib
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app, startup
from app.models import Alert, AnalysisJob, AuditEvent, Evidence, Incident
from app.repositories import DBRepository
from app.storage import LocalEvidenceStorage

WORKSPACE_ID = DBRepository.DEFAULT_WORKSPACE_ID
WORKSPACE_HEADERS = {"X-Workspace-Id": WORKSPACE_ID}
WORKSPACE_B_ID = "00000000-0000-0000-0000-0000000000b2"
WORKSPACE_B_HEADERS = {"X-Workspace-Id": WORKSPACE_B_ID}


@pytest.fixture()
def client(tmp_path, monkeypatch) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test_api.sqlite3"
    uploads_dir = tmp_path / "uploads"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    class TempDirStorage(LocalEvidenceStorage):
        def __init__(self, _ignored: Path):
            super().__init__(uploads_dir)

    monkeypatch.setattr("app.main.LocalEvidenceStorage", TempDirStorage)

    startup()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _db_session() -> Session:
    db_gen = app.dependency_overrides[get_db]()
    return next(db_gen)


def _upload_and_analyze_until_level(
    test_client: TestClient, levels: set[str], headers: dict[str, str] = WORKSPACE_HEADERS
) -> tuple[dict, dict]:
    for idx in range(250):
        upload_resp = test_client.post(
            "/evidence/upload",
            json={"filename": f"sample-{idx}.mp4"},
            headers=headers,
        )
        assert upload_resp.status_code == 200
        upload = upload_resp.json()

        analysis = test_client.post(
            "/detections/analyze",
            json={"evidence_id": upload["evidence_id"]},
            headers=headers,
        )
        assert analysis.status_code == 200
        payload = analysis.json()
        if payload["risk_level"] in levels:
            return upload, payload
    raise AssertionError(f"Could not produce risk level in {levels}")


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "deepshield-api"}


def test_multipart_upload_hash_persistence_and_storage_metadata(client: TestClient) -> None:
    payload = b"deep-shield-evidence-content"
    expected_hash = hashlib.sha256(payload).hexdigest()

    response = client.post(
        "/evidence/upload",
        files={"file": ("camera-feed.mp4", payload, "video/mp4")},
        headers=WORKSPACE_HEADERS,
    )

    assert response.status_code == 200
    uploaded = response.json()
    assert uploaded["original_filename"] == "camera-feed.mp4"
    assert uploaded["storage_backend"] == "local"
    assert uploaded["file_size_bytes"] == len(payload)
    assert uploaded["sha256_hash"] == expected_hash
    assert Path(uploaded["storage_path"]).exists()

    db = _db_session()
    try:
        evidence = db.query(Evidence).filter(Evidence.evidence_id == uploaded["evidence_id"]).one()
        assert evidence.sha256_hash == expected_hash
        assert evidence.storage_backend == "local"
        assert evidence.file_size_bytes == len(payload)
        assert Path(evidence.storage_path).read_bytes() == payload
    finally:
        db.close()


def test_end_to_end_chain_and_runtime_status(client: TestClient) -> None:
    upload, detection = _upload_and_analyze_until_level(client, {"medium", "high"})

    assert upload["evidence_id"]
    assert "uploaded_at" in upload

    for key in [
        "evidence_id",
        "synthetic_risk_score",
        "risk_level",
        "reason_codes",
        "recommended_action",
        "created_at",
        "decision_support_disclaimer",
        "simulated_model_version",
    ]:
        assert key in detection

    alerts_resp = client.get("/alerts", headers=WORKSPACE_HEADERS)
    incidents_resp = client.get("/incidents", headers=WORKSPACE_HEADERS)
    assert alerts_resp.status_code == 200
    assert incidents_resp.status_code == 200

    alerts_payload = alerts_resp.json()
    incidents_payload = incidents_resp.json()
    assert len(alerts_payload) == 1
    assert len(incidents_payload) == 1

    alert = alerts_payload[0]
    incident = incidents_payload[0]
    assert alert["evidence_id"] == upload["evidence_id"]
    assert incident["evidence_id"] == upload["evidence_id"]
    assert incident["alert_id"] == alert["alert_id"]

    export_resp = client.get(f"/evidence/{upload['evidence_id']}/export", headers=WORKSPACE_HEADERS)
    assert export_resp.status_code == 200
    exported = export_resp.json()
    assert exported["evidence_id"] == upload["evidence_id"]
    assert exported["detection_result"]["evidence_id"] == upload["evidence_id"]
    assert exported["related_alert"]["alert_id"] == alert["alert_id"]
    assert exported["related_incident"]["incident_id"] == incident["incident_id"]

    runtime_resp = client.get("/runtime/status", headers=WORKSPACE_HEADERS)
    assert runtime_resp.status_code == 200
    runtime = runtime_resp.json()
    assert runtime["api_status"] == "ok"
    assert runtime["database_status"] == "ok"
    assert runtime["evidence_count"] >= 1
    assert runtime["detection_count"] >= 1
    assert runtime["alert_count"] == 1
    assert runtime["incident_count"] == 1


def test_workspace_isolation_across_upload_analyze_and_export(client: TestClient) -> None:
    upload_a, _ = _upload_and_analyze_until_level(client, {"medium", "high"}, headers=WORKSPACE_HEADERS)

    upload_b_resp = client.post(
        "/evidence/upload",
        json={"filename": "workspace-b.mp4"},
        headers=WORKSPACE_B_HEADERS,
    )
    assert upload_b_resp.status_code == 200
    upload_b_id = upload_b_resp.json()["evidence_id"]

    analyze_b_resp = client.post(
        "/detections/analyze",
        json={"evidence_id": upload_b_id},
        headers=WORKSPACE_B_HEADERS,
    )
    assert analyze_b_resp.status_code == 200

    assert len(client.get("/alerts", headers=WORKSPACE_HEADERS).json()) == 1
    assert client.get("/alerts", headers=WORKSPACE_B_HEADERS).status_code == 200

    cross_scope_analyze = client.post(
        "/detections/analyze",
        json={"evidence_id": upload_a["evidence_id"]},
        headers=WORKSPACE_B_HEADERS,
    )
    assert cross_scope_analyze.status_code == 404

    own_export = client.get(f"/evidence/{upload_a['evidence_id']}/export", headers=WORKSPACE_HEADERS)
    assert own_export.status_code == 200
    foreign_export = client.get(f"/evidence/{upload_a['evidence_id']}/export", headers=WORKSPACE_B_HEADERS)
    assert foreign_export.status_code == 404


def test_low_risk_does_not_create_alert_or_incident(client: TestClient) -> None:
    _upload_and_analyze_until_level(client, {"low"})
    assert client.get("/alerts", headers=WORKSPACE_HEADERS).json() == []
    assert client.get("/incidents", headers=WORKSPACE_HEADERS).json() == []


def test_audit_events_include_required_types(client: TestClient) -> None:
    upload, _ = _upload_and_analyze_until_level(client, {"medium", "high"})
    export_resp = client.get(f"/evidence/{upload['evidence_id']}/export", headers=WORKSPACE_HEADERS)
    assert export_resp.status_code == 200

    db = _db_session()
    try:
        evidence = db.query(Evidence).filter(Evidence.evidence_id == uploaded["evidence_id"]).one()
        assert evidence.sha256_hash == expected_hash
        assert evidence.storage_backend == "local"
        assert evidence.file_size_bytes == len(payload)
        assert Path(evidence.storage_path).read_bytes() == payload
    finally:
        db.close()


def test_workspace_isolation_and_scoped_entities(client: TestClient) -> None:
    upload_a, _ = _upload_and_analyze_until_level(client, {"medium", "high"}, WORKSPACE_HEADERS)
    upload_b = client.post(
        "/evidence/upload",
        json={"filename": "workspace-b.mp4"},
        headers=WORKSPACE_B_HEADERS,
    )
    assert upload_b.status_code == 200
    upload_b_id = upload_b.json()["evidence_id"]

    assert client.get("/alerts", headers=WORKSPACE_HEADERS).status_code == 200
    assert len(client.get("/alerts", headers=WORKSPACE_HEADERS).json()) == 1
    assert client.get("/alerts", headers=WORKSPACE_B_HEADERS).json() == []

    analyze_b = client.post("/detections/analyze", json={"evidence_id": upload_b_id}, headers=WORKSPACE_B_HEADERS)
    assert analyze_b.status_code == 200

    db = _db_session()
    try:
        events = db.query(AuditEvent).filter(AuditEvent.workspace_id == WORKSPACE_ID).all()
    finally:
        db.close()

    hashed_event = next(event for event in events if event.event_type == "evidence_file_hashed")
    job_event = next(event for event in events if event.event_type == "analysis_job_created")

    assert hashed_event.metadata_json["evidence_id"] == upload["evidence_id"]
    assert hashed_event.metadata_json["workspace_id"] == WORKSPACE_ID
    assert "sha256_hash" in hashed_event.metadata_json

    assert job_event.metadata_json["job_id"] == job_event.entity_id
    assert job_event.metadata_json["evidence_id"] == upload["evidence_id"]
    assert job_event.metadata_json["workspace_id"] == WORKSPACE_ID


def test_export_package_integrity_and_scoped_records(client: TestClient) -> None:
    upload, detection = _upload_and_analyze_until_level(client, {"medium", "high"})

    export_resp = client.get(f"/evidence/{upload['evidence_id']}/export", headers=WORKSPACE_HEADERS)
    assert export_resp.status_code == 200
    exported = export_resp.json()

    assert exported["evidence_id"] == upload["evidence_id"]
    assert exported["detection_result"]["evidence_id"] == upload["evidence_id"]
    assert exported["detection_result"]["risk_level"] == detection["risk_level"]
    assert exported["related_alert"]["evidence_id"] == upload["evidence_id"]
    assert exported["related_incident"]["evidence_id"] == upload["evidence_id"]

    db = _db_session()
    try:
        assert db.query(Alert).filter(Alert.evidence_id == upload["evidence_id"], Alert.workspace_id == WORKSPACE_ID).count() == 1
        assert db.query(Incident).filter(Incident.evidence_id == upload["evidence_id"], Incident.workspace_id == WORKSPACE_ID).count() == 1
        assert db.query(AnalysisJob).filter(
            AnalysisJob.evidence_id == upload["evidence_id"], AnalysisJob.workspace_id == WORKSPACE_ID
        ).count() >= 1
    finally:
        db.close()


def test_persistence_across_repository_sessions(client: TestClient) -> None:
    upload, _ = _upload_and_analyze_until_level(client, {"medium", "high"})

    db1 = _db_session()
    try:
        repo1 = DBRepository(db1)
        assert repo1.get_evidence(upload["evidence_id"], workspace_id=WORKSPACE_ID) is not None
    finally:
        db1.close()

    db2 = _db_session()
    try:
        assert db.query(Alert).filter(Alert.evidence_id == upload["evidence_id"], Alert.workspace_id == WORKSPACE_ID).count() == 1
        assert db.query(Incident).filter(Incident.evidence_id == upload["evidence_id"], Incident.workspace_id == WORKSPACE_ID).count() == 1
        assert db.query(AnalysisJob).filter(AnalysisJob.evidence_id == upload["evidence_id"], AnalysisJob.workspace_id == WORKSPACE_ID).count() >= 1
    finally:
        db.close()
