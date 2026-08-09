import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.app.database.connection import engine, Base
from backend.app.routes import auth, candidate, coding, voice

# Automatically create all SQLite database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Preparation Platform",
    description="A production-ready platform to prepare candidates for software engineering interviews.",
    version="1.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(candidate.router)
app.include_router(coding.router)
app.include_router(voice.router)

# Mount frontend static directory if it exists
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
static_dir = os.path.join(frontend_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    """Serves the index.html SPA entrypoint."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "online",
        "message": "AI Interview Platform API is running. Frontend index.html not found.",
        "api_docs": "/docs"
    }
