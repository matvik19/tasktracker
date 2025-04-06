from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(sa.String(256), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=True)
    priority: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    is_completed: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False
    )
    # Новый внешний ключ для связи с пользователем
    user_id: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Отношение с пользователем
    user = relationship("User", back_populates="tasks")
