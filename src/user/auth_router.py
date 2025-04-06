import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response

from src.common.exceptions import UserAlreadyExistsException, UserCredentialsException
from src.user.dependencies import user_auth_service
from src.user.schemas import (
    CreateUserSchema,
    LoginUserSchema,
    LoginSuccessSchema,
    LogoutSuccessSchema,
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
        logging.exception(f"User registration error. Email: {user_data.email}, Error: {e}")
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

@auth_router.get("/logout", response_model=LogoutSuccessSchema, dependencies=[Depends(jwt_auth.get_current_user)])
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
