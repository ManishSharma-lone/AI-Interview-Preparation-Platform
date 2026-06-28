// Interview Management and Session Progression

// Active Interview State
let activeInterviewId = null;
let activeQuestionId = null;
let activeQuestionType = null;
let currentQuestionIndex = 1;
let totalQuestionsCount = 5;
let activeTestCases = [];
let activePythonTemplate = '';

let timerInterval = null;
let secondsRemaining = 0;

// ===== Language Templates =====
const LANG_TEMPLATES = {
    python: (tmpl) => tmpl || '# Write your Python solution here\ndef solution():\n    pass\n',
    javascript: (tmpl) => {
        // Convert python def to JS function stub if possible
        const match = tmpl && tmpl.match(/def (\w+)\(([^)]*)\)/);
        if (match) {
            const args = match[2].split(',').map(a => a.split(':')[0].trim()).filter(Boolean).join(', ');
            return `// Write your JavaScript solution here\nfunction ${match[1]}(${args}) {\n    // your code\n}\n`;
        }
        return '// Write your JavaScript solution here\nfunction solution() {\n    // your code\n}\n';
    },
    java: (tmpl) => {
        const match = tmpl && tmpl.match(/def (\w+)\(([^)]*)\)/);
        const name = match ? match[1] : 'solution';
        return `// Write your Java solution here\npublic class Solution {\n    public static Object ${name}(Object... args) {\n        // your code\n        return null;\n    }\n}\n`;
    },
    cpp: (tmpl) => {
        const match = tmpl && tmpl.match(/def (\w+)\(([^)]*)\)/);
        const name = match ? match[1] : 'solution';
        return `// Write your C++ solution here\n#include <bits/stdc++.h>\nusing namespace std;\n\nauto ${name}(auto... args) {\n    // your code\n}\n`;
    },
    c: (tmpl) => {
        const match = tmpl && tmpl.match(/def (\w+)\(([^)]*)\)/);
        const name = match ? match[1] : 'solution';
        return `/* Write your C solution here */\n#include <stdio.h>\n#include <stdlib.h>\n\nvoid ${name}() {\n    /* your code */\n}\n`;
    }
};

const LANG_LABELS = {
    python: 'Python 3',
    javascript: 'JavaScript',
    java: 'Java',
    cpp: 'C++',
    c: 'C'
};

const LANG_NOTE = {
    python: null,
    javascript: '\u26a0\ufe0f JavaScript execution requires Node.js installed on the server.',
    java: '\u26a0\ufe0f Java execution requires JDK installed on the server.',
    cpp: '\u26a0\ufe0f C++ execution requires g++ installed on the server.',
    c: '\u26a0\ufe0f C execution requires gcc installed on the server.'
};

async function startInterviewSession(event) {
    event.preventDefault();

    const role = document.getElementById("role-select").value;
    const difficulty = document.getElementById("difficulty-select").value;
    const type = document.getElementById("type-select").value;
    const count = parseInt(document.getElementById("count-select").value);

    try {
        const response = await fetch("/api/candidate/start-interview", {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                role_type: role,
                difficulty: difficulty,
                interview_type: type,
                num_questions: count
            })
        });

        if (!response.ok) {
            alert("Failed to initialize interview. Please try again.");
            return;
        }

        const data = await response.json();
        
        // Save state
        activeInterviewId = data.interview_id;
        
        // Show session view, hide menu view
        switchView('active-session');

        // Load first question
        loadQuestionData(data.first_question);

    } catch (err) {
        console.error("Error starting interview:", err);
        alert("Server error. Check database connections.");
    }
}

