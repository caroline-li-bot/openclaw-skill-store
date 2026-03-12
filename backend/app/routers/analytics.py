from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.get("/stats", response_model=schemas.MarketplaceStats)
def get_marketplace_stats(
    db: Session = Depends(get_db)
):
    """Get overall marketplace statistics"""
    return crud.get_marketplace_stats(db)

@router.post("/track/view/{skill_id}", status_code=200)
def track_skill_view(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Track a skill view event"""
    # Get client info
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    referrer = request.headers.get("referer")
    
    # Record event
    crud.record_analytics_event(
        db,
        event_type="view",
        skill_id=skill_id,
        user_agent=user_agent,
        ip_address=ip_address,
        referrer=referrer
    )
    
    return {"status": "success"}

@router.post("/track/download/{skill_id}", status_code=200)
def track_skill_download(
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Track a skill download event"""
    # Get client info
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    referrer = request.headers.get("referer")
    
    # Record event
    crud.record_analytics_event(
        db,
        event_type="download",
        skill_id=skill_id,
        user_agent=user_agent,
        ip_address=ip_address,
        referrer=referrer
    )
    
    return {"status": "success"}

@router.post("/track/search", status_code=200)
def track_search(
    query: str,
    request: Request,
    results_count: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Track a search event"""
    # Get client info
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    referrer = request.headers.get("referer")
    
    # Record event
    crud.record_analytics_event(
        db,
        event_type="search",
        search_query=query,
        user_agent=user_agent,
        ip_address=ip_address,
        referrer=referrer
    )
    
    return {"status": "success"}

@router.post("/track/workflow/use/{workflow_id}", status_code=200)
def track_workflow_use(
    workflow_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Track a workflow usage event"""
    # Get client info
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    referrer = request.headers.get("referer")
    
    # Record event
    crud.record_analytics_event(
        db,
        event_type="workflow_use",
        workflow_id=workflow_id,
        user_agent=user_agent,
        ip_address=ip_address,
        referrer=referrer
    )
    
    return {"status": "success"}

@router.get("/usage/skills/top")
def get_top_skills(
    metric: str = Query("downloads", description="Metric to sort by (downloads, views)"),
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db)
):
    """Get top skills by usage metric"""
    if metric == "downloads":
        skills = crud.get_skills(
            db,
            limit=limit,
            sort_by="download_count",
            sort_order="desc"
        )
    elif metric == "views":
        skills = crud.get_skills(
            db,
            limit=limit,
            sort_by="view_count",
            sort_order="desc"
        )
    else:
        skills = crud.get_trending_skills(db, limit=limit)
    
    return [
        {
            "id": skill.id,
            "name": skill.name,
            "slug": skill.slug,
            "author": skill.author,
            "download_count": skill.download_count,
            "view_count": skill.view_count,
            "security_score": skill.security_score
        }
        for skill in skills
    ]

@router.get("/usage/overview")
def get_usage_overview(
    days: int = Query(30, ge=1, le=365, description="Time period in days"),
    db: Session = Depends(get_db)
):
    """Get usage overview statistics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get total events in period
    from ..models import AnalyticsEvent
    
    total_views = db.query(AnalyticsEvent)\
        .filter(AnalyticsEvent.event_type == "view")\
        .filter(AnalyticsEvent.created_at >= start_date)\
        .count()
    
    total_downloads = db.query(AnalyticsEvent)\
        .filter(AnalyticsEvent.event_type == "download")\
        .filter(AnalyticsEvent.created_at >= start_date)\
        .count()
    
    total_searches = db.query(AnalyticsEvent)\
        .filter(AnalyticsEvent.event_type == "search")\
        .filter(AnalyticsEvent.created_at >= start_date)\
        .count()
    
    total_workflow_uses = db.query(AnalyticsEvent)\
        .filter(AnalyticsEvent.event_type == "workflow_use")\
        .filter(AnalyticsEvent.created_at >= start_date)\
        .count()
    
    # Get daily trends (last 7 days)
    daily_data = []
    for i in range(7):
        day = end_date - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_views = db.query(AnalyticsEvent)\
            .filter(AnalyticsEvent.event_type == "view")\
            .filter(AnalyticsEvent.created_at >= day_start)\
            .filter(AnalyticsEvent.created_at < day_end)\
            .count()
        
        day_downloads = db.query(AnalyticsEvent)\
            .filter(AnalyticsEvent.event_type == "download")\
            .filter(AnalyticsEvent.created_at >= day_start)\
            .filter(AnalyticsEvent.created_at < day_end)\
            .count()
        
        daily_data.append({
            "date": day.strftime("%Y-%m-%d"),
            "views": day_views,
            "downloads": day_downloads
        })
    
    return {
        "period_days": days,
        "total_views": total_views,
        "total_downloads": total_downloads,
        "total_searches": total_searches,
        "total_workflow_uses": total_workflow_uses,
        "daily_trends": list(reversed(daily_data))
    }
