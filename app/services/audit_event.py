from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.repositories.audit_event import AuditEventRepository
from app.schemas.audit_event import AuditEventCreate


class AuditEventConflictError(Exception):
    pass


class AuditEventNotFoundError(Exception):
    pass


def _same_content(event: AuditEvent, data: AuditEventCreate) -> bool:
    return (
        event.actor_id == data.actor_id
        and event.action == data.action
        and event.resource_type == data.resource_type
        and event.resource_id == data.resource_id
        and event.occurred_at == data.occurred_at
        and event.details == data.details
    )


class AuditEventService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AuditEventRepository(session)

    def register(
        self, application_id: UUID, data: AuditEventCreate
    ) -> tuple[AuditEvent, bool]:
        """Registra o evento. Retorna (evento, criado).

        Reenvio idêntico devolve o registro existente com criado=False (RN06);
        mesmo event_id com conteúdo diferente gera conflito (RN07).
        """
        existing = self.repository.get_by_event_id(application_id, data.event_id)
        if existing is not None:
            return self._resolve_duplicate(existing, data), False

        event = self.repository.create(application_id, data)

        try:
            self.session.commit()
        except IntegrityError:
            # Outra requisição concorrente gravou o mesmo event_id primeiro.
            self.session.rollback()
            existing = self.repository.get_by_event_id(application_id, data.event_id)
            if existing is None:
                raise
            return self._resolve_duplicate(existing, data), False

        self.session.refresh(event)
        return event, True

    def get(self, application_id: UUID, id: UUID) -> AuditEvent:
        event = self.repository.get_by_id(application_id, id)
        if event is None:
            raise AuditEventNotFoundError(id)
        return event

    @staticmethod
    def _resolve_duplicate(existing: AuditEvent, data: AuditEventCreate) -> AuditEvent:
        if not _same_content(existing, data):
            raise AuditEventConflictError(data.event_id)
        return existing
