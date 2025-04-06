import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from src.task.schemas import CreateTaskSchema, UpdateTaskSchema, GetTaskSchema
from src.task.dependencies import task_service
from src.task.service import TaskService
from src.common import jwt_auth
from src.user.models import User  # Предполагаем, что модель User импортируется отсюда

task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(jwt_auth.get_current_user)],
    responses={404: {"description": "Not found"}},
)


@task_router.post("", response_model=GetTaskSchema)
async def create_task(
    task_data: CreateTaskSchema,
    service: Annotated[TaskService, Depends(task_service)],
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        return await service.create_task(task_data, current_user.id)
    except Exception as e:
        logging.exception(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail="Error creating task")


@task_router.put("/{task_id}", response_model=GetTaskSchema)
async def update_task(
    task_id: int,
    task_data: UpdateTaskSchema,
    service: Annotated[TaskService, Depends(task_service)],
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        return await service.update_task(task_id, task_data, current_user.id)
    except Exception as e:
        logging.exception(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=400, detail="Error updating task")


@task_router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    service: Annotated[TaskService, Depends(task_service)],
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        return await service.delete_task(task_id, current_user.id)
    except Exception as e:
        logging.exception(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=400, detail="Error deleting task")


@task_router.patch("/{task_id}/complete", response_model=GetTaskSchema)
async def mark_task_completed(
    task_id: int,
    service: Annotated[TaskService, Depends(task_service)],
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        return await service.mark_task_as_completed(task_id, current_user.id)
    except Exception as e:
        logging.exception(f"Error marking task {task_id} as completed: {e}")
        raise HTTPException(status_code=400, detail="Error marking task as completed")


@task_router.get("", response_model=list[GetTaskSchema])
async def list_tasks(
    service: Annotated[TaskService, Depends(task_service)],
    is_completed: bool | None = None,
    priority: int | None = None,
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        return await service.get_tasks(current_user.id, is_completed, priority)
    except Exception as e:
        logging.exception(f"Error listing tasks: {e}")
        raise HTTPException(status_code=400, detail="Error listing tasks")