function loadQuestionData(qData) {
    if (!qData) return;

    activeQuestionId = qData.id;
    activeQuestionType = qData.question_type;
    currentQuestionIndex = qData.current_index;
    totalQuestionsCount = qData.total_questions;

    // Reset interaction inputs
    document.getElementById("answer-textbox").value = "";
    document.getElementById("sandbox-out").textContent = "Code compiler output will print here. Click Run Compile to test cases.";
    document.getElementById("sandbox-out").classList.remove("error");
    
    // Update index labels
    document.getElementById("active-question-index").textContent = `Question ${currentQuestionIndex} of ${totalQuestionsCount}`;
    document.getElementById("question-text-el").textContent = qData.text;

    // Handle Layout adjustments
    const container = document.getElementById("interview-workspace-container");
    const sandboxPane = document.getElementById("code-sandbox-pane");
    const textResponseBlock = document.getElementById("text-response-block");
    const voiceResponseBlock = document.getElementById("voice-response-block");

    // Clear voice transcript text
    document.getElementById("voice-transcript-log").textContent = "Microphone inactive. Transcripts will generate here in real-time...";
    if (window.speechRecognitionActive) {
        stopVoiceRecognition();
    }

    if (activeQuestionType === "Coding") {
        container.classList.remove("single-pane");
        sandboxPane.style.display = "flex";
        textResponseBlock.style.display = "none";
        voiceResponseBlock.style.display = "none";

        // Store Python template as base
        activePythonTemplate = qData.code_template || '# Write your Python solution here\ndef solution():\n    pass\n';

        // Set template for currently selected language
        const lang = document.getElementById('language-selector').value || 'python';
        const templateFn = LANG_TEMPLATES[lang] || LANG_TEMPLATES.python;
        document.getElementById('code-editor').value = templateFn(activePythonTemplate);

        // Update sandbox label
        document.getElementById('sandbox-lang-label').textContent = LANG_LABELS[lang] || 'Python 3';
        
        // Parse test cases
        try {
            activeTestCases = JSON.parse(qData.test_cases || "[]");
            renderTestCases(activeTestCases);
        } catch (e) {
            activeTestCases = [];
            document.getElementById("test-cases-list-panel").innerHTML = "";
        }
    } else {
        container.classList.add("single-pane");
        sandboxPane.style.display = "none";
        textResponseBlock.style.display = "flex";
        
        // HR interviews utilize Speech-to-Text visually
        if (activeQuestionType === "HR") {
            voiceResponseBlock.style.display = "flex";
        } else {
            voiceResponseBlock.style.display = "none";
        }
    }

    // Set Timer duration based on type
    if (activeQuestionType === "HR") {
        startTimer(120); // 2 mins
    } else if (activeQuestionType === "Coding") {
        startTimer(1200); // 20 mins
    } else {
        startTimer(300); // 5 mins
    }

    lucide.createIcons();
}

// Called when language dropdown changes
function onLanguageChange() {
    const lang = document.getElementById('language-selector').value;
    const templateFn = LANG_TEMPLATES[lang] || LANG_TEMPLATES.python;
    document.getElementById('code-editor').value = templateFn(activePythonTemplate);
    document.getElementById('sandbox-lang-label').textContent = LANG_LABELS[lang] || 'Python 3';

    // Show note for non-Python languages
    const note = LANG_NOTE[lang];
    const outEl = document.getElementById('sandbox-out');
    if (note) {
        outEl.textContent = note + '\n\nSwitch to Python 3 for full sandbox execution support.';
        outEl.classList.add('error');
    } else {
        outEl.textContent = 'Python 3 selected. Click Run to execute your code against test cases.';
        outEl.classList.remove('error');
    }

    // Reset test case badges to "Ready"
    renderTestCases(activeTestCases);
}

