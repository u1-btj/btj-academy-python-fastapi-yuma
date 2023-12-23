import datetime
import math
from typing import Annotated

from fastapi import Depends, HTTPException

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from db import get_session
from api.base.base_schemas import PaginationMetaResponse, PaginationParams
from models.user import User, UserSchema
from .schema import (
    UpdateUserRequest,
)

AsyncSession = Annotated[async_sessionmaker, Depends(get_session)]


class ReadAllUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        page_params: PaginationParams,
        include_deactivated: bool,
    ) -> (list[UserSchema], PaginationMetaResponse):
        async with self.async_session() as session:
            total_item = await session.execute(
                select(func.count())
                .select_from(User)
                .where(User.deactivated_at == None)
            )
            total_item = total_item.scalar()

            query = (
                select(User)
                .offset((page_params.page - 1) * page_params.item_per_page)
                .limit(page_params.item_per_page)
            )
            if not include_deactivated:
                query = query.filter(User.deactivated_at == None)

            paginated_query = await session.execute(query)
            paginated_query = paginated_query.scalars().all()

            users = [UserSchema.from_orm(p) for p in paginated_query]

            meta = PaginationMetaResponse(
                total_item=total_item,
                page=page_params.page,
                item_per_page=page_params.item_per_page,
                total_page=math.ceil(total_item / page_params.item_per_page),
            )

            return users, meta


class ReadUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id: int) -> UserSchema:
        async with self.async_session() as session:
            user = await session.execute(
                select(User).where(
                    (User.user_id == user_id).__and__(User.deactivated_at == None)
                )
            )
            user = user.scalars().first()
            if not user:
                raise HTTPException(status_code=404)
            return UserSchema.from_orm(user)


class UpdateUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, user_id: int, request: UpdateUserRequest) -> UserSchema:
        async with self.async_session.begin() as session:
            user = await session.execute(
                select(User).where(
                    (User.user_id == user_id).__and__(User.deactivated_at == None)
                )
            )
            user = user.scalars().first()
            if not user:
                raise HTTPException(status_code=404)

            username_is_modified = user.username != request.username
            if username_is_modified:
                u = await session.execute(
                    select(User).where(User.username == request.username)
                )
                u = u.scalars().first()
                if u is not None:
                    raise HTTPException(
                        400, f"username: {request.username} is already taken"
                    )

            email_is_modified = user.email != request.email
            if email_is_modified:
                u = await session.execute(
                    select(User).where(User.email == request.email)
                )
                u = u.scalars().first()
                if u is not None:
                    raise HTTPException(400, f"email: {request.email} is already taken")

            user.name = request.name
            user.username = request.username
            user.email = request.email
            user.updated_at = datetime.datetime.utcnow()
            user.updated_by = user_id

            await session.flush()
            return UserSchema.from_orm(user)


class DeactivateUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        user_id: int,
    ) -> UserSchema:
        async with self.async_session.begin() as session:
            user = await session.execute(
                select(User).where(
                    (User.user_id == user_id).__and__(User.deactivated_at == None)
                )
            )
            user = user.scalars().first()

            user.deactivated_at = datetime.datetime.utcnow()
            user.deactivated_by = user_id

            await session.flush()

            return UserSchema.from_orm(user)
