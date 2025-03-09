from typing import Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str
    employee_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    employee_id: Optional[int] = None