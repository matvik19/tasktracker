import re
from pydantic import field_validator, EmailStr, Field
from src.common.schema import BaseSchema


def password_validate(value: str) -> str:
    if len(value) < 6:
        raise ValueError("Password must be at least 6 characters long.")
    if len(re.findall(r"[A-Z]", value)) < 2:
        raise ValueError("Password must contain at least two uppercase letters.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValueError("Password must contain at least one special character.")
    return value


class CreateUserSchema(BaseSchema):
    email: EmailStr = Field(...)
    password: str = Field(...)

    @field_validator("email", mode="before")
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email address: missing '@'")
        return value.lower()

    @field_validator("password", mode="before")
    def validate_password(cls, value: str) -> str:
        return password_validate(value)


class LoginUserSchema(BaseSchema):
    email: EmailStr = Field(...)
    password: str = Field(...)

    @field_validator("email", mode="before")
    def validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email address: missing '@'")
        return value.lower()


class GetUserSchema(BaseSchema):
    id: int
    email: str


class LoginSuccessSchema(BaseSchema):
    message: str


class LogoutSuccessSchema(BaseSchema):
    message: str


class UpdateUserSchema(BaseSchema):
    email: str | None = None
    password: str | None = None


class PasswordResetRequestSchema(BaseSchema):
    email: str


class PasswordResetConfirmSchema(BaseSchema):
    token: str
    new_password: str = Field(...)
