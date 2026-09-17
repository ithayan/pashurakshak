"""
PashuRakshak AI Core - FastAPI Main Application
===============================================
"""

import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.api.predict import router as predict_router
from app.api.video import router as video_router
from app.api.triage import router as triage_router
from app.api.rag import router as rag_router
from app.api.health import router as health_router

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Farmer PWA and Veterinary Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health_router)
app.include_router(predict_router)
app.include_router(video_router)
app.include_router(triage_router)
app.include_router(rag_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to PashuRakshak (पशुरक्षक) AI Core API",
        "docs": "/docs",
        "health": "/health",
        "supported_languages": ["mr (मराठी)", "hi (हिन्दी)", "en (English)"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
