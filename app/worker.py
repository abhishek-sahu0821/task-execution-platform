import time
from datetime import datetime
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Task, TaskStatus

def process_task(task: Task, db: Session):
    """Process a single task with atomic status update"""
    try:
        print(f"🔄 Attempting to claim task {task.id}: {task.name}")
        
        # Atomic claim: Update status ONLY if still pending
        result = db.execute(
            update(Task)
            .where(Task.id == task.id, Task.status == TaskStatus.PENDING)
            .values(
                status=TaskStatus.RUNNING,
                started_at=datetime.now()
            )
        )
        db.commit()
        
        # Check if WE successfully claimed it
        if result.rowcount == 0:
            print(f"⚠️  Task {task.id} already claimed by another worker")
            return
        
        print(f"✅ Claimed task {task.id}, processing...")
        
        # Refresh task to get updated values
        db.refresh(task)
        
        # Simulate work (sleep based on payload)
        duration = task.payload.get("duration", 5)
        print(f"⏳ Working for {duration} seconds...")
        time.sleep(duration)
        
        # Mark as completed
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"✅ Task {task.id} completed!")
        
    except Exception as e:
        print(f"❌ Task {task.id} failed: {e}")
        
        # Mark as failed
        db.refresh(task)
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.utcnow()
        db.commit()

def worker_loop():
    """Main worker loop - continuously polls for pending tasks"""
    print("🚀 Worker started. Polling for tasks...")
    
    while True:
        db = SessionLocal()
        
        try:
            # Find a pending task
            task = db.query(Task).filter(
                Task.status == TaskStatus.PENDING
            ).first()
            
            if task:
                process_task(task, db)
            else:
                print("💤 No pending tasks. Waiting...")
                time.sleep(2)  # Poll every 2 seconds
                
        except Exception as e:
            print(f"⚠️  Worker error: {e}")
            time.sleep(2)
        finally:
            db.close()

if __name__ == "__main__":
    worker_loop()