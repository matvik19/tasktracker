from sqlalchemy import select
from src.common.database import async_session_maker
from src.common.repository import SQLAlchemyRepository
from src.user.models import User

class UserRepository(SQLAlchemyRepository):
    model: type[User] = User

    async def find_by_email(self, email: str) -> User | None:
        async with async_session_maker() as session:
            result = await session.execute(select(self.model).where(self.model.email == email))
            return result.scalar_one_or_none()
