import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from jose import jwt, JWTError

from src.common.config import TOKEN_SECRET_KEY, JWT_SIGN_ALGORITHM
from src.common.exceptions import UserAlreadyExistsException, UserCredentialsException
from src.common.jwt_auth import send_password_reset_email
from src.user.dependencies import user_auth_service, user_service
from src.user.schemas import (
    CreateUserSchema,
    LoginUserSchema,
    LoginSuccessSchema,
    LogoutSuccessSchema,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
)
from src.user.service import UserAuthService
from src.common import jwt_auth

auth_router = APIRouter(
    prefix="/user",
    tags=["user_auth_api"],
    responses={404: {"description": "Not found"}},
)


@auth_router.post("/register", response_model=LoginSuccessSchema)
async def create_user_endpoint(
    user_data: CreateUserSchema,
    service: Annotated[UserAuthService, Depends(user_auth_service)],
):
    try:
        response = await service.register_user(user_data)
        return response
    except UserAlreadyExistsException:
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        logging.exception(
            f"User registration error. Email: {user_data.email}, Error: {e}"
        )
        raise HTTPException(status_code=400, detail="User registration error")


@auth_router.post("/login", response_model=LoginSuccessSchema)
async def login_for_token(
    user_data: LoginUserSchema,
    service: Annotated[UserAuthService, Depends(user_auth_service)],
):
    try:
        response = await service.authenticate_user(user_data)
        return response
    except UserCredentialsException:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        logging.exception(f"Error user auth. email: {user_data.email}, Error: {e}")
        raise HTTPException(status_code=400, detail="User authorization error")


@auth_router.get(
    "/logout",
    response_model=LogoutSuccessSchema,
    dependencies=[Depends(jwt_auth.get_current_user)],
)
async def logout_endpoint(
    response: Response,
    service: Annotated[UserAuthService, Depends(user_auth_service)],
):
    try:
        await service.logout_user(response)
        return {"message": "Logout successful"}
    except Exception as e:
        logging.exception(f"Logout error. Error: {e}")
        raise HTTPException(status_code=400, detail="Logout error")


@auth_router.post("/reset_password")
async def password_reset_request(data: PasswordResetRequestSchema):
    user = await user_service().user_repository.find_by_email(data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = jwt_auth.create_password_reset_token(user.email)
    await send_password_reset_email(user.email, token)
    return {"message": "Password reset link sent"}


@auth_router.post("/confirm_reset_password")
async def password_reset_confirm(data: PasswordResetConfirmSchema):
    try:
        payload = jwt.decode(
            data.token, TOKEN_SECRET_KEY, algorithms=[JWT_SIGN_ALGORITHM]
        )
        email = payload.get("sub")
        user = await user_service().user_repository.find_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        new_hashed_password = jwt_auth.get_password_hash(data.new_password)
        await user_service().user_repository.update_one(
            user.id, {"password": new_hashed_password}
        )
        return {"message": "Password has been updated"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
