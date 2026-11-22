from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.application import Application

class AuditEvent(Base):
    __tablename__ = "audit_events"

    __table_args__ = (
        UniqueConstraint("application_id", "event_id", name="uq_audit_events_application_event"),
        Index("ix_audit_events_application_ocurred_at", "application_id", "occurred_at"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    event_id: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="RESTRICT"),
        nullable=False
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True
    )

    action: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    resource_type: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    details: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    application: Mapped["Application"] = relationship(
        back_populates="events",
    )