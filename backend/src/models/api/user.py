from uuid import UUID

import models.base


class UserGet(models.base.PydanticModelBase):
    id: UUID
    username : str
    tag_uuids: list[str] = []
    email : str | None = None
    date_created : str | None
    last_name: str | None


class UserCreate(models.base.PydanticModelBase):
    email: str | None = None
    username : str


class UserUpdate(models.base.PydanticModelBase):
    email: str | None = None
    username : str | None = None
    tag_uuids: list[str] | None = None
