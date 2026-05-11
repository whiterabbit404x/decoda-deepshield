from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_alert_created", "alert_id", "created_at"),
        Index("ix_incidents_priority_status", "priority", "status"),
    )

    incident_id = Column(String, primary_key=True, index=True)
    alert_id = Column(String, ForeignKey("alerts.alert_id"), nullable=False, index=True)
    evidence_id = Column(String, ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    status = Column(String, nullable=False, default="open", index=True)
    priority = Column(String, nullable=False, default="medium", index=True)
    summary = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    audit_trail = Column(JSON, nullable=False, default=list)

    alert = relationship("Alert", back_populates="incidents")
    evidence = relationship("Evidence", back_populates="incidents")
