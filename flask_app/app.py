from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
import jwt
import bcrypt
import os

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# Enable CORS for API endpoints
CORS(app)

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database configuration
DATABASE_PATH = "kanban.db"

def init_database():
    """Initialize the database with tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    """)
    
    # Create boards table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)
    
    # Create columns table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS columns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            board_id INTEGER NOT NULL,
            position INTEGER DEFAULT 0,
            FOREIGN KEY (board_id) REFERENCES boards (id)
        )
    """)
    
    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            board_id INTEGER NOT NULL,
            column_id INTEGER NOT NULL,
            status TEXT DEFAULT 'todo',
            FOREIGN KEY (board_id) REFERENCES boards (id),
            FOREIGN KEY (column_id) REFERENCES columns (id)
        )
    """)
    
    # Create default user (will be removed in production)
    cursor.execute("SELECT * FROM users WHERE username = 'default_user'")
    if not cursor.fetchone():
        # Create a default user with a simple password for development
        default_password = bcrypt.hashpw("default_password".encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            ("default_user", "default@example.com", default_password)
        )
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def dict_from_row(row):
    """Convert a sqlite3.Row to dict"""
    if row is None:
        return None
    return {col: row[col] for col in row.keys()}

# User functions
def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

def create_user(username, email, hashed_password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
        (username, email, hashed_password)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return get_user_by_id(user_id)

# Board functions
def get_board(board_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM boards WHERE id = ?", (board_id,))
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

def get_all_boards():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM boards")
    rows = cursor.fetchall()
    conn.close()
    return [dict_from_row(row) for row in rows]

def create_board(name, description):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO boards (name, description) VALUES (?, ?)",
        (name, description)
    )
    conn.commit()
    board_id = cursor.lastrowid
    conn.close()
    return get_board(board_id)

def update_board(board_id, name, description):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE boards SET name = ?, description = ? WHERE id = ?",
        (name, description, board_id)
    )
    conn.commit()
    conn.close()
    return get_board(board_id)

