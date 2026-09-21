from pydantic import BaseModel
from typing import List, Optional

# Pydantic models for data validation and API documentation

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    board_id: int
    column_id: int
    status: str = "todo"

class Task(TaskBase):
    id: int
    
    class Config:
        from_attributes = True

class BoardBase(BaseModel):
    name: str
    description: Optional[str] = ""

class Board(BoardBase):
    id: int
    
    class Config:
        from_attributes = True

class ColumnBase(BaseModel):
    name: str
    board_id: int
    position: int = 0

class Column(ColumnBase):
    id: int
    
    class Config:
        from_attributes = True