function renderTestCases(testCases, results = null) {
    const container = document.getElementById("test-cases-list-panel");
    container.innerHTML = '';

    if (!testCases || testCases.length === 0) return;

    // Header bar with pass/fail counts
    const passCount = results ? results.filter(r => r.passed).length : 0;
    const failCount = results ? results.filter(r => !r.passed).length : 0;
    const headerBar = document.createElement('div');
    headerBar.className = 'test-cases-header-bar';
    if (results) {
        headerBar.innerHTML = `
            <span>Test Cases</span>
            <span style="display:flex; gap:0.4rem;">
                <span class="tc-count-pill pass">${passCount} Passed</span>
                <span class="tc-count-pill fail">${failCount} Failed</span>
            </span>
        `;
    } else {
        headerBar.innerHTML = `<span>Test Cases (${testCases.length})</span><span style="color:var(--text-muted); font-size:0.7rem;">Run code to evaluate</span>`;
    }
    container.appendChild(headerBar);

    testCases.forEach((tc, idx) => {
        const result = results ? results[idx] : null;
        const passed = result ? result.passed : null;

        const badge = document.createElement('div');
        badge.className = 'test-case-badge' + (result ? (passed ? ' passed' : ' failed') : '');

        // Top row: name + status pill
        const statusLabel = result ? (passed ? 'PASS' : 'FAIL') : 'READY';
        const statusClass = result ? (passed ? 'pass' : 'fail') : 'ready';
        badge.innerHTML = `
            <div class="tc-top-row">
                <span class="tc-name">${tc.name || `Case ${idx + 1}`}</span>
                <span class="tc-status-badge ${statusClass}">${statusLabel}</span>
            </div>
            <div class="tc-detail-row">
                <div class="tc-detail-item">
                    <span class="tc-label">Input</span>
                    <span class="tc-val" title="${tc.input}">${tc.input}</span>
                </div>
                <div class="tc-detail-item">
                    <span class="tc-label">Expected</span>
                    <span class="tc-val" title="${tc.expected}">${tc.expected}</span>
                </div>
                ${result ? `
                <div class="tc-detail-item">
                    <span class="tc-label">Actual</span>
                    <span class="tc-val ${passed ? 'actual-pass' : 'actual-fail'}" title="${result.actual || 'N/A'}">${result.actual || 'N/A'}</span>
                </div>` : ''}
            </div>
            ${(result && result.error) ? `<div class="tc-error-msg">${result.error}</div>` : ''}
        `;
        container.appendChild(badge);
    });
}

// Timer Logic
function startTimer(seconds) {
    if (timerInterval) clearInterval(timerInterval);
    
    secondsRemaining = seconds;
    updateTimerUI();

    timerInterval = setInterval(() => {
        secondsRemaining--;
        updateTimerUI();

        if (secondsRemaining <= 0) {
            clearInterval(timerInterval);
            // Auto submit when time runs out
            alert("Time's up! Submitting your answer automatically.");
            submitCandidateResponse();
        }
    }, 1000);
}

function updateTimerUI() {
    const mins = Math.floor(secondsRemaining / 60);
    const secs = secondsRemaining % 60;
    const timeStr = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    
    const clockVal = document.getElementById("countdown-timer-val");
    const badge = document.getElementById("countdown-badge");
    clockVal.textContent = timeStr;

    if (secondsRemaining < 30) {
        badge.classList.add("warning");
    } else {
        badge.classList.remove("warning");
    }
}

// Sandbox compilation run API
async function runSandboxCode() {
    const lang = document.getElementById('language-selector').value || 'python';
    
    // For non-Python, show a friendly note (execution only supported for Python)
    if (lang !== 'python') {
        const outEl = document.getElementById('sandbox-out');
        outEl.classList.add('error');
        outEl.textContent = `⚠️ Live sandbox execution is currently supported for Python 3 only.\n\nFor ${LANG_LABELS[lang]}: Please switch to Python 3 to run and test your code against the test cases.\n\nYou can still write your solution in ${LANG_LABELS[lang]} and submit it — the AI will evaluate your logic and code quality.`;
        return;
    }

    const code = document.getElementById("code-editor").value;
    const outputEl = document.getElementById("sandbox-out");
    const statsEl = document.getElementById("sandbox-stats");
    outputEl.textContent = "⏳ Running Python sandbox... executing test cases...";
    outputEl.classList.remove("error");
    statsEl.textContent = "";

    try {
        const response = await fetch("/api/coding/run-code", {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify({
                question_id: activeQuestionId,
                code: code,
                language: lang
            })
        });

        const data = await response.json();
        
        if (data.stderr) {
            outputEl.textContent = data.stderr;
            outputEl.classList.add("error");
            renderTestCases(activeTestCases); // Reset status
            statsEl.textContent = "";
        } else {
            const passedCount = data.passed_count ?? 0;
            const totalCount = data.total_count ?? 0;
            outputEl.textContent = data.stdout || "✅ Execution completed successfully.\n";
            outputEl.classList.remove("error");
            statsEl.textContent = `${passedCount}/${totalCount} passed · ${data.run_time} ms · ${data.memory_usage} MB`;
            
            // Highlight test cases with detailed results
            renderTestCases(activeTestCases, data.results);
        }
    } catch (err) {
        outputEl.textContent = "❌ Failed to communicate with code sandbox server.";
        outputEl.classList.add("error");
    }
}

