from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import Settings

_engine: Engine | None = None


def init_engine(settings: Settings) -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    connect_args: dict = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    _engine = create_engine(
        settings.database_url,
        echo=False,
        future=True,
        connect_args=connect_args,
    )
    SQLModel.metadata.create_all(_engine)
    return _engine


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Database engine is not initialized. Call init_engine() first.")
    return _engine


def session_scope() -> Iterator[Session]:
    engine = get_engine()
    with Session(engine) as session:
        yield session


async def dispose_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
