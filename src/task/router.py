import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from src.common.exceptions import ItemNotExist, TaskNotExist
from src.task.schemas import CreateTaskSchema, UpdateTaskSchema, GetTaskSchema
from src.task.dependencies import task_service
from src.task.service import TaskService

task_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
)

@task_router.post("", response_model=GetTaskSchema)
async def create_task(
    task_data: CreateTaskSchema,
    service: Annotated[TaskService, Depends(task_service)],
):
    try:
        return await service.create_task(task_data)
    except Exception as e:
        logging.exception(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail="Error creating task")

@task_router.put("/{task_id}", response_model=GetTaskSchema)
async def update_task(
    task_id: int,
    task_data: UpdateTaskSchema,
    service: Annotated[TaskService, Depends(task_service)],
):
    try:
        return await service.update_task(task_id, task_data)
    except ItemNotExist:
        raise TaskNotExist

    except Exception as e:
        logging.exception(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=400, detail="Error updating task")

@task_router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    service: Annotated[TaskService, Depends(task_service)],
):
    try:
        return await service.delete_task(task_id)
    except ItemNotExist:
        raise TaskNotExist
    except Exception as e:
        logging.exception(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=400, detail="Error deleting task")

@task_router.patch("/{task_id}/complete", response_model=GetTaskSchema)
async def mark_task_completed(
    task_id: int,
    service: Annotated[TaskService, Depends(task_service)],
):
    try:
        return await service.mark_task_as_completed(task_id)
    except Exception as e:
        logging.exception(f"Error marking task {task_id} as completed: {e}")
        raise HTTPException(status_code=400, detail="Error marking task as completed")

@task_router.get("", response_model=list[GetTaskSchema])
async def list_tasks(
    service: Annotated[TaskService, Depends(task_service)],
    is_completed: bool | None = None,
    priority: int | None = None,
):
    try:
        return await service.get_tasks(is_completed, priority)
    except Exception as e:
        logging.exception(f"Error listing tasks: {e}")
        raise HTTPException(status_code=400, detail="Error listing tasks")