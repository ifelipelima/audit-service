from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import generate_api_key, hash_api_key
from app.models.application import Application
from app.repositories.application import ApplicationRepository
from app.schemas.application import ApplicationCreate


class ApplicationAlreadyExistsError(Exception):
    pass

class ApplicationService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ApplicationRepository(session)

    def create(self, data: ApplicationCreate) -> tuple[Application, str]:
        if self.repository.get_by_slug(data.slug):
            raise ApplicationAlreadyExistsError(data.slug)

        api_key = generate_api_key()
        application = self.repository.create(
            name=data.name,
            slug=data.slug,
            api_key_hash=hash_api_key(api_key),
        )

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            if self.repository.get_by_slug(data.slug):
                raise ApplicationAlreadyExistsError(data.slug) from exc
            raise

        self.session.refresh(application)
        return application, api_key