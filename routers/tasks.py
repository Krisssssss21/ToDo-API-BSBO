# routers/tasks.py
from fastapi import APIRouter, HTTPException, status, Response
from typing import List
from datetime import datetime
from schemas import TaskCreate, TaskUpdate, TaskResponse
from database import tasks_db  # импортируем из database.py

router = APIRouter(
    prefix='/tasks',
    tags=['tasks'],
    responses={404: {'description': 'Задача не найдена'}}
)

# POST /tasks/ - создание задачи
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate) -> TaskResponse:
    # Определяем квадрант
    if task.is_important and task.is_urgent:
        quadrant = "Q1"
    elif task.is_important and not task.is_urgent:
        quadrant = "Q2"
    elif not task.is_important and task.is_urgent:
        quadrant = "Q3"
    else:
        quadrant = "Q4"
    
    new_id = max([t["id"] for t in tasks_db], default=0) + 1
    
    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "is_important": task.is_important,
        "is_urgent": task.is_urgent,
        "quadrant": quadrant,
        "completed": False,
        "created_at": datetime.now()
    }
    
    tasks_db.append(new_task)
    return new_task

# GET /tasks/{task_id} - получение задачи по ID
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int) -> TaskResponse:
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task

# GET /tasks/ - получение всех задач
@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks() -> List[TaskResponse]:
    return tasks_db

# PUT /tasks/{task_id} - обновление задачи
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    # Ищем задачу
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Получаем только переданные поля
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Обновляем поля
    for field, value in update_data.items():
        task[field] = value
    
    # Пересчитываем квадрант если изменились важность или срочность
    if "is_important" in update_data or "is_urgent" in update_data:
        if task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q1"
        elif task["is_important"] and not task["is_urgent"]:
            task["quadrant"] = "Q2"
        elif not task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q3"
        else:
            task["quadrant"] = "Q4"
    
    return task

# PATCH /tasks/{task_id}/complete - отметить задачу выполненной
@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int) -> TaskResponse:
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    task["completed"] = True
    task["completed_at"] = datetime.now()
    return task

# DELETE /tasks/{task_id} - удаление задачи
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    tasks_db.remove(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
# Получение задач по квадранту
@router.get("/quadrant/{quadrant}", response_model=List[TaskResponse])
async def get_tasks_by_quadrant(quadrant: str) -> List[TaskResponse]:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )
    
    return [task for task in tasks_db if task["quadrant"] == quadrant]

# Получение задач по статусу
@router.get("/status/{status}", response_model=List[TaskResponse])
async def get_tasks_by_status(status: str) -> List[TaskResponse]:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный статус. Используйте: 'completed' или 'pending'"
        )
    
    is_completed = (status == "completed")
    return [task for task in tasks_db if task["completed"] == is_completed]