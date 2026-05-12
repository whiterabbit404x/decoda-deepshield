from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, Integer, String
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
    original_filename = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    source = Column(String, nullable=True)
    storage_backend = Column(String, nullable=False, default="local")
    storage_path = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=False, default=0)
    sha256_hash = Column(String, nullable=True)
    ingestion_status = Column(String, nullable=False, default="ingested")
    analysis_status = Column(String, nullable=False, default="pending")

    workspace = relationship("Workspace", back_populates="evidence_items")
    detections = relationship("Detection", back_populates="evidence")
    alerts = relationship("Alert", back_populates="evidence")
    incidents = relationship("Incident", back_populates="evidence")
