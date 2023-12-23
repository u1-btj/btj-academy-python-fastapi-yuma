from fastapi import APIRouter, Depends, Request, Response, HTTPException
from api.base.base_schemas import BaseResponse
from middlewares.authentication import (
    refresh_access_token,
    get_user_id_from_access_token,
)

from .schema import (
    RegisterRequest,
    RegisterResponse,
    LoginResponse,
    LoginRequest,
    RefreshTokenResponse,
    TokenSchema,
    ChangePasswordRequest,
)
from .use_cases import LoginUser, Register, ChangePassword

router = APIRouter(prefix="/auth")
tag = "Authentication"


@router.post("/register", response_model=RegisterResponse, tags=[tag])
async def create(
    request: Request,
    response: Response,
    data: RegisterRequest,
    register: Register = Depends(Register),
) -> RegisterResponse:
    try:
        resp_data = await register.execute(
            request=data,
        )

        return RegisterResponse(
            status="success",
            message="success register new user",
            data=resp_data,
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return RegisterResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to register new user"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return RegisterResponse(
            status="error",
            message=message,
        )


@router.post("/login", response_model=LoginResponse, tags=[tag])
async def login(
    request: Request,
    response: Response,
    data: LoginRequest,
    login_user: LoginUser = Depends(LoginUser),
) -> LoginResponse:
    try:
        resp_data = await login_user.execute(
            data=data,
        )

        return LoginResponse(
            status="success",
            message=f"success login for username: {data.username}",
            data=resp_data,
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return LoginResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message = "failed to login"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail
        return LoginResponse(
            status="error",
            message=message,
        )


@router.get("/refresh-token", response_model=RefreshTokenResponse, tags=[tag])
async def refresh_token(
    request: Request,
    response: Response,
    new_token: list[str] = Depends(refresh_access_token),
) -> RefreshTokenResponse:
    try:
        return RefreshTokenResponse(
            status="success",
            message="success refreshing access token",
            data=TokenSchema(
                access_token=str(new_token[0]), refresh_token=str(new_token[1])
            ),
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return RefreshTokenResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message = "failed refresh token"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail
        return RefreshTokenResponse(
            status="error",
            message=message,
        )


@router.put("/change-password", response_model=BaseResponse, tags=[tag])
async def change_password(
    request: Request,
    response: Response,
    data: ChangePasswordRequest,
    token_user_id: int = Depends(get_user_id_from_access_token),
    change_password: ChangePassword = Depends(ChangePassword),
) -> BaseResponse:
    try:
        await change_password.execute(user_id=token_user_id, data=data)

        return BaseResponse(
            status="success",
            message="success change password user",
        )
    except HTTPException as ex:
        response.status_code = ex.status_code
        return BaseResponse(
            status="error",
            message=ex.detail,
        )
    except Exception as e:
        response.status_code = 500
        message = "error change password user"
        if hasattr(e, "message"):
            message = e.message
        elif hasattr(e, "detail"):
            message = e.detail

        return BaseResponse(
            status="error",
            message=message,
        )
