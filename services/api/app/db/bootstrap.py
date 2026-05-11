from __future__ import annotations

from app.db import Base, engine


def bootstrap_schema() -> None:
    """Create the initial SQL schema from SQLAlchemy metadata."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    bootstrap_schema()
