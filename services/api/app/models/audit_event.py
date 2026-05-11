from __future__ import annotations

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_org_created", "organization_id", "created_at"),
        Index("ix_audit_events_entity", "entity_type", "entity_id"),
    )

    audit_event_id = Column(String, primary_key=True, index=True)
    organization_id = Column(String, ForeignKey("organizations.organization_id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.workspace_id"), nullable=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    user = relationship("User", back_populates="audit_events")