def delete_board(board_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM boards WHERE id = ?", (board_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

# Column functions
def get_column(column_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM columns WHERE id = ?", (column_id,))
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

def get_columns_by_board(board_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM columns WHERE board_id = ? ORDER BY position", (board_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict_from_row(row) for row in rows]

def create_column(name, board_id, position=0):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO columns (name, board_id, position) VALUES (?, ?, ?)",
        (name, board_id, position)
    )
    conn.commit()
    column_id = cursor.lastrowid
    conn.close()
    return get_column(column_id)

def update_column(column_id, name, board_id, position):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE columns SET name = ?, board_id = ?, position = ? WHERE id = ?",
        (name, board_id, position, column_id)
    )
    conn.commit()
    conn.close()
    return get_column(column_id)

def delete_column(column_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM columns WHERE id = ?", (column_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

# Task functions
def get_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict_from_row(row)

def get_all_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [dict_from_row(row) for row in rows]

def create_task(title, description, board_id, column_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, board_id, column_id, status) VALUES (?, ?, ?, ?, ?)",
        (title, description, board_id, column_id, status)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return get_task(task_id)

def update_task(task_id, title, description, board_id, column_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET title = ?, description = ?, board_id = ?, column_id = ?, status = ? WHERE id = ?",
        (title, description, board_id, column_id, status, task_id)
    )
    conn.commit()
    conn.close()
    return get_task(task_id)

def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

# Helper functions
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def create_access_token(data, expires_delta=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user():
    """Get the current logged-in user from the session"""
    username = session.get('username')
    if username:
        return get_user_by_username(username)
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Authentication endpoints
@app.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({"detail": "Missing required fields"}), 400
            
        existing_user = get_user_by_username(username)
        if existing_user:
            return jsonify({"detail": "Username already registered"}), 400
        
        hashed_password = get_password_hash(password)
        new_user = create_user(username, email, hashed_password)
        
        return jsonify(new_user), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/token', methods=['POST'])
def login_for_access_token():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"detail": "Missing username or password"}), 400
            
        user = get_user_by_username(username)
        if not user or not verify_password(password, user["hashed_password"]):
            return jsonify({"detail": "Incorrect username or password"}), 401
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        
        session['username'] = user['username']
        
        return jsonify({"access_token": access_token, "token_type": "bearer"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Task endpoints
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = get_all_tasks()
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task_endpoint(task_id):
    try:
        task = get_task(task_id)
        if not task:
            return jsonify({"detail": "Task not found"}), 404
        return jsonify(task), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task_endpoint():
    try:
        data = request.get_json()
        new_task = create_task(
            title=data.get('title'),
            description=data.get('description', ''),
            board_id=data.get('board_id'),
            column_id=data.get('column_id'),
            status=data.get('status', 'todo')
        )
        return jsonify(new_task), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task_endpoint(task_id):
    try:
        data = request.get_json()
        existing_task = get_task(task_id)
        if not existing_task:
            return jsonify({"detail": "Task not found"}), 404
        
        updated_task = update_task(
            task_id=task_id,
            title=data.get('title'),
            description=data.get('description', ''),
            board_id=data.get('board_id'),
            column_id=data.get('column_id'),
            status=data.get('status', 'todo')
        )
        return jsonify(updated_task), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_endpoint(task_id):
    try:
        existing_task = get_task(task_id)
        if not existing_task:
            return jsonify({"detail": "Task not found"}), 404
        
        success = delete_task(task_id)
        if success:
            return jsonify({"message": "Task deleted"}), 200
        else:
            return jsonify({"detail": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Board endpoints
@app.route('/api/boards', methods=['GET'])
def get_boards():
    try:
        boards = get_all_boards()
        return jsonify(boards), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/boards/<int:board_id>', methods=['GET'])
def get_board_endpoint(board_id):
    try:
        board = get_board(board_id)
        if not board:
            return jsonify({"detail": "Board not found"}), 404
        return jsonify(board), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/boards', methods=['POST'])
def create_board_endpoint():
    try:
        data = request.get_json()
        new_board = create_board(
            name=data.get('name'),
            description=data.get('description', '')
        )
        return jsonify(new_board), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/boards/<int:board_id>', methods=['PUT'])
def update_board_endpoint(board_id):
    try:
        data = request.get_json()
        existing_board = get_board(board_id)
        if not existing_board:
            return jsonify({"detail": "Board not found"}), 404
        
        updated_board = update_board(
            board_id=board_id,
            name=data.get('name'),
            description=data.get('description', '')
        )
        return jsonify(updated_board), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/boards/<int:board_id>', methods=['DELETE'])
def delete_board_endpoint(board_id):
    try:
        existing_board = get_board(board_id)
        if not existing_board:
            return jsonify({"detail": "Board not found"}), 404
        
        success = delete_board(board_id)
        if success:
            return jsonify({"message": "Board deleted"}), 200
        else:
            return jsonify({"detail": "Board not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Column endpoints
@app.route('/api/columns', methods=['GET'])
def get_columns():
    try:
        columns = []
        # Get all columns from database
        all_boards = get_all_boards()
        for board in all_boards:
            board_columns = get_columns_by_board(board["id"])
            columns.extend(board_columns)
        
        return jsonify(columns), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/columns/<int:column_id>', methods=['GET'])
def get_column_endpoint(column_id):
    try:
        column = get_column(column_id)
        if not column:
            return jsonify({"detail": "Column not found"}), 404
        return jsonify(column), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/columns', methods=['POST'])
def create_column_endpoint():
    try:
        data = request.get_json()
        new_column = create_column(
            name=data.get('name'),
            board_id=data.get('board_id'),
            position=data.get('position', 0)
        )
        return jsonify(new_column), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/columns/<int:column_id>', methods=['PUT'])
def update_column_endpoint(column_id):
    try:
        data = request.get_json()
        existing_column = get_column(column_id)
        if not existing_column:
            return jsonify({"detail": "Column not found"}), 404
        
        updated_column = update_column(
            column_id=column_id,
            name=data.get('name'),
            board_id=data.get('board_id'),
            position=data.get('position', 0)
        )
        return jsonify(updated_column), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/columns/<int:column_id>', methods=['DELETE'])
def delete_column_endpoint(column_id):
    try:
        existing_column = get_column(column_id)
        if not existing_column:
            return jsonify({"detail": "Column not found"}), 404
        
        success = delete_column(column_id)
        if success:
            return jsonify({"message": "Column deleted"}), 200
        else:
            return jsonify({"detail": "Column not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)