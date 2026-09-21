# Kanban App API Documentation

## Overview
This is a minimal Kanban application API that can be used by both human users and AI agents. It provides full CRUD operations for tasks, boards, and columns with authentication.

## Authentication
All endpoints (except `/register` and `/token`) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /token` - Get access token for existing user

### Tasks
- `GET /tasks` - Get all tasks
- `GET /tasks/{task_id}` - Get specific task
- `POST /tasks` - Create new task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task

### Boards
- `GET /boards` - Get all boards
- `GET /boards/{board_id}` - Get specific board
- `POST /boards` - Create new board
- `PUT /boards/{board_id}` - Update board
- `DELETE /boards/{board_id}` - Delete board

### Columns
- `GET /columns` - Get all columns
- `GET /columns/{column_id}` - Get specific column
- `POST /columns` - Create new column
- `PUT /columns/{column_id}` - Update column
- `DELETE /columns/{column_id}` - Delete column

## Example Usage

### Register a User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword"
  }'
```

### Get Token
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=testuser&password=securepassword'
```

### Create Task
```bash
curl -X POST "http://localhost:8000/tasks" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement authentication",
    "description": "Add JWT authentication to the API",
    "board_id": 1,
    "column_id": 1
  }'
```