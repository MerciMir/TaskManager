from typing import Literal, Optional
from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str

class UserRegister(UserSchema):
    login: str
    password: str
    role: Literal["manager", "employee"] = "employee"


class UserLogin(BaseModel):
    login: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Literal["manager", "employee"]] = None
    