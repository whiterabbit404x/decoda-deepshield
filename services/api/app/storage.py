from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .schemas import AlertRecord, DetectionResult, EvidenceRecord, IncidentRecord


class JsonStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.paths = {
            "evidence": self.data_dir / "evidence.json",
            "detections": self.data_dir / "detections.json",
            "alerts": self.data_dir / "alerts.json",
            "incidents": self.data_dir / "incidents.json",
        }
        self._ensure_files()

    def _ensure_files(self) -> None:
        for path in self.paths.values():
            if not path.exists():
                path.write_text("[]", encoding="utf-8")

    def _read(self, key: str) -> List[Dict]:
        return json.loads(self.paths[key].read_text(encoding="utf-8"))

    def _write(self, key: str, payload: List[Dict]) -> None:
        self.paths[key].write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def create_evidence(self, record: EvidenceRecord) -> EvidenceRecord:
        data = self._read("evidence")
        data.append(record.model_dump())
        self._write("evidence", data)
        return record

    def get_evidence(self, evidence_id: str) -> EvidenceRecord | None:
        for item in self._read("evidence"):
            if item["evidence_id"] == evidence_id:
                return EvidenceRecord(**item)
        return None

    def save_detection(self, result: DetectionResult) -> DetectionResult:
        data = self._read("detections")
        data.append(result.model_dump())
        self._write("detections", data)
        return result

    def create_alert(self, alert: AlertRecord) -> AlertRecord:
        data = self._read("alerts")
        data.append(alert.model_dump())
        self._write("alerts", data)
        return alert

    def list_alerts(self) -> List[AlertRecord]:
        return [AlertRecord(**a) for a in self._read("alerts")]

    def create_incident(self, incident: IncidentRecord) -> IncidentRecord:
        data = self._read("incidents")
        data.append(incident.model_dump())
        self._write("incidents", data)
        return incident

    def list_incidents(self) -> List[IncidentRecord]:
        return [IncidentRecord(**i) for i in self._read("incidents")]

    def export_evidence_package(self, evidence_id: str) -> Dict:
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            raise KeyError(evidence_id)

        detections = [d for d in self._read("detections") if d["evidence_id"] == evidence_id]
        alerts = [a for a in self._read("alerts") if a["evidence_id"] == evidence_id]
        incidents = [i for i in self._read("incidents") if i["evidence_id"] == evidence_id]

        return {
            "evidence": evidence.model_dump(),
            "detections": detections,
            "alerts": alerts,
            "incidents": incidents,
        }
