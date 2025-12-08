# schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Модель для создания новой задачи
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_important: bool = Field(default=False)
    is_urgent: bool = Field(default=False)
    
    @property
    def quadrant(self) -> str:
        if self.is_important and self.is_urgent:
            return "Q1"
        elif self.is_important and not self.is_urgent:
            return "Q2"
        elif not self.is_important and self.is_urgent:
            return "Q3"
        else:
            return "Q4"

# Модель для ответа
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    is_important: bool
    is_urgent: bool
    quadrant: str
    completed: bool
    created_at: datetime