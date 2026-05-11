from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class User(UUIDTimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_org_created", "organization_id", "created_at"),)

    user_id = uuid_pk("user_id")
    organization_id = Column(String(36), ForeignKey("organizations.organization_id"), nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=True)

    organization = relationship("Organization", back_populates="users")
    audit_events = relationship("AuditEvent", back_populates="user")
