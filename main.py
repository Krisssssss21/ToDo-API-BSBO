# Главный файл приложения
from fastapi import FastAPI
from routers import tasks, stats
from schemas import TaskCreate, TaskResponse
from datetime import datetime

app = FastAPI(
    title="ToDo лист API",
    description="API для управления задачами с использованием матрицы Эйзенхауэра",
    version="1.0.0",
    contact={
        "name": "Кристина",
    }
)

# Подключаем роутеры к приложению
app.include_router(tasks.router)
app.include_router(stats.router)

# Временное хранилище для новых задач (дополнение к tasks_db из routers/tasks.py)
new_tasks_db = []

@app.get("/")
async def welcome() -> dict:
    """
    Корневой эндпоинт - информация об API.
    
    Возвращает приветственное сообщение и метаданные API.
    """
    return {
        "message": "Привет, студент!",
        "title": app.title,
        "description": app.description,
        "version": app.version,
        "contact": app.contact
    }

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """
    Создание новой задачи с валидацией данных.
    
    Параметры:
    - **title**: Название задачи (обязательное, 1-200 символов)
    - **description**: Описание задачи (необязательное, до 1000 символов)
    - **is_important**: Важная ли задача? (по умолчанию False)
    - **is_urgent**: Срочная ли задача? (по умолчанию False)
    
    Возвращает созданную задачу с автоматически вычисленным квадрантом.
    """
    # Автоматически вычисляем квадрант на основе важности и срочности
    if task.is_important and task.is_urgent:
        quadrant = "Q1"
    elif task.is_important and not task.is_urgent:
        quadrant = "Q2"
    elif not task.is_important and task.is_urgent:
        quadrant = "Q3"
    else:
        quadrant = "Q4"
    
    # Создаем новую задачу
    new_task = {
        "id": len(new_tasks_db) + 1,  # простой способ генерации ID
        "title": task.title,
        "description": task.description,
        "is_important": task.is_important,
        "is_urgent": task.is_urgent,
        "quadrant": quadrant,
        "completed": False,
        "created_at": datetime.now()
    }
    
    # Добавляем в хранилище
    new_tasks_db.append(new_task)
    
    return new_task

@app.post("/tasks-test")
async def create_task_test(task: TaskCreate):
    """
    Тестовый эндпоинт для демонстрации работы Pydantic валидации.
    
    Показывает, как Pydantic автоматически:
    1. Валидирует типы данных
    2. Проверяет обязательные поля
    3. Отбрасывает лишние поля
    4. Вычисляет квадрант через @property
    """
    return {
        "message": "Задача прошла валидацию Pydantic!",
        "task_data": task.dict(),
        "computed_quadrant": task.quadrant,  # используем вычисляемое свойство
        "validation_passed": True,
        "note": "Это тестовый эндпоинт для демонстрации валидации"
    }