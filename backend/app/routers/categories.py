from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()

@router.get("", response_model=List[schemas.Category])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List all skill categories"""
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=schemas.Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get category details by ID"""
    category = crud.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.get("/slug/{category_slug}", response_model=schemas.Category)
def get_category_by_slug(
    category_slug: str,
    db: Session = Depends(get_db)
):
    """Get category details by slug"""
    category = crud.get_category_by_slug(db, slug=category_slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.get("/{category_id}/skills", response_model=List[schemas.Skill])
def get_category_skills(
    category_id: int,
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("created_at", description="Sort by field (created_at, download_count, star_count, name)"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """Get all skills in a category"""
    category = crud.get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    skills = crud.get_skills(
        db,
        category_id=category_id,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return skills

@router.post("", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    # Check if category with same slug already exists
    db_category = crud.get_category_by_slug(db, slug=category.slug)
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this slug already exists"
        )
    
    return crud.create_category(db=db, category=category)
