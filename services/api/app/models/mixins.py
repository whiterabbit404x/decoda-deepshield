from __future__ import annotations

from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import declared_attr, mapped_column


class UUIDTimestampMixin:
    @declared_attr
    def created_at(cls):
        return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    @declared_attr
    def updated_at(cls):
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        )


def uuid_pk(column_name: str):
    return mapped_column(column_name, String(36), primary_key=True, default=lambda: str(uuid4()))
