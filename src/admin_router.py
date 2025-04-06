# src/admin/router.py
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from src.task.schemas import GetTaskSchema
from src.task.dependencies import task_service
from src.task.service import TaskService
from src.user.schemas import GetUserSchema
from src.user.dependencies import user_service
from src.user.service import UserService

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)


@admin_router.get("/tasks", response_model=list[GetTaskSchema])
async def get_all_tasks(service: Annotated[TaskService, Depends(task_service)]):
    try:
        return await service.get_all_tasks()
    except Exception as e:
        logging.exception(f"Error getting all tasks: {e}")
        raise HTTPException(status_code=400, detail="Error getting all tasks")


@admin_router.patch("/tasks/{task_id}/complete", response_model=GetTaskSchema)
async def admin_mark_task_completed(
    task_id: int, service: Annotated[TaskService, Depends(task_service)]
):
    try:
        return await service.admin_mark_task_as_completed(task_id)
    except Exception as e:
        logging.exception(f"Error marking task {task_id} as completed by admin: {e}")
        raise HTTPException(status_code=400, detail="Error marking task as completed")
