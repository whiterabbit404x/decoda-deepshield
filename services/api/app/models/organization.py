from __future__ import annotations

from sqlalchemy import Column, DateTime, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (Index("ix_organizations_created_at", "created_at"),)

    organization_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    users = relationship("User", back_populates="organization")
    workspaces = relationship("Workspace", back_populates="organization")
