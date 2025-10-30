from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

# Request schema (what client sends)
class TaskCreate(BaseModel):
    name: str
    payload: Dict[str, Any]

# Response schema (what API returns)
class TaskResponse(BaseModel):
    id: int
    name: str
    status: str
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy model