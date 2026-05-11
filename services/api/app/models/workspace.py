from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (Index("ix_workspaces_org_created", "organization_id", "created_at"),)

    workspace_id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.organization_id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    organization = relationship("Organization", back_populates="workspaces")
    evidence_items = relationship("Evidence", back_populates="workspace")
