
const API_BASE_URL = "http://127.0.0.1:8000";

// Регистрация
document.getElementById("registerForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value;
    const login = document.getElementById("login").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, login, password}),
        credentials: "include",
    });

    if (response.ok) {
        window.location.href = "/templates/tasks.html";
    } else {
        alert("Registration failed.");
    }
});

// Авторизация
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const login = document.getElementById("login").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ login, password }),
        credentials: "include",
    });

    if (response.ok) {
        window.location.href = "/templates/tasks.html";
    } else {
        alert("Login failed.");
    }
});


// Создание задачи
document.getElementById("createTaskForm")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("title").value;
    const description = document.getElementById("description").value;
    const assignedTo = document.getElementById("assignedTo").value;

    const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ title, description, employee_id: assignedTo }),
        credentials: "include", 
    });

    if (response.ok) {
        alert("Task created successfully!");
        loadTasks();
    } else {
        alert("Failed to create task.");
    }
});

// Проверка роли и скрытие формы создания задач
async function checkRoleAndHideForm() {
    const response = await fetch(`${API_BASE_URL}/my-role`, {
        credentials: "include", // Для работы с куками
    });

    if (response.ok) {
        const data = await response.json();
        const role = data.role;

        if (role === "employee") {
            document.getElementById("taskForm").style.display = "none"; // Скрываем форму
        }
    }
}

// Вызываем функцию при загрузке страницы
if (window.location.pathname.endsWith("tasks.html")) {
    loadMyTasks();
    checkRoleAndHideForm();
}

// Загрузка задач для текущего пользователя
async function loadMyTasks() {
    const response = await fetch(`${API_BASE_URL}/my-tasks`, {
        credentials: "include",
    });
    if (!response.ok) {
        alert("Failed to load tasks.");
        return;
    }
    const tasks = await response.json();
    const taskList = document.getElementById("tasks");
    taskList.innerHTML = "";

    // Добавляем нумерацию задач
    tasks.forEach((task, index) => {
        const li = document.createElement("li");
        li.className = "list-group-item";
        li.textContent = `${index + 1}. ${task.title}: ${task.description}`;
        taskList.appendChild(li);
    });
}

// Загружаем задачи при открытии страницы
if (window.location.pathname.endsWith("tasks.html")) {
    loadMyTasks();
}

// Выход из системы
document.getElementById("logoutButton")?.addEventListener("click", async () => {
    const response = await fetch(`${API_BASE_URL}/logout`, {
        method: "GET",
        credentials: "include",
    });

    if (response.ok) {
        window.location.href = "/templates/login.html";
    } else {
        alert("Logout failed.");
    }
});

