import datetime
from typing import Annotated
import bcrypt

from fastapi import Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from db import get_session
from middlewares.authentication import generate_access_token, generate_refresh_token
from models.user import User, UserSchema
from .schema import (
    RegisterRequest,
    LoginRequest,
    UserTokenSchema,
    ChangePasswordRequest,
)

AsyncSession = Annotated[async_sessionmaker, Depends(get_session)]


class Register:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(self, request: RegisterRequest) -> UserSchema:
        async with self.async_session.begin() as session:
            usr = await session.execute(
                select(User).where(User.username == request.username)
            )
            usr = usr.scalars().first()
            if usr is not None:
                raise HTTPException(
                    400, f"username: {request.username} is already taken"
                )

            usr = await session.execute(select(User).where(User.email == request.email))
            usr = usr.scalars().first()
            if usr is not None:
                raise HTTPException(400, f"email: {request.email} is already taken")

            pw_bytes = request.password.encode()
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(
                password=pw_bytes,
                salt=salt,
            )

            user = User()
            user.name = request.name
            user.email = request.email
            user.username = request.username
            user.password = hashed_pw.decode()
            user.created_at = datetime.datetime.utcnow()
            user.updated_at = datetime.datetime.utcnow()

            session.add(user)
            await session.flush()

            return UserSchema.from_orm(user)


class LoginUser:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        data: LoginRequest,
    ) -> UserTokenSchema:
        async with self.async_session() as session:
            user = await session.execute(
                select(User).where(
                    (
                        (User.username == data.username).__or__(
                            User.email == data.username
                        )
                    ).__and__(User.deactivated_at == None)
                )
            )
            user = user.scalars().first()
            if user is None:
                raise HTTPException(
                    401,
                    "login failed, make sure your credential are correct and try again",
                )
            password_matched = bcrypt.checkpw(
                password=data.password.encode(),
                hashed_password=user.password.encode(),
            )
            if not password_matched:
                raise HTTPException(
                    401,
                    "login failed, make sure your credential are correct and try again",
                )

            resp_data = UserTokenSchema.from_orm(user)
            resp_data.access_token = generate_access_token(user.user_id)
            resp_data.refresh_token = generate_refresh_token(user.user_id)

            return resp_data


class ChangePassword:
    def __init__(self, session: AsyncSession) -> None:
        self.async_session = session

    async def execute(
        self,
        data: ChangePasswordRequest,
        user_id: int,
    ) -> None:
        async with self.async_session.begin() as session:
            user = await session.execute(
                select(User).where(
                    (User.user_id == user_id).__and__(User.deactivated_at is None)
                )
            )
            user = user.scalars().first()
            if user is None:
                raise HTTPException(404, f"user with id: {user_id} does not exist")

            password_matched = bcrypt.checkpw(
                password=data.old_password.encode(),
                hashed_password=user.password.encode(),
            )
            if not password_matched:
                raise HTTPException(400, "incorrect password")

            pw_bytes = data.new_password.encode()
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(
                password=pw_bytes,
                salt=salt,
            )

            user.password = hashed_pw.decode()
            user.updated_at = datetime.datetime.utcnow()
            user.updated_by = user_id

            await session.flush()
