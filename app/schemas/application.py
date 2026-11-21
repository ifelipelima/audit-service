from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class ApplicationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    created_at: datetime

class ApplicationCreated(ApplicationRead):
    api_key: str

