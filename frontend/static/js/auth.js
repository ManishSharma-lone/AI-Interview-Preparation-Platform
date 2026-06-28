// Authentication Script for local storage state and API hooks

function switchAuthTab(tab) {
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");
    const loginForm = document.getElementById("login-form-el");
    const registerForm = document.getElementById("register-form-el");

    if (tab === "login") {
        tabLogin.classList.add("active");
        tabRegister.classList.remove("active");
        loginForm.style.display = "block";
        registerForm.style.display = "none";
    } else {
        tabLogin.classList.remove("active");
        tabRegister.classList.add("active");
        loginForm.style.display = "none";
        registerForm.style.display = "block";
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value.strip ? document.getElementById("login-email").value.strip() : document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;
    const rememberMe = document.getElementById("login-remember").checked;

    try {
        const response = await fetch("/api/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: email,
                password: password,
                remember_me: rememberMe
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Login failed. Check your email and password.");
            return;
        }

        // Store auth state
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", data.username);
        localStorage.setItem("email", data.email);

        initializeUserSession();
    } catch (err) {
        console.error("Login request error:", err);
        alert("An error occurred. Make sure your backend server is active.");
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById("reg-username").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;

    try {
        const response = await fetch("/api/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Registration failed. Check inputs.");
            return;
        }

        // Store auth state
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("username", data.username);
        localStorage.setItem("email", data.email);

        alert("Account created successfully!");
        initializeUserSession();
    } catch (err) {
        console.error("Registration request error:", err);
        alert("An error occurred during account creation.");
    }
}

function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("email");

    document.getElementById("auth-screen").style.display = "flex";
    document.getElementById("app-shell").style.display = "none";
    
    // Clear active sessions
    if (window.interviewTimer) {
        clearInterval(window.interviewTimer);
    }
}

function checkStoredSession() {
    const token = localStorage.getItem("token");
    if (token) {
        initializeUserSession();
    } else {
        document.getElementById("auth-screen").style.display = "flex";
        document.getElementById("app-shell").style.display = "none";
    }
}

function initializeUserSession() {
    const username = localStorage.getItem("username");
    const email = localStorage.getItem("email");

    // Populate Sidebar UI
    document.getElementById("profile-username").textContent = username || "Candidate";
    document.getElementById("profile-email").textContent = email || "candidate@ai.com";
    document.getElementById("stat-total-interviews").textContent = "..."; // Reset values

    // Hide auth card, show main application dashboard
    document.getElementById("auth-screen").style.display = "none";
    document.getElementById("app-shell").style.display = "flex";

    // Load data
    loadDashboardMetrics();
    loadHistoryList();
    loadLeaderboardRanks();
    
    // Initialize icons
    lucide.createIcons();
    
    // Reset view to dashboard
    switchView('dashboard');
}

// Global Auth Headers Helper
function getAuthHeaders() {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}
