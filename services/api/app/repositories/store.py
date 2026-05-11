from __future__ import annotations

from datetime import timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Alert, AuditEvent, Detection, Evidence, Incident
from app.schemas import MVP_DISCLAIMER, AlertRecord, DetectionResult, EvidenceRecord, IncidentRecord, utcnow_iso


class DBRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _iso(dt):
        return dt.astimezone(timezone.utc).isoformat() if dt else utcnow_iso()

    def create_evidence(self, record: EvidenceRecord) -> EvidenceRecord:
        evidence = Evidence(
            evidence_id=record.evidence_id,
            organization_id="default-org",
            workspace_id="default-workspace",
            filename=record.filename,
            content_type=record.content_type,
            source=record.source,
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return EvidenceRecord(
            evidence_id=evidence.evidence_id,
            filename=evidence.filename,
            content_type=evidence.content_type,
            source=evidence.source,
            uploaded_at=self._iso(evidence.uploaded_at),
        )

    def get_evidence(self, evidence_id: str) -> EvidenceRecord | None:
        evidence = self.db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
        if not evidence:
            return None
        return EvidenceRecord(
            evidence_id=evidence.evidence_id,
            filename=evidence.filename,
            content_type=evidence.content_type,
            source=evidence.source,
            uploaded_at=self._iso(evidence.uploaded_at),
        )

    def save_detection(self, result: DetectionResult) -> DetectionResult:
        detection = Detection(
            detection_id=str(uuid4()),
            evidence_id=result.evidence_id,
            synthetic_risk_score=result.synthetic_risk_score,
            risk_level=result.risk_level,
            reason_codes=result.reason_codes,
            recommended_action=result.recommended_action,
        )
        self.db.add(detection)
        self.db.commit()
        self.db.refresh(detection)
        return DetectionResult(
            evidence_id=detection.evidence_id,
            synthetic_risk_score=detection.synthetic_risk_score,
            risk_level=detection.risk_level,
            reason_codes=detection.reason_codes,
            recommended_action=detection.recommended_action,
            created_at=self._iso(detection.created_at),
            decision_support_disclaimer=MVP_DISCLAIMER,
        )

    def create_alert(self, alert: AlertRecord) -> AlertRecord:
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

    def list_alerts(self) -> list[AlertRecord]:
        alerts = self.db.query(Alert).order_by(Alert.created_at.desc()).all()
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

    def create_incident(self, incident: IncidentRecord) -> IncidentRecord:
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

    def list_incidents(self) -> list[IncidentRecord]:
        incidents = self.db.query(Incident).order_by(Incident.created_at.desc()).all()
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
        organization_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        workspace_id: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        event = AuditEvent(
            audit_event_id=str(uuid4()),
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata,
        )
        self.db.add(event)
        self.db.commit()

    def export_evidence_package(self, evidence_id: str) -> dict:
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            raise KeyError(evidence_id)

        detection = (
            self.db.query(Detection)
            .filter(Detection.evidence_id == evidence_id)
            .order_by(Detection.created_at.desc())
            .first()
        )
        alert = self.db.query(Alert).filter(Alert.evidence_id == evidence_id).order_by(Alert.created_at.desc()).first()
        incident = (
            self.db.query(Incident)
            .filter(Incident.evidence_id == evidence_id)
            .order_by(Incident.created_at.desc())
            .first()
        )

        return {
            "evidence_id": evidence_id,
            "detection_result": (
                DetectionResult(
                    evidence_id=detection.evidence_id,
                    synthetic_risk_score=detection.synthetic_risk_score,
                    risk_level=detection.risk_level,
                    reason_codes=detection.reason_codes,
                    recommended_action=detection.recommended_action,
                    created_at=self._iso(detection.created_at),
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
            "disclaimer": MVP_DISCLAIMER,
        }
