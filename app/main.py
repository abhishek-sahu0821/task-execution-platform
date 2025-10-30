from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import engine, get_db, Base
from app.models import Task
from app.schemas import TaskCreate, TaskResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Execution Platform")

@app.get("/")
def root():
    return {"message": "Task Execution Platform API", "version": "0.1.0"}

@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Submit a new task"""
    db_task = Task(
        name=task.name,
        payload=task.payload,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks", response_model=List[TaskResponse])
def list_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all tasks"""
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks