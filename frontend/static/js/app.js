// Core Application Orchestrator

// Handle Navigation view swaps
function switchView(viewName) {
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
    lucide.createIcons();
}

// App Initialization entrypoint
document.addEventListener("DOMContentLoaded", () => {
    // Render initial icons
    lucide.createIcons();

    // Check session states
    checkStoredSession();
});
