from __future__ import annotations

from sqlalchemy import JSON, Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class Incident(UUIDTimestampMixin, Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_alert_created", "alert_id", "created_at"),
        Index("ix_incidents_priority_status", "priority", "status"),
    )

    incident_id = uuid_pk("incident_id")
    alert_id = Column(String(36), ForeignKey("alerts.alert_id"), nullable=False, index=True)
    evidence_id = Column(String(36), ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="open", index=True)
    priority = Column(String, nullable=False, default="medium", index=True)
    summary = Column(String, nullable=False)
    audit_trail = Column(JSON, nullable=False, default=list)

    alert = relationship("Alert", back_populates="incidents")
    evidence = relationship("Evidence", back_populates="incidents")
