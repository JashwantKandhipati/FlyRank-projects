from fastapi import FastAPI
from database import init_db

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Task API with SQLite Backend"}