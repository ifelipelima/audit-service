from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class AuditEventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1, max_length=120)
    actor_id: str | None = Field(default=None, min_length=1, max_length=120)
    action: str = Field(min_length=1, max_length=120)
    resource_type: str = Field(min_length=1, max_length=120)
    resource_id: str | None = Field(default=None, min_length=1, max_length=120)
    occurred_at: AwareDatetime
    details: dict[str, Any] | None = None


class AuditEventCreated(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: str
    created_at: datetime


class AuditEventFilters(BaseModel):
    actor_id: str | None = None
    action: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    occurred_from: AwareDatetime | None = None
    occurred_to: AwareDatetime | None = None


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: str
    actor_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    occurred_at: datetime
    details: dict[str, Any] | None
    created_at: datetime


class AuditEventPage(BaseModel):
    items: list[AuditEventRead]
    limit: int
    offset: int
