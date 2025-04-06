from datetime import datetime
from pydantic import Field

from src.common.schema import BaseSchema


class CreateTaskSchema(BaseSchema):
    title: str = Field(...)
    description: str | None = Field(None)
    priority: int = Field(...)

class UpdateTaskSchema(BaseSchema):
    title: str | None = Field(None)
    description: str | None = Field(None)
    priority: int | None = Field(None)
    # Флаг для ручного обновления статуса (опционально)
    is_completed: bool | None = Field(None)

class GetTaskSchema(BaseSchema):
    id: int
    title: str
    description: str | None
    priority: int
    is_completed: bool
    created_at: datetime
    updated_at: datetime
