from fastapi import FastAPI, HTTPException, status
from database import init_db, get_db_connection

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