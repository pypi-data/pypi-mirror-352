import uuid
from uuid import UUID

from sqlalchemy import func
from typing_extensions import Optional

from fastapix.crud import Field, SQLModel
from fastapix.crud.mixins._typing import DATETIME, TIMESTAMP


class PkMixin(SQLModel):
    id: int = Field(default=None, title="ID", primary_key=True, nullable=False, create=False, update=False)


class PkMixinUUID(SQLModel):
    id: UUID = Field(default_factory=uuid.uuid4, title="ID", primary_key=True, nullable=False, create=False,
                     update=False)


class CreateTimeMixin(SQLModel):
    create_time: DATETIME = Field(default_factory=DATETIME.now, title="Create Time", create=False, update=False)


class UpdateTimeMixin(SQLModel):
    update_time: Optional[DATETIME] = Field(
        default_factory=DATETIME.now,
        title="Update Time",
        sa_column_kwargs={"onupdate": func.localtimestamp()},
        create=False,
        update=False
    )


class DeleteTimeMixin(SQLModel):
    delete_time: Optional[DATETIME] = Field(None, title="Delete Time", create=False)


class CUDTimeMixin(CreateTimeMixin, UpdateTimeMixin, DeleteTimeMixin):
    pass


class CreateTimeMixinTS(SQLModel):
    create_time: TIMESTAMP = Field(default_factory=TIMESTAMP.now, title="Create Time", create=False, update=False)


class UpdateTimeMixinTS(SQLModel):
    update_time: Optional[TIMESTAMP] = Field(
        default_factory=TIMESTAMP.now,
        title="Update Time",
        sa_column_kwargs={"onupdate": func.localtimestamp()},
        create=False,
        update=False
    )


class DeleteTimeMixinTS(SQLModel):
    delete_time: Optional[TIMESTAMP] = Field(None, title="Delete Time", create=False)


class CUDTimeMixinTS(CreateTimeMixinTS, UpdateTimeMixinTS, DeleteTimeMixinTS):
    pass
