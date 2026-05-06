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


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_detection_alert_and_incident_creation() -> None:
    reset_data()
    upload = client.post("/evidence/upload", json={"filename": "sample.mp4"}).json()
    analyze = client.post("/detections/analyze", json={"evidence_id": upload["evidence_id"]})
    assert analyze.status_code == 200
    payload = analyze.json()
    assert 0 <= payload["synthetic_risk_score"] <= 100
    assert payload["risk_level"] in ["low", "medium", "high"]

    alerts = client.get("/alerts").json()
    incidents = client.get("/incidents").json()
    if payload["risk_level"] in ["medium", "high"]:
        assert len(alerts) == 1
        assert len(incidents) == 1
    else:
        assert len(alerts) == 0
        assert len(incidents) == 0


def test_evidence_export() -> None:
    reset_data()
    upload = client.post("/evidence/upload", json={"filename": "proof.wav"}).json()
    client.post("/detections/analyze", json={"evidence_id": upload["evidence_id"]})

    exported = client.get(f"/evidence/{upload['evidence_id']}/export")
    assert exported.status_code == 200
    body = exported.json()
    assert body["evidence"]["evidence_id"] == upload["evidence_id"]
    assert len(body["detections"]) == 1
