from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Detection(Base):
    __tablename__ = "detections"
    __table_args__ = (
        Index("ix_detections_evidence_created", "evidence_id", "created_at"),
        Index("ix_detections_risk_created", "risk_level", "created_at"),
    )

    detection_id = Column(String, primary_key=True, index=True)
    evidence_id = Column(String, ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    synthetic_risk_score = Column(Integer, nullable=False, index=True)
    risk_level = Column(String, nullable=False, index=True)
    reason_codes = Column(JSON, nullable=False)
    recommended_action = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    evidence = relationship("Evidence", back_populates="detections")
