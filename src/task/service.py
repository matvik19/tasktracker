from src.common.exceptions import ItemNotExist
from src.task.repository import TaskRepository
from src.task.schemas import CreateTaskSchema, UpdateTaskSchema

class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def create_task(self, task_data: CreateTaskSchema):
        data = task_data.model_dump(exclude_unset=True)
        return await self.task_repository.create_one(data)

    async def update_task(self, task_id: int, task_data: UpdateTaskSchema):
        data = task_data.model_dump(exclude_unset=True)
        result = await self.task_repository.update_one(task_id, data)
        if result is None:
            raise ItemNotExist()

        return result

    async def delete_task(self, task_id: int):
        await self.task_repository.delete_one(task_id)
        return {"message": "Task deleted successfully"}

    async def get_tasks(self, is_completed: bool | None = None, priority: int | None = None):
        return await self.task_repository.find_by_status_and_priority(is_completed, priority)

    async def mark_task_as_completed(self, task_id: int):
        return await self.task_repository.mark_as_completed(task_id)
