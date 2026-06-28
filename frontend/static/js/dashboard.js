// Dashboard Data Fetcher and Visuals Renderer

async function loadDashboardMetrics() {
    try {
        const response = await fetch("/api/candidate/dashboard", {
            headers: getAuthHeaders()
        });

        if (!response.ok) {
            if (response.status === 401) handleLogout();
            return;
        }

        const data = await response.json();

        // Populate metrics values
        document.getElementById("stat-total-interviews").textContent = data.total_interviews;
        document.getElementById("stat-avg-score").textContent = data.average_score.toFixed(1);
        document.getElementById("stat-best-score").textContent = data.best_score.toFixed(1);
        document.getElementById("stat-streak").textContent = `${data.streak_count} Day${data.streak_count !== 1 ? 's' : ''}`;
        document.getElementById("stat-today-progress").innerHTML = `
            <i data-lucide="zap" style="width:14px; height:14px;"></i>
            ${data.today_progress} Done Today
        `;

        // Render topic badges
        renderTopicBadges("strong-topics-cloud", data.strong_topics, "strong");
        renderTopicBadges("weak-topics-cloud", data.weak_topics, "weak");

        // Load achievements dynamically
        loadAchievements();
        lucide.createIcons();
    } catch (err) {
        console.error("Failed to load dashboard metrics:", err);
    }
}

function renderTopicBadges(elementId, topics, type) {
    const container = document.getElementById(elementId);
    container.innerHTML = "";

    if (!topics || topics.length === 0) {
        container.innerHTML = `<span class="tag-badge ${type}">No data yet</span>`;
        return;
    }

    topics.forEach(topic => {
        const badge = document.createElement("span");
        badge.className = `tag-badge ${type}`;
        badge.textContent = topic;
        container.appendChild(badge);
    });
}

async function loadAchievements() {
    const grid = document.getElementById("achievements-list-grid");
    
    try {
        const response = await fetch("/api/candidate/achievements", {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) return;
        const achievements = await response.json();
        
        if (achievements.length === 0) {
            grid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 2rem; color: var(--text-muted);">
                    <p style="font-size: 0.9rem;">Complete interviews to unlock career credentials.</p>
                </div>
            `;
            return;
        }

        grid.innerHTML = "";
        achievements.forEach(item => {
            const card = document.createElement("div");
            card.className = "achievement-item";
            
            // Format icon based on key
            let iconMarkup = '<i data-lucide="award"></i>';
            if (item.icon === "star") iconMarkup = '<i data-lucide="star"></i>';
            if (item.icon === "zap") iconMarkup = '<i data-lucide="zap"></i>';
            if (item.icon === "shield") iconMarkup = '<i data-lucide="shield"></i>';

            card.innerHTML = `
                <div class="achievement-icon-wrapper">
                    ${iconMarkup}
                </div>
                <div class="achievement-text">
                    <span class="achievement-title">${item.title}</span>
                    <span class="achievement-desc">${item.description}</span>
                </div>
            `;
            grid.appendChild(card);
        });

    } catch (err) {
        console.error("Error loading achievements:", err);
    }
}

async function loadLeaderboardRanks() {
    const listContainer = document.getElementById("leaderboard-ranks-list");
    
    try {
        const response = await fetch("/api/candidate/leaderboard", {
            headers: getAuthHeaders()
        });

        if (!response.ok) return;
        const leaderboard = await response.json();
        
        listContainer.innerHTML = "";
        
        if (leaderboard.length === 0) {
            listContainer.innerHTML = `<p style="text-align: center; color: var(--text-muted);">No entries yet.</p>`;
            return;
        }

        leaderboard.forEach(item => {
            const row = document.createElement("div");
            // Highlight top three spots
            const isTopThree = item.rank <= 3;
            row.className = `leaderboard-row-item ${isTopThree ? 'top-three' : ''}`;

            row.innerHTML = `
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <div class="rank-badge-orb">${item.rank}</div>
                    <span style="font-weight: 600;">${item.username}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-weight: 800; color: var(--primary);">${Math.round(item.score)}</span>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">XP</span>
                </div>
            `;
            listContainer.appendChild(row);
        });
        
        lucide.createIcons();
    } catch (err) {
        console.error("Error loading leaderboard:", err);
    }
}
