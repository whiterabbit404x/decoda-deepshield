from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = (
        Index("ix_evidence_workspace_uploaded", "workspace_id", "uploaded_at"),
    )

    evidence_id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.organization_id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.workspace_id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    source = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    workspace = relationship("Workspace", back_populates="evidence_items")
    detections = relationship("Detection", back_populates="evidence")
    alerts = relationship("Alert", back_populates="evidence")
    incidents = relationship("Incident", back_populates="evidence")
