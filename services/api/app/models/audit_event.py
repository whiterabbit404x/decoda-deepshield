from __future__ import annotations

from sqlalchemy import JSON, Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class AuditEvent(UUIDTimestampMixin, Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        Index("ix_audit_events_workspace_created", "workspace_id", "created_at"),
        Index("ix_audit_events_event_created", "event_type", "created_at"),
        Index("ix_audit_events_entity", "entity_type", "entity_id"),
    )

    audit_event_id = uuid_pk("audit_event_id")
    workspace_id = Column(String(36), ForeignKey("workspaces.workspace_id"), nullable=False, index=True)
    actor_id = Column(String(36), ForeignKey("users.user_id"), nullable=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)
    metadata_json = Column(JSON, nullable=True)

    actor = relationship("User", back_populates="audit_events")
