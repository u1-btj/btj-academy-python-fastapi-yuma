from __future__ import annotations

import datetime

from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        "user_id",
        autoincrement=True,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column("name", nullable=False)
    email: Mapped[str] = mapped_column("email", nullable=False)
    username: Mapped[str] = mapped_column("username", nullable=False)
    password: Mapped[str] = mapped_column("password", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        "created_at",
        default=datetime.datetime.utcnow(),
        nullable=True,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        "updated_at",
        default=datetime.datetime.utcnow(),
        nullable=True,
    )
    deactivated_at: Mapped[datetime.datetime] = mapped_column(
        "deactivated_at",
        nullable=True,
    )
    created_by: Mapped[int] = mapped_column(
        "created_by",
        ForeignKey("users.user_id"),
        nullable=True,
    )
    updated_by: Mapped[int] = mapped_column(
        "updated_by",
        ForeignKey("users.user_id"),
        nullable=True,
    )
    deactivated_by: Mapped[int] = mapped_column(
        "deactivated_by",
        ForeignKey("users.user_id"),
        nullable=True,
    )


class UserSchema(BaseModel):
    user_id: int
    name: str
    email: str
    username: str
    _password: str
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None
    deactivated_at: datetime.datetime | None
    created_by: int | None
    updated_by: int | None
    deactivated_by: int | None

    class Config:
        orm_mode = True
        underscore_attrs_are_private = True
