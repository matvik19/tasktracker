from sqlalchemy import select, update, delete
from src.task.models import Task
from src.common.database import async_session_maker
from src.common.repository import SQLAlchemyRepository
from src.common.exceptions import ItemNotExist


class TaskRepository(SQLAlchemyRepository):
    model: type[Task] = Task

    async def find_by_status_and_priority(
        self,
        user_id: int,
        is_completed: bool | None = None,
        priority: int | None = None,
    ):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.user_id == user_id)
            if is_completed is not None:
                stmt = stmt.where(self.model.is_completed == is_completed)
            if priority is not None:
                stmt = stmt.where(self.model.priority == priority)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def update_one(self, task_id: int, data: dict, user_id: int):
        async with async_session_maker() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == task_id, self.model.user_id == user_id)
                .values(**data)
                .returning(self.model)
            )
            res = await session.execute(stmt)
            await session.commit()
            row = res.scalar_one_or_none()
            if row is None:
                raise ItemNotExist("Task not found")
            return row

    async def delete_one(self, task_id: int, user_id: int):
        async with async_session_maker() as session:
            stmt = delete(self.model).where(
                self.model.id == task_id, self.model.user_id == user_id
            )
            res = await session.execute(stmt)
            await session.commit()
            if res.rowcount == 0:
                raise ItemNotExist("Task not found")

    async def admin_update_one(self, task_id: int, data: dict):
        async with async_session_maker() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == task_id)
                .values(**data)
                .returning(self.model)
            )
            res = await session.execute(stmt)
            await session.commit()
            row = res.scalar_one_or_none()
            if row is None:
                raise ItemNotExist("Task not found")
            return row
