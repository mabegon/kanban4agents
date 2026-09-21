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

# Dummy database (in production, use a proper database like PostgreSQL/MySQL)
users_db = {}
tasks_db = {}
boards_db = {}
columns_db = {}

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

# Authentication endpoints
@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = {
        "id": len(users_db) + 1,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password
    }
    
    users_db[user.username] = new_user
    return new_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
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
    return list(tasks_db.values())

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int, token: str = Depends(oauth2_scheme)):
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=Task)
async def create_task(task: TaskBase, token: str = Depends(oauth2_scheme)):
    new_task = {
        "id": len(tasks_db) + 1,
        "title": task.title,
        "description": task.description,
        "board_id": task.board_id,
        "column_id": task.column_id,
        "status": task.status
    }
    
    tasks_db[new_task["id"]] = new_task
    return new_task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskBase, token: str = Depends(oauth2_scheme)):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    updated_task = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "board_id": task.board_id,
        "column_id": task.column_id,
        "status": task.status
    }
    
    tasks_db[task_id] = updated_task
    return updated_task

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, token: str = Depends(oauth2_scheme)):
    if task_id in tasks_db:
        del tasks_db[task_id]
        return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")

# Board endpoints
@app.get("/boards", response_model=List[Board])
async def get_boards(token: str = Depends(oauth2_scheme)):
    return list(boards_db.values())

@app.get("/boards/{board_id}", response_model=Board)
async def get_board(board_id: int, token: str = Depends(oauth2_scheme)):
    board = boards_db.get(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@app.post("/boards", response_model=Board)
async def create_board(board: BoardBase, token: str = Depends(oauth2_scheme)):
    new_board = {
        "id": len(boards_db) + 1,
        "name": board.name,
        "description": board.description
    }
    
    boards_db[new_board["id"]] = new_board
    return new_board

@app.put("/boards/{board_id}", response_model=Board)
async def update_board(board_id: int, board: BoardBase, token: str = Depends(oauth2_scheme)):
    if board_id not in boards_db:
        raise HTTPException(status_code=404, detail="Board not found")
    
    updated_board = {
        "id": board_id,
        "name": board.name,
        "description": board.description
    }
    
    boards_db[board_id] = updated_board
    return updated_board

@app.delete("/boards/{board_id}")
async def delete_board(board_id: int, token: str = Depends(oauth2_scheme)):
    if board_id in boards_db:
        del boards_db[board_id]
        return {"message": "Board deleted"}
    raise HTTPException(status_code=404, detail="Board not found")

# Column endpoints
@app.get("/columns", response_model=List[Column])
async def get_columns(token: str = Depends(oauth2_scheme)):
    return list(columns_db.values())

@app.get("/columns/{column_id}", response_model=Column)
async def get_column(column_id: int, token: str = Depends(oauth2_scheme)):
    column = columns_db.get(column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column

@app.post("/columns", response_model=Column)
async def create_column(column: ColumnBase, token: str = Depends(oauth2_scheme)):
    new_column = {
        "id": len(columns_db) + 1,
        "name": column.name,
        "board_id": column.board_id,
        "position": column.position
    }
    
    columns_db[new_column["id"]] = new_column
    return new_column

@app.put("/columns/{column_id}", response_model=Column)
async def update_column(column_id: int, column: ColumnBase, token: str = Depends(oauth2_scheme)):
    if column_id not in columns_db:
        raise HTTPException(status_code=404, detail="Column not found")
    
    updated_column = {
        "id": column_id,
        "name": column.name,
        "board_id": column.board_id,
        "position": column.position
    }
    
    columns_db[column_id] = updated_column
    return updated_column

@app.delete("/columns/{column_id}")
async def delete_column(column_id: int, token: str = Depends(oauth2_scheme)):
    if column_id in columns_db:
        del columns_db[column_id]
        return {"message": "Column deleted"}
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