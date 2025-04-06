import hmac
from datetime import datetime, timedelta
import bcrypt
from fastapi import HTTPException, Security
from fastapi.security import APIKeyCookie
from fastapi_mail import MessageSchema, FastMail, ConnectionConfig
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.common.config import (
    DEFAULT_ENCODING,
    HMAC_DIGEST_MODE,
    JWT_SIGN_ALGORITHM,
    TOKEN_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    MAIL_PASSWORD_APP,
)
from src.common.exceptions import (
    InvalidTokenException,
    UserAlreadyExistsException,
    UserNotAuthorizedException,
)
from src.user.models import User
from src.user.repository import UserRepository

# Для получения токена из cookie
auth_scheme = APIKeyCookie(name="authorization", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conf = ConnectionConfig(
    MAIL_USERNAME="matvey.sherbaev@gmail.com",
    MAIL_PASSWORD=MAIL_PASSWORD_APP,
    MAIL_FROM="matvey.sherbaev@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)


def _pepper_password(
    password: str, salt: bytes, encoding: str = DEFAULT_ENCODING
) -> bytes:
    bpwd = password.encode(encoding)
    pepper = TOKEN_SECRET_KEY.encode(encoding)
    seasoned = hmac.new(pepper, msg=bpwd, digestmod=HMAC_DIGEST_MODE)
    seasoned.update(salt)
    return seasoned.digest()


def get_password_hash(password: str, encoding: str = DEFAULT_ENCODING) -> str:
    salt = bcrypt.gensalt()
    peppered = _pepper_password(password, salt, encoding)
    return bcrypt.hashpw(peppered, salt).decode(encoding)


def verify_password(
    plain_password: str, hashed_password: str, encoding: str = DEFAULT_ENCODING
) -> bool:
    bsalt = hashed_password[:29].encode(encoding)
    peppered = _pepper_password(plain_password, bsalt, encoding)
    return bcrypt.checkpw(peppered, hashed_password.encode(encoding))


def create_access_token(email: str) -> str:
    data: dict[str, str | datetime] = {"sub": email}
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=JWT_SIGN_ALGORITHM)
    return encoded_jwt


async def create_user(user_data: dict) -> User:
    """
    Регистрирует пользователя: проверяет наличие email в БД,
    хеширует пароль и сохраняет запись.
    """
    user_repository = UserRepository()
    existing_user = await user_repository.find_by_email(user_data["email"])
    if existing_user is not None:
        raise UserAlreadyExistsException
    user_data["password"] = get_password_hash(user_data["password"])
    user = await user_repository.create_one(user_data)
    return user


async def get_user_from_db(email: str) -> User | None:
    user_repository = UserRepository()
    return await user_repository.find_by_email(email)


async def get_current_user(token_in_cookie: str = Security(auth_scheme)) -> User:
    if not token_in_cookie:
        raise UserNotAuthorizedException
    try:
        payload = jwt.decode(
            token_in_cookie, TOKEN_SECRET_KEY, algorithms=[JWT_SIGN_ALGORITHM]
        )
        email: str = payload.get("sub")
        exp_time = datetime.utcfromtimestamp(payload.get("exp"))
        if email is None or exp_time < datetime.utcnow():
            raise JWTError
        user = await get_user_from_db(email)
        if user is None:
            raise InvalidTokenException

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error getting authorization data - {e}"
        )


def create_password_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": email, "exp": expire}
    return jwt.encode(to_encode, TOKEN_SECRET_KEY, algorithm=JWT_SIGN_ALGORITHM)


async def send_password_reset_email(email: str, token: str):
    reset_url = f"https://localhost:3000/reset-password?token={token}"
    message = MessageSchema(
        subject="Password Reset",
        recipients=[email],
        body=f"Click to reset your password: {reset_url}",
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)
