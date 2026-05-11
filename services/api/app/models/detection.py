from __future__ import annotations

from sqlalchemy import JSON, Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class Detection(UUIDTimestampMixin, Base):
    __tablename__ = "detections"
    __table_args__ = (
        Index("ix_detections_evidence_created", "evidence_id", "created_at"),
        Index("ix_detections_risk_created", "risk_level", "created_at"),
    )

    detection_id = uuid_pk("detection_id")
    evidence_id = Column(String(36), ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    synthetic_risk_score = Column(Integer, nullable=False, index=True)
    risk_level = Column(String, nullable=False, index=True)
    reason_codes = Column(JSON, nullable=False)
    recommended_action = Column(String, nullable=False)

    evidence = relationship("Evidence", back_populates="detections")
