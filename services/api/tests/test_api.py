from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.session import get_db
from app.main import app, startup
from app.models import AuditEvent
from app.repositories import DBRepository


@pytest.fixture()
def client(tmp_path) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test_api.sqlite3"
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

    # Ensure required default org/workspace rows exist for this temp DB.
    startup()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def _upload_and_analyze_until_level(test_client: TestClient, levels: set[str]) -> tuple[dict, dict]:
    for idx in range(250):
        upload_resp = test_client.post("/evidence/upload", json={"filename": f"sample-{idx}.mp4"})
        assert upload_resp.status_code == 200
        upload = upload_resp.json()

        analysis = test_client.post("/detections/analyze", json={"evidence_id": upload["evidence_id"]})
        assert analysis.status_code == 200
        payload = analysis.json()
        if payload["risk_level"] in levels:
            return upload, payload
    raise AssertionError(f"Could not produce risk level in {levels}")


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "deepshield-api"}


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

    alerts_resp = client.get("/alerts")
    incidents_resp = client.get("/incidents")
    assert alerts_resp.status_code == 200
    assert incidents_resp.status_code == 200

    alerts_payload = alerts_resp.json()
    incidents_payload = incidents_resp.json()
    assert len(alerts_payload) == 1
    assert len(incidents_payload) == 1

    alert = alerts_payload[0]
    incident = incidents_payload[0]

    for key in [
        "alert_id",
        "evidence_id",
        "severity",
        "synthetic_risk_score",
        "reason_codes",
        "recommended_action",
        "created_at",
        "status",
    ]:
        assert key in alert

    for key in [
        "incident_id",
        "alert_id",
        "evidence_id",
        "status",
        "priority",
        "summary",
        "created_at",
        "audit_trail",
    ]:
        assert key in incident

    assert alert["evidence_id"] == upload["evidence_id"]
    assert incident["evidence_id"] == upload["evidence_id"]
    assert incident["alert_id"] == alert["alert_id"]

    export_resp = client.get(f"/evidence/{upload['evidence_id']}/export")
    assert export_resp.status_code == 200
    exported = export_resp.json()

    for key in [
        "evidence_id",
        "detection_result",
        "related_alert",
        "related_incident",
        "generated_at",
        "disclaimer",
    ]:
        assert key in exported

    assert exported["evidence_id"] == upload["evidence_id"]
    assert exported["detection_result"]["evidence_id"] == upload["evidence_id"]
    assert exported["related_alert"]["alert_id"] == alert["alert_id"]
    assert exported["related_incident"]["incident_id"] == incident["incident_id"]

    runtime_resp = client.get("/runtime/status")
    assert runtime_resp.status_code == 200
    runtime = runtime_resp.json()
    assert runtime["api_status"] == "ok"
    assert runtime["database_status"] == "ok"
    assert runtime["evidence_count"] >= 1
    assert runtime["detection_count"] >= 1
    assert runtime["alert_count"] == 1
    assert runtime["incident_count"] == 1
    assert runtime["last_evidence_at"]
    assert runtime["last_detection_at"]
    assert runtime["last_alert_at"]
    assert runtime["last_incident_at"]
    assert runtime["last_sync_at"]
    assert runtime["mode"] == "simulated_decision_support"


def test_low_risk_does_not_create_alert_or_incident(client: TestClient) -> None:
    _upload_and_analyze_until_level(client, {"low"})
    assert client.get("/alerts").json() == []
    assert client.get("/incidents").json() == []


def test_audit_events_include_required_types(client: TestClient) -> None:
    upload, _ = _upload_and_analyze_until_level(client, {"medium", "high"})
    export_resp = client.get(f"/evidence/{upload['evidence_id']}/export")
    assert export_resp.status_code == 200

    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    try:
        event_types = {event.event_type for event in db.query(AuditEvent).all()}
    finally:
        db.close()

    required = {
        "evidence_uploaded",
        "detection_generated",
        "alert_created",
        "incident_created",
        "evidence_exported",
    }
    assert required.issubset(event_types)


def test_persistence_across_repository_sessions(client: TestClient) -> None:
    upload, _ = _upload_and_analyze_until_level(client, {"medium", "high"})

    db1_gen = app.dependency_overrides[get_db]()
    db1 = next(db1_gen)
    try:
        repo1 = DBRepository(db1)
        assert repo1.get_evidence(upload["evidence_id"]) is not None
    finally:
        db1.close()

    db2_gen = app.dependency_overrides[get_db]()
    db2 = next(db2_gen)
    try:
        repo2 = DBRepository(db2)
        assert repo2.get_evidence(upload["evidence_id"]) is not None
        assert any(a.evidence_id == upload["evidence_id"] for a in repo2.list_alerts())
        assert any(i.evidence_id == upload["evidence_id"] for i in repo2.list_incidents())
    finally:
        db2.close()
