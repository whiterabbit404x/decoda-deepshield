from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.storage import JsonStore


client = TestClient(app)


def reset_data() -> None:
    data_dir = Path(__file__).resolve().parents[1] / "data"
    JsonStore(data_dir)
    for name in ["evidence", "detections", "alerts", "incidents"]:
        (data_dir / f"{name}.json").write_text("[]", encoding="utf-8")


def _upload_and_analyze_until_level(levels: set[str]) -> tuple[dict, dict]:
    for idx in range(250):
        upload = client.post("/evidence/upload", json={"filename": f"sample-{idx}.mp4"}).json()
        analysis = client.post("/detections/analyze", json={"evidence_id": upload["evidence_id"]})
        assert analysis.status_code == 200
        payload = analysis.json()
        if payload["risk_level"] in levels:
            return upload, payload
    raise AssertionError(f"Could not produce risk level in {levels}")


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "deepshield-api"}


def test_upload_analyze_alert_incident_and_lists() -> None:
    reset_data()
    upload, detection = _upload_and_analyze_until_level({"medium", "high"})

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
    ]:
        assert key in detection

    alerts = client.get("/alerts")
    incidents = client.get("/incidents")
    assert alerts.status_code == 200
    assert incidents.status_code == 200

    alerts_payload = alerts.json()
    incidents_payload = incidents.json()
    assert len(alerts_payload) == 1
    assert len(incidents_payload) == 1

    alert = alerts_payload[0]
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

    incident = incidents_payload[0]
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


def test_low_risk_does_not_create_alert_or_incident() -> None:
    reset_data()
    _upload_and_analyze_until_level({"low"})
    assert client.get("/alerts").json() == []
    assert client.get("/incidents").json() == []


def test_evidence_export_package_shape() -> None:
    reset_data()
    upload = client.post("/evidence/upload", json={"filename": "proof.wav"}).json()
    client.post("/detections/analyze", json={"evidence_id": upload["evidence_id"]})

    exported = client.get(f"/evidence/{upload['evidence_id']}/export")
    assert exported.status_code == 200
    body = exported.json()

    for key in [
        "evidence_id",
        "detection_result",
        "related_alert",
        "related_incident",
        "generated_at",
        "disclaimer",
    ]:
        assert key in body
    assert body["evidence_id"] == upload["evidence_id"]
    assert body["detection_result"]["evidence_id"] == upload["evidence_id"]
