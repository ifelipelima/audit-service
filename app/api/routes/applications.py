from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import verify_admin_key
from app.db.session import get_db
from app.schemas.application import ApplicationCreate, ApplicationCreated
from app.services.application import ApplicationAlreadyExistsError, ApplicationService

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)

@router.post(
    "/",
    response_model=ApplicationCreated,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_admin_key)],
)
def create_application(
    data: ApplicationCreate,
    session: Annotated[Session, Depends(get_db)],
) -> ApplicationCreated:
    service = ApplicationService(session)

    try:
        application, api_key = service.create(data)
    except ApplicationAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Application with slug '{exc.args[0]}' already exists.",
        ) from exc

    return ApplicationCreated(
        id=application.id,
        name=application.name,
        slug=application.slug,
        created_at=application.created_at,
        api_key=api_key,
    ) 