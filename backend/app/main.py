from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import SessionLocal, engine
from .routers import skills, categories, security, search, workflows, analytics

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OpenClaw Skill Store API",
    description="Backend API for the OpenClaw Skill Store marketplace",
    version="1.0.0",
    contact={
        "name": "OpenClaw Team",
        "url": "https://github.com/openclaw",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(security.router, prefix="/api/security", tags=["security"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

add_pagination(app)

@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "OpenClaw Skill Store API is running"
    }

@app.get("/api/stats", tags=["stats"])
async def get_stats(db: Session = Depends(get_db)):
    """Get marketplace statistics"""
    stats = crud.get_marketplace_stats(db)
    return stats
