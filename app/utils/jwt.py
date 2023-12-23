from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Union

import jwt
from fastapi import HTTPException

from settings import settings


class TokenType(Enum):
    ACCESS = 1
    REFRESH = 2


def create_jwt(data: dict, type: TokenType) -> bytes:
    to_encode = data.copy()

    # set expired timestamp
    # opting out from using match case because mypy still hasnt supported it
    if type == TokenType.ACCESS:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    if type == TokenType.REFRESH:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    # Use exp as the expiration date key
    # https://pyjwt.readthedocs.io/en/latest/usage.html#expiration-time-claim-exp
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


# A function that receive jwt token without the scheme prefix (Bearer)
# Then try to decode it
def decode_jwt(token: str) -> Union[Dict[str, Any], None]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": True, "verify_signature": True},
        )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token. {e}")
