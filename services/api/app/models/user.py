from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_org_created", "organization_id", "created_at"),
    )

    user_id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.organization_id"), nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    organization = relationship("Organization", back_populates="users")
    audit_events = relationship("AuditEvent", back_populates="user")
