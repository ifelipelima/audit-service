from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.audit_event import AuditEvent

if TYPE_CHECKING:
    from app.models.audit_event import AuditEvent

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    slug: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True,
        nullable=False
    )

    api_key_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )

    events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="application",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )