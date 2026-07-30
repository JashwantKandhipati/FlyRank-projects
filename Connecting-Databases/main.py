from fastapi import FastAPI, HTTPException, status
from database import init_db, get_db_connection
from pydantic import BaseModel, field_validator
from typing import Optional

app = FastAPI()


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/tasks")
def get_all_tasks():
    """Fetch all tasks from the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()

    # Convert sqlite3.Row objects into standard dictionaries
    tasks = [dict(row) for row in rows]
    return tasks


@app.get("/tasks/{id}")
def get_task_by_id(id: int):
    """Fetch a single task by ID using a parameterized query."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Parameterized query protects against SQL injection
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Task not found"}
        )

    return dict(row)


# Pydantic schema for task creation input
class TaskCreate(BaseModel):
    title: str
    done: Optional[bool] = False

    @field_validator("title")
    def title_must_not_be_empty(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip()


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Insert a new task into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Parameterized query to insert the new task
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, int(task.done))
    )
    conn.commit()

    # Retrieve the auto-generated primary key ID
    new_id = cursor.lastrowid

    # Fetch the inserted row to return complete record
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    new_task = cursor.fetchone()
    conn.close()

    return dict(new_task)