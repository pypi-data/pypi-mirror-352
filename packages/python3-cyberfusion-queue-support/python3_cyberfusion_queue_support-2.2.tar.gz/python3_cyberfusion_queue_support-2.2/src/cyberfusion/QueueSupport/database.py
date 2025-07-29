from alembic.config import Config
from alembic import command
import sqlite3
from datetime import datetime, timezone
from sqlalchemy.pool.base import _ConnectionRecord
from sqlalchemy import ForeignKey, MetaData, Boolean
from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.orm import Session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.types import JSON

from cyberfusion.QueueSupport.settings import settings


@event.listens_for(Engine, "connect")  # type: ignore[misc]
def set_sqlite_pragma(
    dbapi_connection: sqlite3.Connection, connection_record: _ConnectionRecord
) -> None:
    """Enable foreign key support.

    This is needed for cascade deletes to work.

    See https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys
    """
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


def run_migrations() -> None:
    """Upgrade database schema to latest version."""
    alembic_config = Config(file_=settings.alembic_config_file_path)
    alembic_config.set_main_option("sqlalchemy.url", settings.database_path)

    command.upgrade(alembic_config, "head")


def make_database_session() -> Session:
    engine = create_engine(
        settings.database_path, connect_args={"check_same_thread": False}
    )

    return sessionmaker(bind=engine)()


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

Base = declarative_base(metadata=metadata)


class BaseModel(Base):  # type: ignore[misc, valid-type]
    """Base model."""

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)


class Queue(BaseModel):
    """Queue model."""

    __tablename__ = "queues"


class QueueProcess(BaseModel):
    """QueueProcess model."""

    __tablename__ = "queue_processes"

    queue_id = Column(Integer, ForeignKey("queues.id"), nullable=False)
    queue = relationship("Queue")
    preview = Column(Boolean, nullable=False)


class QueueItem(BaseModel):
    """QueueItem model."""

    __tablename__ = "queue_items"

    queue_id = Column(Integer, ForeignKey("queues.id"), nullable=False)
    queue = relationship("Queue")
    type = Column(String(length=255), nullable=False)
    reference = Column(String(length=255), nullable=True)
    hide_outcomes = Column(Boolean, nullable=False)
    deduplicated = Column(Boolean, nullable=False)
    attributes = Column(JSON, nullable=False)


class QueueItemOutcome(BaseModel):
    """QueueItemOutcome model."""

    __tablename__ = "queue_item_outcomes"

    queue_item_id = Column(Integer, ForeignKey("queue_items.id"), nullable=False)
    queue_item = relationship("QueueItem")
    queue_process_id = Column(Integer, ForeignKey("queue_processes.id"), nullable=False)
    queue_process = relationship("QueueProcess")
    type = Column(String(length=255), nullable=False)
    attributes = Column(JSON, nullable=False)
