import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import bcrypt
from datetime import datetime, timedelta
import jwt
from jose import JWTError

# Initialize the FastAPI app
app = FastAPI(title="Kanban App API", version="1.0.0")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize database
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import init_database
init_database()

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Get configuration from environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")

# Pydantic models
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

# Configuration model
class ConfigResponse(BaseModel):
    backend_url: str
    backend_port: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Import database functions
from .database import (
    get_user_by_username,
    create_user,
    get_board,
    get_all_boards,
    create_board,
    update_board,
    delete_board,
    get_column,
    get_columns_by_board,
    create_column,
    update_column,
    delete_column,
    get_task,
    get_all_tasks,
    create_task,
    update_task,
    delete_task
)

# Authentication endpoints
@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = create_user(user.username, user.email, hashed_password)
    return new_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Configuration endpoint
@app.get("/config", response_model=ConfigResponse)
async def get_config():
    return ConfigResponse(
        backend_url=BACKEND_URL,
        backend_port=BACKEND_PORT
    )

# Task endpoints
@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = create_user(user.username, user.email, hashed_password)
    return new_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Task endpoints
@app.get("/tasks", response_model=List[Task])
async def get_tasks(token: str = Depends(oauth2_scheme)):
    tasks = get_all_tasks()
    # Convert to Pydantic models
    return [Task(**task) for task in tasks]

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task_endpoint(task_id: int, token: str = Depends(oauth2_scheme)):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(**task)

@app.post("/tasks", response_model=Task)
async def create_task_endpoint(task: TaskBase, token: str = Depends(oauth2_scheme)):
    new_task = create_task(
        title=task.title,
        description=task.description,
        board_id=task.board_id,
        column_id=task.column_id,
        status=task.status
    )
    return Task(**new_task)

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task_endpoint(task_id: int, task: TaskBase, token: str = Depends(oauth2_scheme)):
    existing_task = get_task(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = update_task(
        task_id=task_id,
        title=task.title,
        description=task.description,
        board_id=task.board_id,
        column_id=task.column_id,
        status=task.status
    )
    return Task(**updated_task)

@app.delete("/tasks/{task_id}")
async def delete_task_endpoint(task_id: int, token: str = Depends(oauth2_scheme)):
    existing_task = get_task(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    success = delete_task(task_id)
    if success:
        return {"message": "Task deleted"}
    else:
        raise HTTPException(status_code=404, detail="Task not found")

# Board endpoints
@app.get("/boards", response_model=List[Board])
async def get_boards(token: str = Depends(oauth2_scheme)):
    boards = get_all_boards()
    # Convert to Pydantic models
    return [Board(**board) for board in boards]

@app.get("/boards/{board_id}", response_model=Board)
async def get_board_endpoint(board_id: int, token: str = Depends(oauth2_scheme)):
    board = get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return Board(**board)

@app.post("/boards", response_model=Board)
async def create_board_endpoint(board: BoardBase, token: str = Depends(oauth2_scheme)):
    new_board = create_board(
        name=board.name,
        description=board.description
    )
    return Board(**new_board)

@app.put("/boards/{board_id}", response_model=Board)
async def update_board_endpoint(board_id: int, board: BoardBase, token: str = Depends(oauth2_scheme)):
    existing_board = get_board(board_id)
    if not existing_board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    updated_board = update_board(
        board_id=board_id,
        name=board.name,
        description=board.description
    )
    return Board(**updated_board)

@app.delete("/boards/{board_id}")
async def delete_board_endpoint(board_id: int, token: str = Depends(oauth2_scheme)):
    existing_board = get_board(board_id)
    if not existing_board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    success = delete_board(board_id)
    if success:
        return {"message": "Board deleted"}
    else:
        raise HTTPException(status_code=404, detail="Board not found")

# Column endpoints
@app.get("/columns", response_model=List[Column])
async def get_columns(token: str = Depends(oauth2_scheme)):
    columns = []
    # Get all columns from database
    from .database import get_columns_by_board
    all_boards = get_all_boards()
    for board in all_boards:
        board_columns = get_columns_by_board(board["id"])
        columns.extend(board_columns)
    
    # Convert to Pydantic models
    return [Column(**column) for column in columns]

@app.get("/columns/{column_id}", response_model=Column)
async def get_column_endpoint(column_id: int, token: str = Depends(oauth2_scheme)):
    column = get_column(column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return Column(**column)

@app.post("/columns", response_model=Column)
async def create_column_endpoint(column: ColumnBase, token: str = Depends(oauth2_scheme)):
    new_column = create_column(
        name=column.name,
        board_id=column.board_id,
        position=column.position
    )
    return Column(**new_column)

@app.put("/columns/{column_id}", response_model=Column)
async def update_column_endpoint(column_id: int, column: ColumnBase, token: str = Depends(oauth2_scheme)):
    existing_column = get_column(column_id)
    if not existing_column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    updated_column = update_column(
        column_id=column_id,
        name=column.name,
        board_id=column.board_id,
        position=column.position
    )
    return Column(**updated_column)

@app.delete("/columns/{column_id}")
async def delete_column_endpoint(column_id: int, token: str = Depends(oauth2_scheme)):
    existing_column = get_column(column_id)
    if not existing_column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    success = delete_column(column_id)
    if success:
        return {"message": "Column deleted"}
    else:
        raise HTTPException(status_code=404, detail="Column not found")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Kanban App API",
        "version": "1.0.0",
        "endpoints": [
            "/register",
            "/token",
            "/tasks",
            "/boards", 
            "/columns"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)