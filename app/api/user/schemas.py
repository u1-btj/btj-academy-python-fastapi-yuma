from pydantic import BaseModel, Field, EmailStr
from api.base.base_schemas import BaseResponse, PaginationMetaResponse
from utils import REGEX_PASSWORD

from models.user import UserSchema


class ReadUserResponse(BaseResponse):
    data: UserSchema | None


class UserPaginationResponse(BaseModel):
    records: list[UserSchema]
    meta: PaginationMetaResponse


class ReadAllUserResponse(BaseResponse):
    data: UserPaginationResponse


class UpdateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=6, max_length=100)
    email: EmailStr


class UpdateUserResponse(BaseResponse):
    data: UserSchema | None


class ActivateDeactivateUserResponse(BaseResponse):
    data: UserSchema | None
