import datetime
from email.headerregistry import Group
from pydantic import BaseModel

from database.models.accounts import UserGroupEnum


class PatchUserRequestSchema(BaseModel):
    is_active: bool | None = None
    group: UserGroupEnum | None = None


class PatchUserResponseSchema(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    group: str

    model_config = {"from_attributes": True}
