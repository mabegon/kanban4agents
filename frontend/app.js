// Configuration - uses default values, can be overridden by environment settings
const DEFAULT_API_BASE_URL = 'http://localhost:8000';
let API_BASE_URL = DEFAULT_API_BASE_URL;

// Function to initialize configuration from environment variables (if available)
function initConfig() {
    // In a production environment with server-side rendering, we would load from 
    // an injected variable or a config endpoint
    // For now, we're maintaining the default value but allowing customization
    
    // Allow override via global window object (for development/debugging)
    if (typeof window !== 'undefined' && window.config && window.config.backendUrl) {
        API_BASE_URL = window.config.backendUrl;
    }
}

// Initialize configuration
initConfig();

// Current user state
let currentUser = null;
let currentToken = null;

// DOM Elements
const loginForm = document.getElementById('login-form');
const userInfo = document.getElementById('user-info');
const userGreeting = document.getElementById('user-greeting');
const logoutBtn = document.getElementById('logout-btn');

const boardsContainer = document.getElementById('boards-container');
const addBoardBtn = document.getElementById('add-board-btn');
const modal = document.getElementById('modal');
const taskModal = document.getElementById('task-modal');
const closeModalBtns = document.querySelectorAll('.close');
const boardForm = document.getElementById('board-form');
const taskForm = document.getElementById('task-form');
const boardNameInput = document.getElementById('board-name');
const boardDescriptionInput = document.getElementById('board-description');
const taskTitleInput = document.getElementById('task-title');
const taskDescriptionInput = document.getElementById('task-description');
const taskBoardIdInput = document.getElementById('task-board-id');
const taskColumnIdInput = document.getElementById('task-column-id');

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    checkAuthStatus();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    if (currentUser && currentToken) {
        loadBoards();
    }
});

function setupEventListeners() {
    // Login/Register handling
    document.getElementById('login-btn').addEventListener('click', handleLogin);
    document.getElementById('register-btn').addEventListener('click', handleRegister);
    logoutBtn.addEventListener('click', handleLogout);
    
    // Add board button
    addBoardBtn.addEventListener('click', () => openModal('Add Board'));
    
    // Modal forms
    boardForm.addEventListener('submit', handleBoardSubmit);
    taskForm.addEventListener('submit', handleTaskSubmit);
    
    // Close modals
    closeModalBtns.forEach(btn => btn.addEventListener('click', closeModal));
    
    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === modal) closeModal();
        if (event.target === taskModal) closeModalTask();
    });
}

function checkAuthStatus() {
    // Check for stored token in localStorage
    const token = localStorage.getItem('kanban_token');
    const user = localStorage.getItem('kanban_user');
    
    if (token && user) {
        currentToken = token;
        currentUser = JSON.parse(user);
        showLoggedIn();
    } else {
        showLoggedOut();
    }
}

function showLoggedIn() {
    loginForm.classList.add('hidden');
    userInfo.classList.remove('hidden');
    userGreeting.textContent = `Hello, ${currentUser.username}`;
}

function showLoggedOut() {
    loginForm.classList.remove('hidden');
    userInfo.classList.add('hidden');
    currentUser = null;
    currentToken = null;
    // Clear stored data
    localStorage.removeItem('kanban_token');
    localStorage.removeItem('kanban_user');
    boardsContainer.innerHTML = '';
}

function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        alert('Please enter both username and password');
        return;
    }
    
    login(username, password);
}

function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = prompt('Enter your email:');
    
    if (!username || !password || !email) {
        alert('Please enter all fields');
        return;
    }
    
    register(username, email, password);
}

function handleLogout() {
    localStorage.removeItem('kanban_token');
    localStorage.removeItem('kanban_user');
    showLoggedOut();
    boardsContainer.innerHTML = '';
}

async function login(username, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        if (response.ok) {
            const data = await response.json();
            currentToken = data.access_token;
            currentUser = { username };
            
            // Store in localStorage
            localStorage.setItem('kanban_token', currentToken);
            localStorage.setItem('kanban_user', JSON.stringify(currentUser));
            
            showLoggedIn();
            loadBoards();
        } else {
            const error = await response.json();
            alert(`Login failed: ${error.detail}`);
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login failed. Please check your connection.');
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        
        if (response.ok) {
            alert('Registration successful. Please login.');
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        } else {
            const error = await response.json();
            alert(`Registration failed: ${error.detail}`);
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed. Please check your connection.');
    }
}

async function loadBoards() {
    try {
        const response = await fetch(`${API_BASE_URL}/boards`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const boards = await response.json();
            displayBoards(boards);
        } else {
            console.error('Failed to load boards');
        }
    } catch (error) {
        console.error('Error loading boards:', error);
    }
}

function displayBoards(boards) {
    boardsContainer.innerHTML = '';
    
    boards.forEach(board => {
        const boardElement = createBoardElement(board);
        boardsContainer.appendChild(boardElement);
    });
}

function createBoardElement(board) {
    const boardDiv = document.createElement('div');
    boardDiv.className = 'board';
    boardDiv.innerHTML = `
        <div class="board-header">
            <h2 class="board-title">${board.name}</h2>
            <button class="add-task-btn" data-board-id="${board.id}">+ Task</button>
        </div>
        <div class="column-task-list" id="columns-${board.id}">
            <!-- Columns will be populated here -->
        </div>
    `;
    
    // Add event listener for the add task button
    boardDiv.querySelector('.add-task-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        openTaskModal(board.id);
    });
    
    loadColumnsForBoard(board.id);
    
    return boardDiv;
}

