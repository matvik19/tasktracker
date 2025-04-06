from datetime import datetime, timedelta, timezone
from fastapi import Response
from fastapi.responses import JSONResponse
from src.common import jwt_auth
from src.common.config import MAIL_PASSWORD_APP
from src.common.exceptions import UserCredentialsException
from src.user.repository import UserRepository
from src.user.schemas import CreateUserSchema, LoginUserSchema, UpdateUserSchema
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


class UserAuthService:
    """
    Сервис для регистрации и аутентификации.
    """

    def __init__(self, user_repository: UserRepository):
        # Создаем экземпляр репозитория
        self.user_repository = user_repository

    async def register_user(self, user_data: CreateUserSchema):
        # Регистрируем пользователя через jwt_auth
        await jwt_auth.create_user(user_data.model_dump())
        # Сразу логиним – возвращаем ответ с установкой cookie
        access_token_response = await self.authenticate_user(
            LoginUserSchema(email=user_data.email, password=user_data.password)
        )
        return access_token_response

    async def authenticate_user(self, user_data: LoginUserSchema):
        user = await self.user_repository.find_by_email(user_data.email)
        if not user:
            raise UserCredentialsException
        check_pass = jwt_auth.verify_password(user_data.password, user.password)
        if not check_pass:
            raise UserCredentialsException
        access_token = jwt_auth.create_access_token(email=user.email)
        response = JSONResponse({"message": "Login successful"})
        response.set_cookie(
            key="authorization",
            value=access_token,
            httponly=True,
            expires=(
                datetime.now(timezone.utc)
                + timedelta(minutes=jwt_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
            ).timestamp(),
            path="/",
            secure=False,  # Если используете HTTPS, установить True
            samesite="lax",
        )
        return response

    async def authenticate_user_with_token(self, user_data: LoginUserSchema):
        user = await self.user_repository.find_by_email(user_data.email)
        if not user:
            raise UserCredentialsException

        check_pass = jwt_auth.verify_password(user_data.password, user.password)
        if not check_pass:
            raise UserCredentialsException

        access_token = jwt_auth.create_access_token(email=user.email)

        # Возвращаем токен в теле ответа, без set_cookie
        return JSONResponse(
            {
                "message": "Login successful",
                "access_token": access_token,
                "token_type": "Bearer",
            }
        )

    @staticmethod
    async def logout_user(response: Response):
        response.delete_cookie("authorization")
        return response


class UserService:
    """
    Сервис для операций CRUD над пользователями.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_users(self):
        return await self.user_repository.find_all()

    async def get_user(self, user_id: int):
        return await self.user_repository.find_one(user_id)

    async def update_user(self, user_id: int, user_data: UpdateUserSchema):
        data = user_data.model_dump(exclude_unset=True)
        # Если обновляется пароль, его нужно хешировать
        if "password" in data and data["password"]:
            data["password"] = jwt_auth.get_password_hash(data["password"])
        return await self.user_repository.update_one(user_id, data)

    async def get_all_users(self):
        return await self.user_repository.find_all()
