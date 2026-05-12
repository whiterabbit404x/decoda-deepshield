from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class AnalysisJob(UUIDTimestampMixin, Base):
    __tablename__ = "analysis_jobs"
    __table_args__ = (
        Index("ix_analysis_jobs_evidence_created", "evidence_id", "created_at"),
        Index("ix_analysis_jobs_workspace_created", "workspace_id", "created_at"),
        Index("ix_analysis_jobs_status_created", "status", "created_at"),
    )

    job_id = uuid_pk("job_id")
    evidence_id = Column(String(36), ForeignKey("evidence.evidence_id"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.workspace_id"), nullable=False, index=True)
    status = Column(String, nullable=False, index=True, default="running")
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
