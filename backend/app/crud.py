from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from . import models, schemas
from .scanner.security_scanner import SecurityScanner

# Category CRUD
def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def get_category_by_slug(db: Session, slug: str) -> Optional[models.Category]:
    return db.query(models.Category).filter(models.Category.slug == slug).first()

def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    return db.query(models.Category).order_by(models.Category.name).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# Skill CRUD
def get_skill(db: Session, skill_id: int) -> Optional[models.Skill]:
    return db.query(models.Skill).filter(models.Skill.id == skill_id).first()

def get_skill_by_slug(db: Session, slug: str) -> Optional[models.Skill]:
    return db.query(models.Skill).filter(models.Skill.slug == slug).first()

def get_skill_by_repository(db: Session, repository: str) -> Optional[models.Skill]:
    return db.query(models.Skill).filter(models.Skill.repository == repository).first()

def get_skills(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    author: Optional[str] = None,
    is_verified: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    min_security_score: Optional[float] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> List[models.Skill]:
    query = db.query(models.Skill)
    
    if category_id is not None:
        query = query.filter(models.Skill.category_id == category_id)
    if author is not None:
        query = query.filter(models.Skill.author == author)
    if is_verified is not None:
        query = query.filter(models.Skill.is_verified == is_verified)
    if is_featured is not None:
        query = query.filter(models.Skill.is_featured == is_featured)
    if min_security_score is not None:
        query = query.filter(models.Skill.security_score >= min_security_score)
    
    # Sorting
    if sort_order == "desc":
        query = query.order_by(desc(getattr(models.Skill, sort_by, models.Skill.created_at)))
    else:
        query = query.order_by(asc(getattr(models.Skill, sort_by, models.Skill.created_at)))
    
    return query.offset(skip).limit(limit).all()

def get_trending_skills(db: Session, limit: int = 10) -> List[models.Skill]:
    """Get trending skills based on recent downloads/views"""
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # For MVP, just return most downloaded skills
    return db.query(models.Skill)\
        .order_by(desc(models.Skill.download_count))\
        .limit(limit)\
        .all()

def get_popular_skills(db: Session, limit: int = 10) -> List[models.Skill]:
    """Get most popular skills by star count"""
    return db.query(models.Skill)\
        .order_by(desc(models.Skill.star_count))\
        .limit(limit)\
        .all()

def get_newest_skills(db: Session, limit: int = 10) -> List[models.Skill]:
    """Get recently added skills"""
    return db.query(models.Skill)\
        .order_by(desc(models.Skill.created_at))\
        .limit(limit)\
        .all()

def create_skill(db: Session, skill: schemas.SkillCreate) -> models.Skill:
    db_skill = models.Skill(**skill.model_dump())
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

def update_skill(db: Session, skill_id: int, skill_update: schemas.SkillUpdate) -> Optional[models.Skill]:
    db_skill = get_skill(db, skill_id)
    if not db_skill:
        return None
    
    update_data = skill_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_skill, field, value)
    
    db_skill.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_skill)
    return db_skill

def increment_skill_downloads(db: Session, skill_id: int) -> None:
    db_skill = get_skill(db, skill_id)
    if db_skill:
        db_skill.download_count += 1
        db.commit()

def increment_skill_views(db: Session, skill_id: int) -> None:
    db_skill = get_skill(db, skill_id)
    if db_skill:
        db_skill.view_count += 1
        db.commit()

# Security Scan CRUD
def get_security_scans_for_skill(
    db: Session,
    skill_id: int,
    skip: int = 0,
    limit: int = 10
) -> List[models.SecurityScan]:
    return db.query(models.SecurityScan)\
        .filter(models.SecurityScan.skill_id == skill_id)\
        .order_by(desc(models.SecurityScan.scanned_at))\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_latest_security_scan(db: Session, skill_id: int) -> Optional[models.SecurityScan]:
    return db.query(models.SecurityScan)\
        .filter(models.SecurityScan.skill_id == skill_id)\
        .order_by(desc(models.SecurityScan.scanned_at))\
        .first()

def create_security_scan(
    db: Session,
    skill_id: int,
    scan: schemas.SecurityScanCreate
) -> models.SecurityScan:
    db_scan = models.SecurityScan(skill_id=skill_id, **scan.model_dump())
    db.add(db_scan)
    
    # Update skill security score
    db_skill = get_skill(db, skill_id)
    if db_skill:
        db_skill.security_score = scan.score
        db_skill.security_risk_level = scan.risk_level
    
    db.commit()
    db.refresh(db_scan)
    return db_scan

# Workflow Template CRUD
def get_workflow_template(db: Session, workflow_id: int) -> Optional[models.WorkflowTemplate]:
    return db.query(models.WorkflowTemplate).filter(models.WorkflowTemplate.id == workflow_id).first()

def get_workflow_templates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_featured: Optional[bool] = None
) -> List[models.WorkflowTemplate]:
    query = db.query(models.WorkflowTemplate)
    
    if category is not None:
        query = query.filter(models.WorkflowTemplate.category == category)
    if is_featured is not None:
        query = query.filter(models.WorkflowTemplate.is_featured == is_featured)
    
    return query.order_by(desc(models.WorkflowTemplate.usage_count)).offset(skip).limit(limit).all()

def create_workflow_template(
    db: Session,
    workflow: schemas.WorkflowTemplateCreate
) -> models.WorkflowTemplate:
    db_workflow = models.WorkflowTemplate(**workflow.model_dump())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

def increment_workflow_usage(db: Session, workflow_id: int) -> None:
    db_workflow = get_workflow_template(db, workflow_id)
    if db_workflow:
        db_workflow.usage_count += 1
        db.commit()

# Analytics and Stats
def get_marketplace_stats(db: Session) -> Dict[str, Any]:
    """Get overall marketplace statistics"""
    total_skills = db.query(func.count(models.Skill.id)).scalar()
    total_categories = db.query(func.count(models.Category.id)).scalar()
    total_workflows = db.query(func.count(models.WorkflowTemplate.id)).scalar()
    total_downloads = db.query(func.sum(models.Skill.download_count)).scalar() or 0
    total_views = db.query(func.sum(models.Skill.view_count)).scalar() or 0
    
    trending_skills = get_trending_skills(db, limit=5)
    popular_categories = db.query(models.Category)\
        .order_by(desc(models.Category.skill_count))\
        .limit(5)\
        .all()
    
    return {
        "total_skills": total_skills,
        "total_categories": total_categories,
        "total_workflows": total_workflows,
        "total_downloads": total_downloads,
        "total_views": total_views,
        "trending_skills": trending_skills,
        "popular_categories": popular_categories
    }

def record_analytics_event(
    db: Session,
    event_type: str,
    skill_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    user_agent: Optional[str] = None,
    ip_address: Optional[str] = None,
    referrer: Optional[str] = None,
    search_query: Optional[str] = None
) -> models.AnalyticsEvent:
    """Record an analytics event"""
    event = models.AnalyticsEvent(
        event_type=event_type,
        skill_id=skill_id,
        workflow_id=workflow_id,
        user_agent=user_agent,
        ip_address=ip_address,
        referrer=referrer,
        search_query=search_query
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