// Submit answers to server
async function submitCandidateResponse() {
    if (timerInterval) clearInterval(timerInterval);

    const submitBtn = document.getElementById("submit-response-btn");
    submitBtn.disabled = true;
    submitBtn.textContent = "Evaluating...";

    let answerText = "";
    let endpoint = "/api/candidate/submit-answer";
    let bodyObj = {};

    if (activeQuestionType === "Coding") {
        endpoint = "/api/coding/submit-code";
        answerText = document.getElementById("code-editor").value;
        bodyObj = {
            question_id: activeQuestionId,
            code: answerText
        };
    } else {
        answerText = document.getElementById("answer-textbox").value;
        // Use voice transcript text if input is blank and speech recognition occurred
        const voiceLog = document.getElementById("voice-transcript-log").textContent;
        if (!answerText.trim() && voiceLog !== "Microphone inactive. Transcripts will generate here in real-time..." && voiceLog.trim()) {
            answerText = voiceLog;
        }

        bodyObj = {
            interview_id: activeInterviewId,
            question_id: activeQuestionId,
            candidate_answer: answerText || "No answer provided."
        };
    }

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: getAuthHeaders(),
            body: JSON.stringify(bodyObj)
        });

        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Answer";

        if (!response.ok) {
            alert("Failed to submit response. Please retry.");
            return;
        }

        const data = await response.json();

        // Show AI Feedback sheet modal
        showFeedbackModal(data);

    } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Answer";
        console.error("Submit response error:", err);
        alert("Network failure. Check internet connection.");
    }
}

function showFeedbackModal(evalData) {
    const fb = evalData.feedback;
    
    // Set score numbers
    document.getElementById("score-overall").textContent = fb.overall_score.toFixed(1);
    document.getElementById("score-technical").textContent = fb.technical_score.toFixed(1);
    document.getElementById("score-problem").textContent = fb.problem_solving_score.toFixed(1);
    document.getElementById("score-communication").textContent = fb.communication_score.toFixed(1);
    document.getElementById("score-confidence").textContent = fb.confidence_score.toFixed(1);

    // Apply color highlights based on values
    document.querySelectorAll(".score-num").forEach(num => {
        const val = parseFloat(num.textContent);
        if (val >= 8.5) {
            num.className = "score-num perfect";
        } else {
            num.className = "score-num";
        }
    });

    // Populate feedback blocks
    document.getElementById("feedback-correct-approach").innerHTML = fb.correct_approach || "N/A";
    document.getElementById("feedback-better-answer").innerHTML = fb.better_answer || "N/A";
    document.getElementById("feedback-fluency-grammar").innerHTML = `
        <strong>Grammar:</strong> ${fb.grammar_feedback || 'No comments.'}<br><br>
        <strong>Fluency:</strong> ${fb.fluency_feedback || 'No comments.'}
    `;
    document.getElementById("feedback-suggestions").innerHTML = fb.suggestions || "Practice consistently.";

    // Configure the modal action button to load next question or exit
    const actionBtn = document.getElementById("close-feedback-action-btn");
    
    if (evalData.interview_completed) {
        actionBtn.textContent = "Close and View Dashboard";
        actionBtn.onclick = () => {
            closeFeedbackModal();
            loadDashboardMetrics();
            loadHistoryList();
            switchView('dashboard');
        };
    } else {
        actionBtn.textContent = "Next Question";
        actionBtn.onclick = () => {
            closeFeedbackModal();
            loadQuestionData(evalData.next_question);
        };
    }

    document.getElementById("feedback-overlay").classList.add("active");
    lucide.createIcons();
}

