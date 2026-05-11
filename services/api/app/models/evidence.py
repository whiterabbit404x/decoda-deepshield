from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class Evidence(UUIDTimestampMixin, Base):
    __tablename__ = "evidence"
    __table_args__ = (Index("ix_evidence_workspace_uploaded", "workspace_id", "created_at"),)

    evidence_id = uuid_pk("evidence_id")
    organization_id = Column(String(36), ForeignKey("organizations.organization_id"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.workspace_id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    source = Column(String, nullable=True)

    workspace = relationship("Workspace", back_populates="evidence_items")
    detections = relationship("Detection", back_populates="evidence")
    alerts = relationship("Alert", back_populates="evidence")
    incidents = relationship("Incident", back_populates="evidence")
