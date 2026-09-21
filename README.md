# Kanban App

A minimal Kanban application that can be used by both human users and AI agents with basic security for external access.

## Features

- RESTful API with authentication
- Task, Board, and Column management
- Minimal UI for human interaction
- Secure JWT-based authentication
- Agent-friendly API endpoints

## Architecture

### Backend
Built with FastAPI for high performance and automatic API documentation.

### Security
- JWT token authentication 
- Password hashing with bcrypt
- Input validation and sanitization
- Rate limiting (configured in production)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/kanban-app.git
cd kanban-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Navigate to the backend directory:
```bash
cd backend
```

2. Start the server:
```bash
python main.py
```

The API will be available at http://localhost:8000

For development with auto-reload, you can also use:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

The API documentation is automatically generated at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Usage for Agents

The API endpoints are designed to be agent-friendly with clear JSON responses. The main endpoints include:
- `/tasks` - Manage tasks
- `/boards` - Manage boards  
- `/columns` - Manage columns
- `/token` - Authentication

For authentication, agents should:
1. Register a user (POST /register)
2. Get an access token (POST /token)
3. Use the token for subsequent requests in the Authorization header