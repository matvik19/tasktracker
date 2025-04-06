from src.task.repository import TaskRepository
from src.task.schemas import CreateTaskSchema, UpdateTaskSchema
from src.common.exceptions import TaskNotExist


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def create_task(self, task_data: CreateTaskSchema, user_id: int):
        # Получаем максимальный текущий приоритет для пользователя
        current_tasks = await self.task_repository.find_by_user(user_id)
        max_priority = max((task.priority for task in current_tasks), default=0)

        data = task_data.model_dump(exclude_unset=True)
        data["user_id"] = user_id
        data["priority"] = max_priority + 1  # следующий приоритет
        return await self.task_repository.create_one(data)

    async def update_task(
        self, task_id: int, task_data: UpdateTaskSchema, user_id: int
    ):
        data = task_data.model_dump(exclude_unset=True)
        try:
            return await self.task_repository.update_one(task_id, data, user_id)
        except Exception:
            raise TaskNotExist()

    async def delete_task(self, task_id: int, user_id: int):
        try:
            return await self.task_repository.delete_one(task_id, user_id)
        except Exception:
            raise TaskNotExist()

    async def get_tasks(
        self,
        user_id: int,
        is_completed: bool | None = None,
        priority: int | None = None,
    ):
        return await self.task_repository.find_by_status_and_priority(
            user_id, is_completed, priority
        )

    async def mark_task_as_completed(self, task_id: int, user_id: int):
        data = {"is_completed": True}
        try:
            return await self.task_repository.update_one(task_id, data, user_id)
        except Exception:
            raise TaskNotExist()

    async def get_all_tasks(self):
        return await self.task_repository.find_all()

    async def admin_mark_task_as_completed(self, task_id: int):
        data = {"is_completed": True}
        try:
            return await self.task_repository.admin_update_one(task_id, data)
        except Exception:
            raise TaskNotExist()

    async def get_task_by_id(self, task_id: int, user_id: int):
        return await self.task_repository.find_one_by_id(task_id, user_id)
