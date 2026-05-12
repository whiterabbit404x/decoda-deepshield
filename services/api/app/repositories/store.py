from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Alert, AnalysisJob, AuditEvent, Detection, Evidence, Incident
from app.analyzers.metadata import MVP_DECISION_SUPPORT_DISCLAIMER, SIMULATED_ANALYZER_VERSION
from app.schemas import AlertRecord, DetectionResult, EvidenceRecord, IncidentRecord, utcnow_iso


class DBRepository:
    DEFAULT_ORGANIZATION_ID = "00000000-0000-0000-0000-000000000001"
    DEFAULT_WORKSPACE_ID = "00000000-0000-0000-0000-000000000001"
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _iso(dt):
        return dt.astimezone(timezone.utc).isoformat() if dt else utcnow_iso()

    def _add_audit_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        workspace_id: str,
        actor_id: str | None = None,
        metadata_json: dict | None = None,
    ) -> None:
        event_metadata = dict(metadata_json or {})
        event_metadata.setdefault("workspace_id", workspace_id)
        event = AuditEvent(
            audit_event_id=str(uuid4()),
            workspace_id=workspace_id,
            actor_id=actor_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=event_metadata,
        )
        self.db.add(event)

    def create_evidence(self, record: EvidenceRecord, workspace_id: str) -> EvidenceRecord:
        evidence = Evidence(
            evidence_id=record.evidence_id,
            organization_id=self.DEFAULT_ORGANIZATION_ID,
            workspace_id=workspace_id,
            filename=record.filename,
            original_filename=record.original_filename,
            content_type=record.content_type,
            source=record.source,
            storage_backend=record.storage_backend,
            storage_path=record.storage_path,
            file_size_bytes=record.file_size_bytes,
            sha256_hash=record.sha256_hash,
            ingestion_status=record.ingestion_status,
            analysis_status=record.analysis_status,
        )
        self.db.add(evidence)
        self._add_audit_event(
            event_type="evidence_uploaded",
            entity_type="evidence",
            entity_id=evidence.evidence_id,
            workspace_id=evidence.workspace_id,
            metadata_json={"evidence_id": evidence.evidence_id, "storage_path": evidence.storage_path},
        )
        if evidence.sha256_hash:
            self._add_audit_event(
                event_type="evidence_file_hashed",
                entity_type="evidence",
                entity_id=evidence.evidence_id,
                workspace_id=evidence.workspace_id,
                metadata_json={"evidence_id": evidence.evidence_id, "sha256_hash": evidence.sha256_hash},
            )
        self.db.commit()
        self.db.refresh(evidence)
        return EvidenceRecord(
            evidence_id=evidence.evidence_id,
            filename=evidence.filename,
            original_filename=evidence.original_filename,
            content_type=evidence.content_type,
            source=evidence.source,
            storage_backend=evidence.storage_backend,
            storage_path=evidence.storage_path,
            file_size_bytes=evidence.file_size_bytes,
            sha256_hash=evidence.sha256_hash,
            ingestion_status=evidence.ingestion_status,
            analysis_status=evidence.analysis_status,
            uploaded_at=self._iso(evidence.created_at),
        )

    def get_evidence(self, evidence_id: str, workspace_id: str) -> EvidenceRecord | None:
        evidence = (
            self.db.query(Evidence)
            .filter(Evidence.evidence_id == evidence_id, Evidence.workspace_id == workspace_id)
            .first()
        )
        if not evidence:
            return None
        return EvidenceRecord(
            evidence_id=evidence.evidence_id,
            filename=evidence.filename,
            original_filename=evidence.original_filename,
            content_type=evidence.content_type,
            source=evidence.source,
            storage_backend=evidence.storage_backend,
            storage_path=evidence.storage_path,
            file_size_bytes=evidence.file_size_bytes,
            sha256_hash=evidence.sha256_hash,
            ingestion_status=evidence.ingestion_status,
            analysis_status=evidence.analysis_status,
            uploaded_at=self._iso(evidence.created_at),
        )

    def save_detection(self, result: DetectionResult, workspace_id: str) -> DetectionResult:
        evidence = (
            self.db.query(Evidence)
            .filter(Evidence.evidence_id == result.evidence_id, Evidence.workspace_id == workspace_id)
            .first()
        )
        if not evidence:
            raise KeyError(result.evidence_id)
        detection = Detection(
            detection_id=str(uuid4()),
            evidence_id=result.evidence_id,
            synthetic_risk_score=result.synthetic_risk_score,
            risk_level=result.risk_level,
            reason_codes=result.reason_codes,
            recommended_action=result.recommended_action,
        )
        self.db.add(detection)
        self._add_audit_event(
            event_type="detection_generated",
            entity_type="detection",
            entity_id=detection.detection_id,
            workspace_id=workspace_id,
            metadata_json={"evidence_id": detection.evidence_id, "detection_id": detection.detection_id},
        )
        self.db.commit()
        self.db.refresh(detection)
        return DetectionResult(
            evidence_id=detection.evidence_id,
            synthetic_risk_score=detection.synthetic_risk_score,
            risk_level=detection.risk_level,
            reason_codes=detection.reason_codes,
            recommended_action=detection.recommended_action,
            created_at=self._iso(detection.created_at),
            analyzer_version=result.analyzer_version or SIMULATED_ANALYZER_VERSION,
            decision_support_disclaimer=result.decision_support_disclaimer or MVP_DECISION_SUPPORT_DISCLAIMER,
        )

    def create_analysis_job(self, evidence_id: str, workspace_id: str) -> AnalysisJob:
        job = AnalysisJob(
            job_id=str(uuid4()),
            evidence_id=evidence_id,
            workspace_id=workspace_id,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(job)
        self._add_audit_event(
            event_type="analysis_job_created",
            entity_type="analysis_job",
            entity_id=job.job_id,
            workspace_id=workspace_id,
            metadata_json={"job_id": job.job_id, "evidence_id": evidence_id},
        )
        self.db.commit()
        self.db.refresh(job)
        return job

    def complete_analysis_job(self, job_id: str, status: str, error_message: str | None = None) -> None:
        job = self.db.query(AnalysisJob).filter(AnalysisJob.job_id == job_id).first()
        if not job:
            return
        job.status = status
        job.completed_at = datetime.now(timezone.utc)
        if error_message is not None:
            job.error_message = error_message
        self.db.commit()

    def create_alert(self, alert: AlertRecord, workspace_id: str) -> AlertRecord:
        evidence = (
            self.db.query(Evidence)
            .filter(Evidence.evidence_id == alert.evidence_id, Evidence.workspace_id == workspace_id)
            .first()
        )
        if not evidence:
            raise KeyError(alert.evidence_id)
        db_alert = Alert(
            alert_id=alert.alert_id,
            evidence_id=alert.evidence_id,
            severity=alert.severity,
            synthetic_risk_score=alert.synthetic_risk_score,
            reason_codes=alert.reason_codes,
            recommended_action=alert.recommended_action,
            status=alert.status,
        )
        self.db.add(db_alert)
        self._add_audit_event(
            event_type="alert_created",
            entity_type="alert",
            entity_id=db_alert.alert_id,
            workspace_id=workspace_id,
            metadata_json={"evidence_id": db_alert.evidence_id, "alert_id": db_alert.alert_id},
        )
        self.db.commit()
        self.db.refresh(db_alert)
        return AlertRecord(
            alert_id=db_alert.alert_id,
            evidence_id=db_alert.evidence_id,
            severity=db_alert.severity,
            synthetic_risk_score=db_alert.synthetic_risk_score,
            reason_codes=db_alert.reason_codes,
            recommended_action=db_alert.recommended_action,
            status=db_alert.status,
            created_at=self._iso(db_alert.created_at),
        )

    def list_alerts(self, workspace_id: str) -> list[AlertRecord]:
        alerts = (
            self.db.query(Alert)
            .join(Evidence, Evidence.evidence_id == Alert.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .order_by(Alert.created_at.desc())
            .all()
        )
        return [
            AlertRecord(
                alert_id=a.alert_id,
                evidence_id=a.evidence_id,
                severity=a.severity,
                synthetic_risk_score=a.synthetic_risk_score,
                reason_codes=a.reason_codes,
                recommended_action=a.recommended_action,
                status=a.status,
                created_at=self._iso(a.created_at),
            )
            for a in alerts
        ]

    def create_incident(self, incident: IncidentRecord, workspace_id: str) -> IncidentRecord:
        evidence = (
            self.db.query(Evidence)
            .filter(Evidence.evidence_id == incident.evidence_id, Evidence.workspace_id == workspace_id)
            .first()
        )
        if not evidence:
            raise KeyError(incident.evidence_id)
        db_incident = Incident(
            incident_id=incident.incident_id,
            alert_id=incident.alert_id,
            evidence_id=incident.evidence_id,
            status=incident.status,
            priority=incident.priority,
            summary=incident.summary,
            audit_trail=incident.audit_trail,
        )
        self.db.add(db_incident)
        self._add_audit_event(
            event_type="incident_created",
            entity_type="incident",
            entity_id=db_incident.incident_id,
            workspace_id=workspace_id,
            metadata_json={
                "incident_id": db_incident.incident_id,
                "alert_id": db_incident.alert_id,
                "evidence_id": db_incident.evidence_id,
            },
        )
        self.db.commit()
        self.db.refresh(db_incident)
        return IncidentRecord(
            incident_id=db_incident.incident_id,
            alert_id=db_incident.alert_id,
            evidence_id=db_incident.evidence_id,
            status=db_incident.status,
            priority=db_incident.priority,
            summary=db_incident.summary,
            created_at=self._iso(db_incident.created_at),
            audit_trail=db_incident.audit_trail,
        )

    def list_incidents(self, workspace_id: str) -> list[IncidentRecord]:
        incidents = (
            self.db.query(Incident)
            .join(Evidence, Evidence.evidence_id == Incident.evidence_id)
            .filter(Evidence.workspace_id == workspace_id)
            .order_by(Incident.created_at.desc())
            .all()
        )
        return [
            IncidentRecord(
                incident_id=i.incident_id,
                alert_id=i.alert_id,
                evidence_id=i.evidence_id,
                status=i.status,
                priority=i.priority,
                summary=i.summary,
                created_at=self._iso(i.created_at),
                audit_trail=i.audit_trail,
            )
            for i in incidents
        ]

    def create_audit_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        workspace_id: str,
        actor_id: str | None = None,
        metadata_json: dict | None = None,
    ) -> None:
        self._add_audit_event(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            workspace_id=workspace_id,
            actor_id=actor_id,
            metadata_json=metadata_json,
        )
        self.db.commit()

    def export_evidence_package(self, evidence_id: str, workspace_id: str) -> dict:
        evidence = self.get_evidence(evidence_id, workspace_id)
        if not evidence:
            raise KeyError(evidence_id)

        detection = (
            self.db.query(Detection)
            .join(Evidence, Evidence.evidence_id == Detection.evidence_id)
            .filter(Detection.evidence_id == evidence_id, Evidence.workspace_id == workspace_id)
            .order_by(Detection.created_at.desc())
            .first()
        )
        alert = (
            self.db.query(Alert)
            .join(Evidence, Evidence.evidence_id == Alert.evidence_id)
            .filter(Alert.evidence_id == evidence_id, Evidence.workspace_id == workspace_id)
            .order_by(Alert.created_at.desc())
            .first()
        )
        incident = (
            self.db.query(Incident)
            .join(Evidence, Evidence.evidence_id == Incident.evidence_id)
            .filter(Incident.evidence_id == evidence_id, Evidence.workspace_id == workspace_id)
            .order_by(Incident.created_at.desc())
            .first()
        )

        self._add_audit_event(
            event_type="evidence_exported",
            entity_type="evidence",
            entity_id=evidence_id,
            workspace_id=workspace_id,
            metadata_json={
                "evidence_id": evidence_id,
                "detection_id": detection.detection_id if detection else None,
                "alert_id": alert.alert_id if alert else None,
                "incident_id": incident.incident_id if incident else None,
            },
        )
        self.db.commit()

        return {
            "evidence_id": evidence_id,
            "evidence": evidence.model_dump(),
            "detection_result": (
                DetectionResult(
                    evidence_id=detection.evidence_id,
                    synthetic_risk_score=detection.synthetic_risk_score,
                    risk_level=detection.risk_level,
                    reason_codes=detection.reason_codes,
                    recommended_action=detection.recommended_action,
                    created_at=self._iso(detection.created_at),
                    analyzer_version=SIMULATED_ANALYZER_VERSION,
                    decision_support_disclaimer=MVP_DECISION_SUPPORT_DISCLAIMER,
                ).model_dump()
                if detection
                else None
            ),
            "related_alert": (
                AlertRecord(
                    alert_id=alert.alert_id,
                    evidence_id=alert.evidence_id,
                    severity=alert.severity,
                    synthetic_risk_score=alert.synthetic_risk_score,
                    reason_codes=alert.reason_codes,
                    recommended_action=alert.recommended_action,
                    status=alert.status,
                    created_at=self._iso(alert.created_at),
                ).model_dump()
                if alert
                else None
            ),
            "related_incident": (
                IncidentRecord(
                    incident_id=incident.incident_id,
                    alert_id=incident.alert_id,
                    evidence_id=incident.evidence_id,
                    status=incident.status,
                    priority=incident.priority,
                    summary=incident.summary,
                    created_at=self._iso(incident.created_at),
                    audit_trail=incident.audit_trail,
                ).model_dump()
                if incident
                else None
            ),
            "generated_at": utcnow_iso(),
            "disclaimer": MVP_DECISION_SUPPORT_DISCLAIMER,
        }
