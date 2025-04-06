from sqlalchemy import select, update, delete
from src.task.models import Task
from src.common.database import async_session_maker
from src.common.repository import SQLAlchemyRepository

class TaskRepository(SQLAlchemyRepository):
    model: type[Task] = Task

    async def find_by_status_and_priority(
        self, is_completed: bool | None = None, priority: int | None = None
    ):
        async with async_session_maker() as session:
            stmt = select(self.model)
            if is_completed is not None:
                stmt = stmt.where(self.model.is_completed == is_completed)
            if priority is not None:
                stmt = stmt.where(self.model.priority == priority)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def mark_as_completed(self, task_id: int):
        async with async_session_maker() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == task_id)
                .values(is_completed=True)
                .returning(self.model)
            )
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()
