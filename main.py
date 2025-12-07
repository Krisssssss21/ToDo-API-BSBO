# Главный файл приложения
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",  
    contact={
        "name": "Кристина",
    }
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]

@app.get("/")
async def welcome() -> dict:
    return {
        "message": "Привет, студент!",
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "contact": app.contact
    }

# 1. Все задачи
@app.get("/tasks")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),
        "tasks": tasks_db
    }

# 2. Статистика - ДОЛЖЕН БЫТЬ ПЕРЕД /tasks/{task_id}
@app.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    # Считаем по квадрантам
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    # Считаем по статусу
    by_status = {"completed": 0, "pending": 0}
    
    for task in tasks_db:
        # Квадранты
        quadrant = task["quadrant"]
        by_quadrant[quadrant] += 1
        
        # Статус
        if task["completed"]:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1
    
    return {
        "total_tasks": len(tasks_db),
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }

# 3. Поиск задач - ДОЛЖЕН БЫТЬ ПЕРЕД /tasks/{task_id}
@app.get("/tasks/search")
async def search_tasks(q: str) -> dict:
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="Поисковый запрос должен содержать минимум 2 символа"
        )
    
    q_lower = q.lower()
    results = []
    
    for task in tasks_db:
        # Ищем в названии и описании
        title = task["title"].lower() if task["title"] else ""
        description = task["description"].lower() if task["description"] else ""
        
        if q_lower in title or q_lower in description:
            results.append(task)
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи по запросу '{q}' не найдены"
        )
    
    return {
        "query": q,
        "count": len(results),
        "tasks": results
    }

# 4. Задачи по квадранту
@app.get("/tasks/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )
    
    filtered_tasks = [task for task in tasks_db if task["quadrant"] == quadrant]
    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

# 5. Задачи по статусу
@app.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=400,
            detail="Неверный статус. Используйте: 'completed' или 'pending'"
        )
    
    is_completed = (status == "completed")
    filtered_tasks = [task for task in tasks_db if task["completed"] == is_completed]
    
    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

# 6. Задача по ID - В САМОМ КОНЦЕ!
@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=404,
        detail=f"Задача с ID {task_id} не найдена"
    )