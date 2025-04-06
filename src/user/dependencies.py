from src.user.repository import UserRepository
from src.user.service import UserAuthService, UserService

def user_auth_service() -> UserAuthService:
    return UserAuthService(UserRepository())

def user_service() -> UserService:
    return UserService(UserRepository())
