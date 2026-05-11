from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_evidence_created", "evidence_id", "created_at"),
        Index("ix_alerts_severity_created", "severity", "created_at"),
    )

    alert_id = Column(String, primary_key=True, index=True)
    evidence_id = Column(String, ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)
    synthetic_risk_score = Column(Integer, nullable=False)
    reason_codes = Column(JSON, nullable=False)
    recommended_action = Column(String, nullable=False)
    status = Column(String, nullable=False, default="open", index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    evidence = relationship("Evidence", back_populates="alerts")
    incidents = relationship("Incident", back_populates="alert")
