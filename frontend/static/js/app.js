// Core Application Orchestrator

// Mobile Navigation Drawer Toggle Handler
function toggleMobileSidebar(forceState) {
    const sidebar = document.getElementById("app-sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    
    if (!sidebar || !backdrop) return;

    const shouldOpen = typeof forceState === "boolean" ? forceState : !sidebar.classList.contains("open");

    if (shouldOpen) {
        sidebar.classList.add("open");
        backdrop.classList.add("open");
        document.body.style.overflow = "hidden"; // Disable scroll behind drawer
    } else {
        sidebar.classList.remove("open");
        backdrop.classList.remove("open");
        document.body.style.overflow = "";
    }
}

// Handle Navigation view swaps
function switchView(viewName) {
    // Auto close mobile menu when switching views
    if (window.innerWidth <= 992) {
        toggleMobileSidebar(false);
    }

    // List of all sections and sidebar items
    const views = ['dashboard', 'interview', 'active-session', 'history', 'leaderboard'];
    
    views.forEach(v => {
        const section = document.getElementById(`view-${v}`);
        const navItem = document.getElementById(`nav-${v}`);
        
        if (section) {
            if (v === viewName) {
                section.classList.add("active");
            } else {
                section.classList.remove("active");
            }
        }

        if (navItem) {
            if (v === viewName) {
                navItem.classList.add("active");
            } else {
                navItem.classList.remove("active");
            }
        }
    });

    // Lazy load metrics when viewing corresponding panels
    if (viewName === 'dashboard') {
        loadDashboardMetrics();
    } else if (viewName === 'history') {
        loadHistoryList();
    } else if (viewName === 'leaderboard') {
        loadLeaderboardRanks();
    }

    // Refresh Lucide Icons in case new elements are injected
    if (window.lucide) {
        lucide.createIcons();
    }
}

// App Initialization entrypoint
document.addEventListener("DOMContentLoaded", () => {
    // Render initial icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // Check session states
    checkStoredSession();

    // Auto-reset mobile sidebar on resize to desktop
    window.addEventListener("resize", () => {
        if (window.innerWidth > 992) {
            toggleMobileSidebar(false);
        }
    });
});

