from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application


class ApplicationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_api_key_hash(self, api_key_hash: str) -> Application | None:
        stmt = select(Application).where(Application.api_key_hash == api_key_hash)
        return self.session.scalar(stmt)

    def get_by_slug(self, slug: str) -> Application | None:
        stmt = select(Application).where(Application.slug == slug)
        return self.session.scalar(stmt)

    def create(self, name: str, slug: str, api_key_hash: str) -> Application:
        application = Application(name=name, slug=slug, api_key_hash=api_key_hash)
        self.session.add(application)
        return application
        