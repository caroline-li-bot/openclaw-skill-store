from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi_pagination import Page, paginate

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()

@router.get("", response_model=Page[schemas.Skill])
def list_skills(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    author: Optional[str] = Query(None, description="Filter by author"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    min_security_score: Optional[float] = Query(None, ge=0, le=10, description="Minimum security score"),
    sort_by: str = Query("created_at", description="Sort by field (created_at, download_count, star_count, name)"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """List all skills with optional filters"""
    skills = crud.get_skills(
        db,
        category_id=category_id,
        author=author,
        is_verified=is_verified,
        is_featured=is_featured,
        min_security_score=min_security_score,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return paginate(skills)

@router.get("/trending", response_model=List[schemas.Skill])
def get_trending_skills(
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Get trending skills"""
    return crud.get_trending_skills(db, limit=limit)

@router.get("/popular", response_model=List[schemas.Skill])
def get_popular_skills(
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Get most popular skills by star count"""
    return crud.get_popular_skills(db, limit=limit)

@router.get("/newest", response_model=List[schemas.Skill])
def get_newest_skills(
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Get recently added skills"""
    return crud.get_newest_skills(db, limit=limit)

@router.get("/{skill_id}", response_model=schemas.Skill)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """Get skill details by ID"""
    skill = crud.get_skill(db, skill_id=skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Increment view count
    crud.increment_skill_views(db, skill_id=skill_id)
    return skill

@router.get("/slug/{skill_slug}", response_model=schemas.Skill)
def get_skill_by_slug(
    skill_slug: str,
    db: Session = Depends(get_db)
):
    """Get skill details by slug"""
    skill = crud.get_skill_by_slug(db, slug=skill_slug)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Increment view count
    crud.increment_skill_views(db, skill_id=skill.id)
    return skill

@router.post("", response_model=schemas.Skill, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill: schemas.SkillCreate,
    db: Session = Depends(get_db)
):
    """Create a new skill"""
    # Check if skill with same repository already exists
    db_skill = crud.get_skill_by_repository(db, repository=str(skill.repository))
    if db_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill with this repository already exists"
        )
    
    # Check if skill with same slug already exists
    db_skill = crud.get_skill_by_slug(db, slug=skill.slug)
    if db_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Skill with this slug already exists"
        )
    
    return crud.create_skill(db=db, skill=skill)

@router.patch("/{skill_id}", response_model=schemas.Skill)
def update_skill(
    skill_id: int,
    skill_update: schemas.SkillUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing skill"""
    db_skill = crud.update_skill(db, skill_id=skill_id, skill_update=skill_update)
    if not db_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    return db_skill

@router.post("/{skill_id}/install", status_code=status.HTTP_200_OK)
def record_install(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """Record a skill installation"""
    skill = crud.get_skill(db, skill_id=skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    crud.increment_skill_downloads(db, skill_id=skill_id)
    return {
        "status": "success",
        "message": "Installation recorded",
        "install_command": skill.install_command
    }

@router.get("/{skill_id}/security-scans", response_model=List[schemas.SecurityScan])
def get_skill_security_scans(
    skill_id: int,
    limit: int = Query(10, ge=1, le=100, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Get security scan history for a skill"""
    skill = crud.get_skill(db, skill_id=skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    return crud.get_security_scans_for_skill(db, skill_id=skill_id, limit=limit)

@router.get("/{skill_id}/usage-examples", response_model=List[schemas.UsageExample])
def get_skill_usage_examples(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """Get usage examples for a skill"""
    skill = crud.get_skill(db, skill_id=skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    return skill.usage_examples
