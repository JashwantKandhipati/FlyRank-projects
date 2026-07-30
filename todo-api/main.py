from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Task API", version="1.0")

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write README", "done": False},
    {"id": 3, "title": "Push to GitHub", "done": True},
]
next_id = 4


@app.get("/", summary="API info")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.post("/tasks", summary="Create a new task", status_code=201)
async def create_task(request: Request):
    global next_id
    body = await request.json()
    title = body.get("title")

    if not title or not isinstance(title, str) or not title.strip():
        return JSONResponse(status_code=400, content={"error": "title is required"})

    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    return JSONResponse(status_code=201, content=task)


@app.put("/tasks/{task_id}", summary="Update a task")
async def update_task(task_id: int, request: Request):
    body = await request.json()

    if not isinstance(body, dict) or not body:
        return JSONResponse(status_code=400, content={"error": "request body is required"})

    for task in tasks:
        if task["id"] == task_id:
            if "title" in body:
                if not isinstance(body["title"], str) or not body["title"].strip():
                    return JSONResponse(status_code=400, content={"error": "title must be a non-empty string"})
                task["title"] = body["title"]
            if "done" in body:
                if not isinstance(body["done"], bool):
                    return JSONResponse(status_code=400, content={"error": "done must be a boolean"})
                task["done"] = body["done"]
            return task

    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.delete("/tasks/{task_id}", summary="Delete a task", status_code=204)
def delete_task(task_id: int):
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return JSONResponse(status_code=204, content=None)
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})