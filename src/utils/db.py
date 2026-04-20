"""Database utility helpers."""

from sqlalchemy import create_engine


def get_engine(db_url: str):
    """Create SQLAlchemy engine from database URL."""
    return create_engine(db_url, pool_pre_ping=True)