async function loadColumnsForBoard(boardId) {
    try {
        const response = await fetch(`${API_BASE_URL}/columns?board_id=${boardId}`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const columns = await response.json();
            displayColumns(columns, boardId);
        } else {
            console.error('Failed to load columns for board:', boardId);
        }
    } catch (error) {
        console.error('Error loading columns:', error);
    }
}

function displayColumns(columns, boardId) {
    const container = document.getElementById(`columns-${boardId}`);
    container.innerHTML = '';
    
    // Create a column for each column
    columns.forEach(column => {
        const columnDiv = createColumnElement(column);
        container.appendChild(columnDiv);
        
        // Load tasks for this column
        loadTasksForColumn(column.id, columnDiv);
    });
}

function createColumnElement(column) {
    const columnDiv = document.createElement('div');
    columnDiv.className = 'column';
    columnDiv.innerHTML = `
        <div class="column-header">
            <h3 class="column-title">${column.name}</h3>
        </div>
        <div class="tasks-container" id="tasks-${column.id}">
            <div class="empty-column">No tasks</div>
        </div>
    `;
    
    return columnDiv;
}

async function loadTasksForColumn(columnId, columnElement) {
    try {
        const response = await fetch(`${API_BASE_URL}/tasks?column_id=${columnId}`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const tasks = await response.json();
            displayTasks(tasks, columnId, columnElement);
        } else {
            console.error('Failed to load tasks for column:', columnId);
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

function displayTasks(tasks, columnId, columnElement) {
    const tasksContainer = columnElement.querySelector('.tasks-container');
    
    if (tasks.length === 0) {
        tasksContainer.innerHTML = '<div class="empty-column">No tasks</div>';
        return;
    }
    
    tasksContainer.innerHTML = '';
    
    tasks.forEach(task => {
        const taskElement = createTaskElement(task);
        tasksContainer.appendChild(taskElement);
    });
}

function createTaskElement(task) {
    const taskDiv = document.createElement('div');
    taskDiv.className = 'task';
    taskDiv.innerHTML = `
        <div class="task-title">${task.title}</div>
        <div class="task-description">${task.description || ''}</div>
    `;
    
    // Add click event to show task details
    taskDiv.addEventListener('click', () => {
        alert(`Task: ${task.title}\nDescription: ${task.description || 'No description'}`);
    });
    
    return taskDiv;
}

function openModal(title) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('board-id').value = '';
    boardNameInput.value = '';
    boardDescriptionInput.value = '';
    modal.classList.remove('hidden');
}

function closeModal() {
    modal.classList.add('hidden');
    taskModal.classList.add('hidden');
}

function openTaskModal(boardId) {
    document.getElementById('task-modal-title').textContent = 'Add Task';
    document.getElementById('task-id').value = '';
    taskTitleInput.value = '';
    taskDescriptionInput.value = '';
    taskBoardIdInput.value = boardId;
    
    // Load columns for this board
    loadColumnsForTaskModal(boardId);
    
    taskModal.classList.remove('hidden');
}

function closeModalTask() {
    taskModal.classList.add('hidden');
}

async function loadColumnsForTaskModal(boardId) {
    try {
        const response = await fetch(`${API_BASE_URL}/columns?board_id=${boardId}`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const columns = await response.json();
            populateColumnsSelect(columns);
        } else {
            console.error('Failed to load columns for task modal');
        }
    } catch (error) {
        console.error('Error loading columns for task modal:', error);
    }
}

function populateColumnsSelect(columns) {
    taskColumnIdInput.innerHTML = '';
    
    columns.forEach(column => {
        const option = document.createElement('option');
        option.value = column.id;
        option.textContent = column.name;
        taskColumnIdInput.appendChild(option);
    });
}

async function handleBoardSubmit(e) {
    e.preventDefault();
    
    const boardId = document.getElementById('board-id').value;
    const name = boardNameInput.value;
    const description = boardDescriptionInput.value;
    
    if (!name) {
        alert('Please enter a board name');
        return;
    }
    
    try {
        let response;
        if (boardId) {
            // Update existing board
            response = await fetch(`${API_BASE_URL}/boards/${boardId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${currentToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description
                })
            });
        } else {
            // Create new board
            response = await fetch(`${API_BASE_URL}/boards`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description
                })
            });
        }
        
        if (response.ok) {
            closeModal();
            loadBoards(); // Reload boards to show changes
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error saving board:', error);
        alert('Failed to save board. Please check your connection.');
    }
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    
    const taskId = document.getElementById('task-id').value;
    const title = taskTitleInput.value;
    const description = taskDescriptionInput.value;
    const boardId = parseInt(taskBoardIdInput.value);
    const columnId = parseInt(taskColumnIdInput.value);
    
    if (!title || !boardId || !columnId) {
        alert('Please fill in all required fields');
        return;
    }
    
    try {
        let response;
        if (taskId) {
            // Update existing task
            response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${currentToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    description,
                    board_id: boardId,
                    column_id: columnId
                })
            });
        } else {
            // Create new task
            response = await fetch(`${API_BASE_URL}/tasks`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${currentToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title,
                    description,
                    board_id: boardId,
                    column_id: columnId
                })
            });
        }
        
        if (response.ok) {
            closeModalTask();
            loadBoards(); // Reload boards to show changes
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error saving task:', error);
        alert('Failed to save task. Please check your connection.');
    }
}

// Export functions for testing and debugging
window.app = {
    login,
    register,
    loadBoards,
    openModal,
    closeModal,
    openTaskModal,
    closeModalTask
};