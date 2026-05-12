from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Index, String

from app.db.base import Base
from app.models.mixins import UUIDTimestampMixin, uuid_pk


class APIKey(UUIDTimestampMixin, Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_workspace_created", "workspace_id", "created_at"),
        Index("ix_api_keys_workspace_status", "workspace_id", "status"),
        Index("ix_api_keys_workspace_prefix", "workspace_id", "key_prefix"),
    )

    api_key_id = uuid_pk("api_key_id")
    workspace_id = Column(String(36), ForeignKey("workspaces.workspace_id"), nullable=False, index=True)
    key_prefix = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active", index=True)
