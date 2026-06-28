# AI Interview Preparation Platform

A production-ready, full-stack AI-powered preparation platform for technical, coding, and behavioral interviews. Designed with a clean three-tier architecture, a responsive dark glassmorphic single-page application (SPA) client, automatic SQLite table migration, and secure local subprocess code execution tests.

---

## Technical Stack & Architecture

### Backend
* **Python 3.12+**
* **FastAPI**: Robust, asynchronous high-performance REST API routing.
* **SQLAlchemy ORM**: Entity mapping for SQLite database storage.
* **SQLite**: Single-file structured storage.
* **Pydantic v2**: High-speed schema model parsing and request validations.
* **PyJWT / Python-Jose**: Token-based JSON Web Signature creation and security.
* **Passlib + BCrypt**: Heavy-duty password cryptographic hashing.

### Frontend
* **Vanilla HTML5, CSS3, & JavaScript (ES6+)**: Fast, framework-free modular SPA structure.
* **Glassmorphism Theme System**: High-fidelity dark space aesthetics using translucent panels, glowing custom accent borders, and micro-interactions.
* **Web Speech API**: Browser-native real-time vocal transcript processing.

### AI Integration
* Supports both **Gemini API (`gemini-1.5-flash`)** and **OpenAI API (`gpt-3.5-turbo`)**.
* Implements a detailed **Mock Mode** for offline demo capability out-of-the-box (no keys required).

---

## Features

1. **JWT-secured Authentication**: Secure registrations and logins with optional session remember configurations (7-day longevity).
2. **Adaptive Candidate Dashboard**: Summary stats of total mock practice exams, overall score aggregates, and personal best grades. Shows dynamic strong/weak tags and progress.
3. **Interactive Session Configurator**: Custom setups selecting focus roles (Software/Frontend/Backend Developer, Data Analyst, etc.), difficulty levels (Easy, Medium, Hard), exam types (HR, Technical, Coding, Mixed), and questions count (5, 10, or 20).
4. **LeetCode-style Coding Sandbox**: Code editor panel supporting real-time sandbox execution. Code is evaluated against standard test suites in an isolated timed process.
5. **Speech Recognition**: Voice evaluations processing vocal answers via browser microphones with transcript preview panels.
6. **Granular AI Evaluations**: Question-by-question scoring indices: Overall score, communication pacing, correctness, suggestions, grammar/fluency checks, and model answers.
7. **Achievements System**: Dynamic badges ("First Step", "Star Candidate", "Consistent Scholar") that unlock automatically upon meeting goals.
8. **Interactive Leaderboard**: Competitive standing system computing scores from completed interviews and average ratings.

---

## Project Layout

```
AI-Interview-Platform/
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   │   └── auth_service.py       # Hashing and JWT auth verification
│   │   ├── database/
│   │   │   └── connection.py         # SQLAlchemy engine setups
│   │   ├── models/
│   │   │   └── database_models.py    # Tables schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # /api/auth routes
│   │   │   ├── candidate.py          # Dashboard and start interview routes
│   │   │   ├── coding.py             # Code evaluation sandbox routes
│   │   │   └── voice.py              # Audio evaluation routes
│   │   ├── schemas/
│   │   │   └── api_schemas.py        # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ai_service.py         # Gemini / OpenAI wrappers
│   │   │   └── code_runner.py        # Subprocess compilation runner
│   │   ├── config.py                 # Pydantic settings manager
│   │   └── main.py                   # FastAPI init and Static mount
│   └── requirements.txt              # Backend packages
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css            # Glassmorphism dark-theme style
│   │   └── js/
│   │       ├── app.js                # Routing orchestration
│   │       ├── auth.js               # Login and register controller
│   │       ├── dashboard.js          # Dashboard aggregator loader
│   │       ├── interview.js          # Interview progressions and sandboxing
│   │       └── voice.js              # Microphone Web Speech wrappers
│   └── index.html                    # Single Page App layout
├── .env                              # Environment variables config
└── README.md
```

---

## Installation & Local Execution

### 1. Clone & Set Up Directory
Open your terminal (PowerShell/Bash) in the workspace directory.

### 2. Install Python Dependencies
Install the required libraries listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Configure the Environment
Create/edit the `.env` file in the root directory:
```env
# Supported providers: 'gemini', 'openai', 'mock'
# If set to 'mock', the platform generates rich simulated responses without calling external services.
AI_PROVIDER=mock
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key
```

### 4. Boot the FastAPI Server
Run the FastAPI development server:
```bash
uvicorn backend.app.main:app --reload
```
* The SQLite database folder and structure tables migrate automatically upon server launch.
* The application runs locally at `http://127.0.0.1:8000`.

### 5. Access and Authenticate
* Open `http://127.0.0.1:8000` in Google Chrome or Microsoft Edge.
* Click **Register** to create a candidate profile, then sign in.
* For visual REST API schema walkthroughs, view Swagger docs at `http://127.0.0.1:8000/docs`.

---

## Security Configurations
* **Token validation**: Uses JWT tokens with 1440-minute expirations (7 days if "Remember Me" is activated).
* **Cryptographic hashes**: Salting and password encryption using BCrypt.
* **SQL Injection protection**: Handled via SQLAlchemy parameter bindings.
* **Malicious Script checks**: Standalone AST token analysis blocks system imports (`os`, `sys`, `subprocess`) from running inside the coding sandbox.
* **Rate Limits**: Code executions apply strict timeout constraints (3.0 seconds maximum) preventing thread locking from infinite loops.

---

## Future Enhancements
* **WASM Sandboxes**: Run client code execution in Pyodide/WebAssembly inside the browser context rather than server processes.
* **PDF Report Exports**: Print comprehensive score feedback analysis to local PDFs using ReportLab.
* **Real-time Audio Streams**: Continuous websocket voice stream transcript analysis.
.\.venv\Scripts\uvicorn.exe backend.app.main:app --reload