# schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Базовая модель для задачи (содержит все основные поля)
class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Название задачи")
    description: Optional[str] = Field(None, max_length=500, description="Описание задачи")
    is_important: bool = Field(..., description="Важность задачи")
    is_urgent: bool = Field(..., description="Срочность задачи")

# Модель для создания задачи (наследует от TaskBase)
class TaskCreate(TaskBase):
    pass

# Модель для обновления задачи (все поля опциональны)
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100, description="Новое название")
    description: Optional[str] = Field(None, max_length=500, description="Новое описание")
    is_important: Optional[bool] = Field(None, description="Новая важность")
    is_urgent: Optional[bool] = Field(None, description="Новая срочность")
    completed: Optional[bool] = Field(None, description="Статус выполнения")

# Модель для ответа (добавляем вычисляемые поля)
class TaskResponse(TaskBase):
    id: int = Field(..., description="Уникальный идентификатор задачи", examples=[1])
    quadrant: str = Field(..., description="Квадрант матрицы Эйзенхауэра", examples=["Q1"])
    completed: bool = Field(default=False, description="Статус выполнения")
    created_at: datetime = Field(..., description="Дата создания")
    
    class Config:
        from_attributes = True