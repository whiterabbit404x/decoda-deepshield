from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List
from uuid import uuid4

from fastapi import UploadFile

from .schemas import MVP_DISCLAIMER, AlertRecord, DetectionResult, EvidenceRecord, IncidentRecord, utcnow_iso


class LocalEvidenceStorage:
    def __init__(self, uploads_dir: Path):
        self.uploads_dir = uploads_dir

    def persist_upload(self, upload: UploadFile) -> dict:
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

        original_name = Path(upload.filename or "upload.bin").name
        suffix = Path(original_name).suffix
        stored_name = f"{Path(original_name).stem}-{uuid4().hex}{suffix}"
        destination = self.uploads_dir / stored_name

        hasher = hashlib.sha256()
        total_size = 0

        with destination.open("wb") as out:
            while True:
                chunk = upload.file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                hasher.update(chunk)
                total_size += len(chunk)

        upload.file.close()

        return {
            "original_filename": original_name,
            "content_type": upload.content_type,
            "storage_backend": "local",
            "storage_path": str(destination),
            "file_size_bytes": total_size,
            "sha256_hash": hasher.hexdigest(),
        }


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

        detection = next((d for d in reversed(self._read("detections")) if d["evidence_id"] == evidence_id), None)
        alert = next((a for a in reversed(self._read("alerts")) if a["evidence_id"] == evidence_id), None)
        incident = next((i for i in reversed(self._read("incidents")) if i["evidence_id"] == evidence_id), None)

        return {
            "evidence_id": evidence_id,
            "detection_result": detection,
            "related_alert": alert,
            "related_incident": incident,
            "generated_at": utcnow_iso(),
            "disclaimer": MVP_DISCLAIMER,
        }