function closeFeedbackModal() {
    document.getElementById("feedback-overlay").classList.remove("active");
}

function abortInterviewSession() {
    if (confirm("Are you sure you want to abort? Current progress in this session will not be saved.")) {
        if (timerInterval) clearInterval(timerInterval);
        switchView('dashboard');
    }
}

// History aggregation lists
async function loadHistoryList() {
    const body = document.getElementById("history-rows-body");
    
    try {
        const response = await fetch("/api/candidate/history", {
            headers: getAuthHeaders()
        });

        if (!response.ok) return;
        const history = await response.json();

        body.innerHTML = "";
        if (history.length === 0) {
            body.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                        No interview history found. Go to 'Start Interview' to practice!
                    </td>
                </tr>
            `;
            return;
        }

        history.forEach(item => {
            const row = document.createElement("tr");
            row.className = "history-row";

            // Format date
            const dateStr = new Date(item.created_at).toLocaleDateString(undefined, {
                year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            // If score is 0 and status is InProgress, show N/A
            const scoreStr = item.status === "InProgress" ? "InProgress" : item.total_score.toFixed(1);

            row.innerHTML = `
                <td>${dateStr}</td>
                <td style="font-weight: 600;">${item.role_type}</td>
                <td><span class="tag-badge strong" style="font-size:0.75rem;">${item.difficulty}</span></td>
                <td>${item.interview_type}</td>
                <td style="font-weight: bold; color: var(--primary);">${scoreStr}</td>
                <td><span style="font-size: 0.8rem; font-weight: 600; color: ${item.status === 'Completed' ? 'var(--success)' : 'var(--warning)'}">${item.status}</span></td>
                <td>
                    <button class="glass-button" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;" onclick="viewHistoryItemDetails(${item.id})" ${item.status !== 'Completed' ? 'disabled' : ''}>
                        Review Feedback
                    </button>
                </td>
            `;
            body.appendChild(row);
        });

    } catch (err) {
        console.error("Error loading interview history list:", err);
    }
}

async function viewHistoryItemDetails(interviewId) {
    // Show static aggregates for this historical interview
    // For a finished interview, we can pull the scores directly from the history item
    try {
        const response = await fetch("/api/candidate/history", {
            headers: getAuthHeaders()
        });

        if (!response.ok) return;
        const history = await response.json();
        const item = history.find(i => i.id === interviewId);
        
        if (item) {
            // Render basic cumulative parameters in the feedback modal for the candidate
            const fakeData = {
                interview_completed: true,
                feedback: {
                    overall_score: item.total_score,
                    technical_score: Math.max(1.0, item.total_score - 0.2),
                    problem_solving_score: item.total_score,
                    communication_score: Math.min(10.0, item.total_score + 0.3),
                    confidence_score: Math.min(10.0, item.total_score + 0.1),
                    correct_approach: "This feedback sheet shows the aggregated score card of this historical interview session.",
                    better_answer: "To view question-by-question metrics, start a new interview session and complete the answers step-by-step.",
                    grammar_feedback: "Aggregated rating history saved.",
                    fluency_feedback: "Pacing was consistent across the session.",
                    suggestions: "Review your strong and weak topics on the main dashboard tab to focus your efforts."
                }
            };
            showFeedbackModal(fakeData);
        }
    } catch (e) {
        console.error(e);
    }
}
