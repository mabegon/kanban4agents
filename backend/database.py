import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

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
    
    # Check if we're in production mode
    try:
        import os
        is_prod = os.getenv('IS_PROD', 'false').lower() == 'true'
    except:
        is_prod = False
    
    # Create default user (will be removed in production)
    cursor.execute("SELECT * FROM users WHERE username = 'default_user'")
    if not cursor.fetchone():
        # Create a default user with a simple password for development
        import bcrypt
        default_password = bcrypt.hashpw("default_password".encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            ("default_user", "default@example.com", default_password)
        )
    
    # If in production mode and default user exists, remove it
    if is_prod:
        cursor.execute("DELETE FROM users WHERE username = 'default_user'")
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    try:
        yield conn
    finally:
        conn.close()

def dict_from_row(row):
    """Convert a sqlite3.Row to dict"""
    return {col: row[col] for col in row.keys()}

# User functions
def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict_from_row(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict_from_row(row) if row else None

def create_user(username: str, email: str, hashed_password: str) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return get_user_by_id(user_id)

# Board functions
def get_board(board_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM boards WHERE id = ?", (board_id,))
        row = cursor.fetchone()
        return dict_from_row(row) if row else None

def get_all_boards() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM boards")
        rows = cursor.fetchall()
        return [dict_from_row(row) for row in rows]

def create_board(name: str, description: str) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO boards (name, description) VALUES (?, ?)",
            (name, description)
        )
        conn.commit()
        board_id = cursor.lastrowid
        return get_board(board_id)

def update_board(board_id: int, name: str, description: str) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE boards SET name = ?, description = ? WHERE id = ?",
            (name, description, board_id)
        )
        conn.commit()
        return get_board(board_id)

def delete_board(board_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        conn.commit()
        return cursor.rowcount > 0

# Column functions
def get_column(column_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM columns WHERE id = ?", (column_id,))
        row = cursor.fetchone()
        return dict_from_row(row) if row else None

def get_columns_by_board(board_id: int) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM columns WHERE board_id = ? ORDER BY position", (board_id,))
        rows = cursor.fetchall()
        return [dict_from_row(row) for row in rows]

def create_column(name: str, board_id: int, position: int = 0) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO columns (name, board_id, position) VALUES (?, ?, ?)",
            (name, board_id, position)
        )
        conn.commit()
        column_id = cursor.lastrowid
        return get_column(column_id)

def update_column(column_id: int, name: str, board_id: int, position: int) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE columns SET name = ?, board_id = ?, position = ? WHERE id = ?",
            (name, board_id, position, column_id)
        )
        conn.commit()
        return get_column(column_id)

def delete_column(column_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM columns WHERE id = ?", (column_id,))
        conn.commit()
        return cursor.rowcount > 0

# Task functions
def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict_from_row(row) if row else None

def get_all_tasks() -> List[Dict[str, Any]]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        return [dict_from_row(row) for row in rows]

def create_task(title: str, description: str, board_id: int, column_id: int, status: str) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, board_id, column_id, status) VALUES (?, ?, ?, ?, ?)",
            (title, description, board_id, column_id, status)
        )
        conn.commit()
        task_id = cursor.lastrowid
        return get_task(task_id)

def update_task(task_id: int, title: str, description: str, board_id: int, column_id: int, status: str) -> Dict[str, Any]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET title = ?, description = ?, board_id = ?, column_id = ?, status = ? WHERE id = ?",
            (title, description, board_id, column_id, status, task_id)
        )
        conn.commit()
        return get_task(task_id)

def delete_task(task_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0