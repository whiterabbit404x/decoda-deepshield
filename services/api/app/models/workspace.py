from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class Workspace(UUIDTimestampMixin, Base):
    __tablename__ = "workspaces"
    __table_args__ = (Index("ix_workspaces_org_created", "organization_id", "created_at"),)

    workspace_id = uuid_pk("workspace_id")
    organization_id = Column(String(36), ForeignKey("organizations.organization_id"), nullable=False, index=True)
    name = Column(String, nullable=False)

    organization = relationship("Organization", back_populates="workspaces")
    evidence_items = relationship("Evidence", back_populates="workspace")
