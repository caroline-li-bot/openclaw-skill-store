from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()

@router.get("", response_model=List[schemas.WorkflowTemplate])
def list_workflows(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """List all workflow templates"""
    workflows = crud.get_workflow_templates(
        db,
        skip=skip,
        limit=limit,
        category=category,
        is_featured=is_featured
    )
    return workflows

@router.get("/featured", response_model=List[schemas.WorkflowTemplate])
def get_featured_workflows(
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    db: Session = Depends(get_db)
):
    """Get featured workflow templates"""
    return crud.get_workflow_templates(db, is_featured=True, limit=limit)

@router.get("/{workflow_id}", response_model=schemas.WorkflowTemplate)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Get workflow template details by ID"""
    workflow = crud.get_workflow_template(db, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    return workflow

@router.post("", response_model=schemas.WorkflowTemplate, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow: schemas.WorkflowTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new workflow template"""
    return crud.create_workflow_template(db=db, workflow=workflow)

@router.post("/{workflow_id}/use", status_code=status.HTTP_200_OK)
def record_workflow_usage(
    workflow_id: int,
    db: Session = Depends(get_db)
):
    """Record workflow usage increment"""
    workflow = crud.get_workflow_template(db, workflow_id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    
    crud.increment_workflow_usage(db, workflow_id=workflow_id)
    return {
        "status": "success",
        "message": "Usage recorded",
        "workflow": workflow.name,
        "required_skills": workflow.required_skills,
        "steps": workflow.steps
    }
