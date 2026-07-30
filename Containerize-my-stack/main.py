from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from database import (
    init_db,
    get_all_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
)

app = FastAPI()

class TaskCreate(BaseModel):
    title: str
    done: bool = False

class TaskUpdate(BaseModel):
    title: str
    done: bool

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/tasks")
def read_tasks():
    return get_all_tasks()

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_new_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return create_task(task.title, task.done)

@app.put("/tasks/{task_id}")
def update_existing_task(task_id: int, task: TaskUpdate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    updated = update_task(task_id, task.title, task.done)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_task(task_id: int):
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)