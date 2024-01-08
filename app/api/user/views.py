from fastapi import APIRouter, Depends, Path, Request, Response, HTTPException
from api.base.base_schemas import BaseResponse, PaginationParams
from middlewares.authentication import get_user_id_from_access_token

from .schemas import (
    ReadAllUserResponse,
    ReadUserResponse,
    UpdateUserRequest,
    UpdateUserResponse,
    UserPaginationResponse,
)
from .use_cases import DeactivateUser, ReadAllUser, ReadUser, UpdateUser

router = APIRouter(prefix="/users")
tag = "User"


@router.get("", response_model=ReadAllUserResponse, tags=[tag])
async def read_all(
    request: Request,
    response: Response,
    token_user_id: int = Depends(get_user_id_from_access_token),
    include_deactivated: bool = False,
    page_params: PaginationParams = Depends(),
    read_all: ReadAllUser = Depends(ReadAllUser),
) -> ReadAllUserResponse:
    try:
        resp_data = await read_all.execute(
            page_params=page_params, include_deactivated=include_deactivated
        )

        return ReadAllUserResponse(
            status="success",
            message="success read users",
            data=UserPaginationResponse(records=resp_data[0], meta=resp_data[1]),
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return ReadAllUserResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to read users"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return ReadAllUserResponse(
            status="error",
            message=message,
        )


@router.get("/{user_id}", response_model=ReadUserResponse, tags=[tag])
async def read(
    request: Request,
    response: Response,
    user_id: int = Path(..., description=""),
    token_user_id: int = Depends(get_user_id_from_access_token),
    read_user: ReadUser = Depends(ReadUser),
) -> ReadUserResponse:
    try:
        resp_data = await read_user.execute(user_id=user_id)

        return ReadUserResponse(
            status="success",
            message="success read user",
            data=resp_data,
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return ReadUserResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to read user"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return ReadUserResponse(
            status="error",
            message=message,
        )


@router.put("", response_model=UpdateUserResponse, tags=[tag])
async def update(
    request: Request,
    response: Response,
    data: UpdateUserRequest,
    token_user_id: int = Depends(get_user_id_from_access_token),
    update_user: UpdateUser = Depends(UpdateUser),
) -> UpdateUserResponse:
    try:
        resp_data = await update_user.execute(user_id=token_user_id, request=data)

        return UpdateUserResponse(
            status="success",
            message="success update user",
            data=resp_data,
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return UpdateUserResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message="failed to update user"
        if hasattr(e, 'message'):
            message = e.message
        elif hasattr(e, 'detail'):
            message = e.detail

        return UpdateUserResponse(
            status="error",
            message=message,
        )


@router.put("/deactivate", response_model=BaseResponse, tags=[tag])
async def deactivate(
    response: Response,
    request: Request,
    token_user_id: int = Depends(get_user_id_from_access_token),
    deactivate_user: DeactivateUser = Depends(DeactivateUser),
) -> BaseResponse:
    try:
        await deactivate_user.execute(
            user_id=token_user_id,
        )

        return BaseResponse(
            status="success",
            message="success deactivate user",
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return BaseResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message = "error deactivate user"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return BaseResponse(
            status="error",
            message=message,
        )
