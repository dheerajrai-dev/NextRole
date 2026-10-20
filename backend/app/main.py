import os
import sys
from pathlib import Path

# Ensure backend directory is in sys.path regardless of where command is run
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes.search import router as search_router

# Load environment variables from project root .env regardless of working directory
root_dir = Path(__file__).resolve().parent.parent.parent
env_path = root_dir / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv(override=True)

app = FastAPI(
    title="NextRole API",
    description="Unified Job & Internship Finder powered by TinyFish Web API",
    version="0.1.0",
)

# CORS configuration
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
allowed_origins = list({
    frontend_url,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)

# Mount frontend/dist if built, providing single-command full-stack runtime
dist_dir = root_dir / "frontend" / "dist"
if dist_dir.exists() and (dist_dir / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=dist_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes or docs
        if full_path.startswith("api/") or full_path in ("docs", "openapi.json", "redoc"):
            return None
        file_target = dist_dir / full_path
        if file_target.exists() and file_target.is_file():
            return FileResponse(file_target)
        return FileResponse(dist_dir / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "name": "NextRole API",
            "version": "0.1.0",
            "status": "running",
            "docs": "/docs",
            "health": "/api/health",
            "frontend": "Run 'npm run dev' inside frontend/ to start the UI dev server.",
        }
