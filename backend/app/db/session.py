from __future__ import annotations

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()
connect_args = {'check_same_thread': False} if settings.database_url.startswith('sqlite') else {}
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _apply_compatible_schema_updates()


def _apply_compatible_schema_updates() -> None:
    """Apply small additive migrations needed by existing local databases."""
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if 'scraped_posts' not in tables:
        return

    columns = {column['name'] for column in inspector.get_columns('scraped_posts')}
    with engine.begin() as connection:
        if 'processed_at' not in columns:
            column_type = 'TIMESTAMP WITH TIME ZONE' if engine.dialect.name == 'postgresql' else 'DATETIME'
            connection.execute(text(f'ALTER TABLE scraped_posts ADD COLUMN processed_at {column_type} NULL'))
        connection.execute(text(
            'CREATE INDEX IF NOT EXISTS idx_scraped_posts_processed_at '
            'ON scraped_posts(processed_at)'
        ))
        if 'lead_candidates' in tables:
            connection.execute(text(
                'CREATE INDEX IF NOT EXISTS idx_lead_candidates_post_id '
                'ON lead_candidates(post_id)'
            ))
            connection.execute(text(
                'CREATE INDEX IF NOT EXISTS idx_lead_candidates_status '
                'ON lead_candidates(status)'
            ))
