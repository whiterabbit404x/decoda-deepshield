from __future__ import annotations

from sqlalchemy import Column, Index, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class Organization(UUIDTimestampMixin, Base):
    __tablename__ = "organizations"
    __table_args__ = (Index("ix_organizations_created_at", "created_at"),)

    organization_id = uuid_pk("organization_id")
    name = Column(String, nullable=False, index=True)

    users = relationship("User", back_populates="organization")
    workspaces = relationship("Workspace", back_populates="organization")
