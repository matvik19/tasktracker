from src.task.router import task_router
from src.user.auth_router import auth_router
from src.user.routers import user_router

all_routers = [
    auth_router,
    user_router,
    task_router,
]