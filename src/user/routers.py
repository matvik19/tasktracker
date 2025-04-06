import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from src.user.dependencies import user_service
from src.user.schemas import GetUserSchema, UpdateUserSchema
from src.user.service import UserService
from src.common import jwt_auth

# Роутер для CRUD по пользователям
user_router = APIRouter(
    prefix="/user",
    tags=["user_api"],
    responses={404: {"description": "Not found"}},
)


@user_router.get(
    "",
    response_model=list[GetUserSchema],
    dependencies=[Depends(jwt_auth.get_current_user)],
)
async def get_users(service: Annotated[UserService, Depends(user_service)]):
    try:
        return await service.get_users()
    except Exception as e:
        logging.exception(f"Error getting list of users. Error: {e}")
        raise HTTPException(status_code=400, detail="Error getting list of users")


@user_router.get(
    "/{user_id}",
    response_model=GetUserSchema,
    dependencies=[Depends(jwt_auth.get_current_user)],
)
async def get_user(
    user_id: int, service: Annotated[UserService, Depends(user_service)]
):
    try:
        return await service.get_user(user_id)
    except Exception as e:
        logging.exception(f"Error getting a user. Error: {e}")
        raise HTTPException(status_code=400, detail="Error getting a user")


@user_router.put(
    "/{user_id}",
    response_model=GetUserSchema,
    dependencies=[Depends(jwt_auth.get_current_user)],
)
async def update_user(
    user_id: int,
    user_data: UpdateUserSchema,
    service: Annotated[UserService, Depends(user_service)],
):
    try:
        return await service.update_user(user_id, user_data)
    except Exception as e:
        logging.exception(f"Error changing a user. User_id: {user_id}, Error: {e}")
        raise HTTPException(status_code=400, detail="Error changing a user")
