from sqlalchemy import Column, Integer, String, ForeignKey
from database.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)