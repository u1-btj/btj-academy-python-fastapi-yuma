from datetime import datetime, timedelta
from enum import Enum

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from settings import settings

algorithm = "HS256"


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


def generate_access_token(user_id: int) -> str:
    return jwt.encode(
        payload={
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "user_id": user_id,
            "token_type": TokenType.ACCESS.value,
        },
        key=settings.SECRET_KEY,
        algorithm=algorithm,
    )


def generate_refresh_token(user_id: int) -> str:
    return jwt.encode(
        payload={
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            "user_id": user_id,
            "token_type": TokenType.REFRESH.value,
        },
        key=settings.SECRET_KEY,
        algorithm=algorithm,
    )


def verify_token_type(payload: dict, token_type: TokenType) -> bool:
    str_token_type = payload.get("token_type")
    if str_token_type is None:
        return False

    actual_token_type = TokenType(str_token_type)
    if actual_token_type is not token_type:
        return False

    return True


scheme = HTTPBearer()


async def get_user_id_from_access_token(
    token: HTTPAuthorizationCredentials = Depends(scheme),
) -> int:
    credentials_exception = HTTPException(
        status_code=401,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[algorithm]
        )
    except jwt.ExpiredSignatureError as e:
        credentials_exception.detail = e.__str__()
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    token_type_matched = verify_token_type(
        payload=payload,
        token_type=TokenType.ACCESS,
    )
    if not token_type_matched:
        credentials_exception.detail = (
            f"mismatched token type, expecting token with type {TokenType.ACCESS.value}"
        )
        raise credentials_exception

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    return user_id


async def refresh_access_token(
    token: HTTPAuthorizationCredentials = Depends(scheme),
) -> (str, str):
    credentials_exception = HTTPException(
        status_code=401,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[algorithm]
        )
    except jwt.ExpiredSignatureError as e:
        credentials_exception.detail = e.__str__()
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    token_type_matched = verify_token_type(
        payload=payload,
        token_type=TokenType.REFRESH,
    )
    if not token_type_matched:
        credentials_exception.detail = f"mismatched token type, expecting token with type {TokenType.REFRESH.value}"
        raise credentials_exception

    user_id: int = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    return generate_access_token(user_id=user_id), generate_refresh_token(
        user_id=user_id
    )
