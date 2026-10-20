import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/")
async def root():
    return {
        "name": "NextRole API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }
