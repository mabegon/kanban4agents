#!/usr/bin/env python3
"""
Test script to verify SQLite database implementation
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import init_database, create_user, get_user_by_username, create_board, get_all_boards, create_column, get_columns_by_board, create_task, get_all_tasks

def test_database():
    # Initialize database
    print("Initializing database...")
    init_database()
    print("Database initialized successfully")
    
    # Test user creation
    print("\nTesting user creation...")
    user = create_user("testuser", "test@example.com", "$2b$12$example_hashed_password")
    print(f"Created user: {user}")
    
    # Retrieve user
    retrieved_user = get_user_by_username("testuser")
    print(f"Retrieved user: {retrieved_user}")
    
    # Test board creation
    print("\nTesting board creation...")
    board = create_board("Test Board", "This is a test board")
    print(f"Created board: {board}")
    
    # Test column creation
    print("\nTesting column creation...")
    column = create_column("To Do", board["id"], 0)
    print(f"Created column: {column}")
    
    # Test task creation
    print("\nTesting task creation...")
    task = create_task("Test Task", "This is a test task", board["id"], column["id"], "todo")
    print(f"Created task: {task}")
    
    # Retrieve all tasks
    print("\nTesting retrieval of all tasks...")
    tasks = get_all_tasks()
    print(f"All tasks: {tasks}")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_database()