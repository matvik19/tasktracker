from fastapi import Depends
from src.task.repository import TaskRepository
from src.task.service import TaskService

def task_service() -> TaskService:
    return TaskService(TaskRepository())
