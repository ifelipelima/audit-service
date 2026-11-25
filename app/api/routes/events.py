from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_application
from app.db.session import get_db
from app.models.application import Application
from app.schemas.audit_event import (
    AuditEventCreate,
    AuditEventCreated,
    AuditEventFilters,
    AuditEventPage,
    AuditEventRead,
)
from app.services.audit_event import (
    AuditEventConflictError,
    AuditEventNotFoundError,
    AuditEventService,
    InvalidPeriodError,
)

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)

CurrentApplication = Annotated[Application, Depends(get_current_application)]
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=AuditEventCreated,
    status_code=status.HTTP_201_CREATED,
    responses={
        200: {"model": AuditEventCreated, "description": "Reenvio idêntico"},
        409: {"description": "event_id já usado com outro conteúdo"},
    },
)
def create_event(
    data: AuditEventCreate,
    response: Response,
    application: CurrentApplication,
    session: DbSession,
) -> AuditEventCreated:
    service = AuditEventService(session)

    try:
        event, created = service.register(application.id, data)
    except AuditEventConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Event '{exc.args[0]}' already exists with different content.",
        ) from exc

    if not created:
        response.status_code = status.HTTP_200_OK

    return AuditEventCreated.model_validate(event)


@router.get("", response_model=AuditEventPage)
def list_events(
    application: CurrentApplication,
    session: DbSession,
    filters: Annotated[AuditEventFilters, Query()],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> AuditEventPage:
    try:
        events = AuditEventService(session).list(
            application.id, filters, limit, offset
        )
    except InvalidPeriodError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="occurred_from must be before occurred_to.",
        ) from exc

    return AuditEventPage(
        items=[AuditEventRead.model_validate(event) for event in events],
        limit=limit,
        offset=offset,
    )


@router.get("/{id}", response_model=AuditEventRead)
def get_event(
    id: UUID,
    application: CurrentApplication,
    session: DbSession,
) -> AuditEventRead:
    try:
        event = AuditEventService(session).get(application.id, id)
    except AuditEventNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        ) from exc

    return AuditEventRead.model_validate(event)
