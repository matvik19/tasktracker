import logging
import httpx
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from src.task.schemas import CreateTaskSchema, UpdateTaskSchema, GetTaskSchema
from src.task.dependencies import task_service
from src.task.service import TaskService
from src.common import jwt_auth
from src.user.models import User

pomodoro_router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(jwt_auth.get_current_user)],
    responses={404: {"description": "Not found"}},
)

SECOND_BACKEND_URL = "http://212.41.30.156:7000/pomodoro"


@pomodoro_router.post("", response_model=GetTaskSchema)
async def create_task(
    task_data: CreateTaskSchema,
    service: Annotated[TaskService, Depends(task_service)],
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        task = await service.create_task(task_data, current_user.id)

        # Пример запроса ко второму бэкенду
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SECOND_BACKEND_URL}/start",
                params={
                    "userId": current_user.id,
                    "taskId": task.id,
                    "workMinutes": 25,
                    "chillMinutes": 5,
                },
            )

        return task
    except Exception as e:
        logging.exception(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail="Error creating task")


@pomodoro_router.patch("/{task_id}/complete", response_model=GetTaskSchema)
async def mark_task_completed(
    task_id: int,
    service: Annotated[TaskService, Depends(task_service)],
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        task = await service.mark_task_as_completed(task_id, current_user.id)

        # Запрос к другому бэкенду для остановки таймера
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{SECOND_BACKEND_URL}/stop",
                params={"userId": current_user.id, "taskId": task_id},
            )

        return task
    except Exception as e:
        logging.exception(f"Error marking task {task_id} as completed: {e}")
        raise HTTPException(status_code=400, detail="Error marking task as completed")


@pomodoro_router.get("/pomodoro-info")
async def get_pomodoro_info(
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SECOND_BACKEND_URL}/get-started-pomodoro",
                params={"userId": current_user.id},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logging.exception("Failed to fetch Pomodoro info")
        raise HTTPException(
            status_code=e.response.status_code, detail="Failed to get Pomodoro info"
        )


@pomodoro_router.get("/pomodoro-stats")
async def get_pomodoro_stats(
    current_user: User = Depends(jwt_auth.get_current_user),
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SECOND_BACKEND_URL}/get-pomodoro-stats",
                params={"userId": current_user.id},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logging.exception("Failed to fetch Pomodoro stats")
        raise HTTPException(
            status_code=e.response.status_code, detail="Failed to get Pomodoro stats"
        )
