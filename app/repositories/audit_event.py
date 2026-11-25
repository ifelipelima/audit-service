from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.schemas.audit_event import AuditEventCreate, AuditEventFilters


class AuditEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, application_id: UUID, data: AuditEventCreate) -> AuditEvent:
        event = AuditEvent(application_id=application_id, **data.model_dump())
        self.session.add(event)
        return event

    def get_by_event_id(self, application_id: UUID, event_id: str) -> AuditEvent | None:
        stmt = select(AuditEvent).where(
            AuditEvent.application_id == application_id,
            AuditEvent.event_id == event_id,
        )
        return self.session.scalar(stmt)

    def list(
        self,
        application_id: UUID,
        filters: AuditEventFilters,
        limit: int,
        offset: int,
    ) -> list[AuditEvent]:
        stmt = select(AuditEvent).where(AuditEvent.application_id == application_id)

        for field in ("actor_id", "action", "resource_type", "resource_id"):
            value = getattr(filters, field)
            if value is not None:
                stmt = stmt.where(getattr(AuditEvent, field) == value)

        if filters.occurred_from is not None:
            stmt = stmt.where(AuditEvent.occurred_at >= filters.occurred_from)
        if filters.occurred_to is not None:
            stmt = stmt.where(AuditEvent.occurred_at <= filters.occurred_to)

        stmt = (
            stmt.order_by(AuditEvent.occurred_at.desc(), AuditEvent.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(stmt))

    def get_by_id(self, application_id: UUID, id: UUID) -> AuditEvent | None:
        stmt = select(AuditEvent).where(
            AuditEvent.application_id == application_id,
            AuditEvent.id == id,
        )
        return self.session.scalar(stmt)
