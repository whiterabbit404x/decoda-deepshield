from __future__ import annotations

from sqlalchemy import JSON, Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class AuditEvent(UUIDTimestampMixin, Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_org_created", "organization_id", "created_at"),
        Index("ix_audit_events_entity", "entity_type", "entity_id"),
    )

    audit_event_id = uuid_pk("audit_event_id")
    organization_id = Column(String(36), ForeignKey("organizations.organization_id"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.workspace_id"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)
    metadata = Column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_events")
