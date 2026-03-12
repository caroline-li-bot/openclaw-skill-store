from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import meilisearch
from meilisearch.errors import MeilisearchApiError

from .. import crud, models, schemas
from ..database import get_db, settings

router = APIRouter()

# Initialize Meilisearch client
meilisearch_client = meilisearch.Client(
    settings.MEILISEARCH_URL,
    settings.MEILISEARCH_API_KEY
)

def get_meilisearch_index():
    """Get or create Meilisearch index for skills"""
    try:
        index = meilisearch_client.index("skills")
        # Configure index settings
        index.update_settings({
            "searchableAttributes": [
                "name",
                "description",
                "long_description",
                "author",
                "required_tools",
                "category_name"
            ],
            "filterableAttributes": [
                "category_id",
                "author",
                "is_verified",
                "is_featured",
                "security_score",
                "security_risk_level"
            ],
            "sortableAttributes": [
                "download_count",
                "star_count",
                "created_at",
                "updated_at"
            ]
        })
        return index
    except MeilisearchApiError as e:
        print(f"Meilisearch error: {e}")
        return None

def index_skill(skill: models.Skill) -> None:
    """Index a skill in Meilisearch"""
    index = get_meilisearch_index()
    if not index:
        return
    
    document = {
        "id": skill.id,
        "name": skill.name,
        "slug": skill.slug,
        "description": skill.description,
        "long_description": skill.long_description,
        "author": skill.author,
        "repository": str(skill.repository),
        "homepage": str(skill.homepage) if skill.homepage else None,
        "required_tools": skill.required_tools or [],
        "category_id": skill.category_id,
        "category_name": skill.category.name if skill.category else None,
        "download_count": skill.download_count,
        "star_count": skill.star_count,
        "security_score": skill.security_score,
        "security_risk_level": skill.security_risk_level,
        "is_verified": skill.is_verified,
        "is_featured": skill.is_featured,
        "created_at": skill.created_at.isoformat(),
        "updated_at": skill.updated_at.isoformat()
    }
    
    try:
        index.add_documents([document])
    except MeilisearchApiError as e:
        print(f"Failed to index skill {skill.id}: {e}")

def bulk_index_skills(skills: List[models.Skill]) -> None:
    """Bulk index multiple skills"""
    index = get_meilisearch_index()
    if not index:
        return
    
    documents = []
    for skill in skills:
        documents.append({
            "id": skill.id,
            "name": skill.name,
            "slug": skill.slug,
            "description": skill.description,
            "long_description": skill.long_description,
            "author": skill.author,
            "repository": str(skill.repository),
            "homepage": str(skill.homepage) if skill.homepage else None,
            "required_tools": skill.required_tools or [],
            "category_id": skill.category_id,
            "category_name": skill.category.name if skill.category else None,
            "download_count": skill.download_count,
            "star_count": skill.star_count,
            "security_score": skill.security_score,
            "security_risk_level": skill.security_risk_level,
            "is_verified": skill.is_verified,
            "is_featured": skill.is_featured,
            "created_at": skill.created_at.isoformat(),
            "updated_at": skill.updated_at.isoformat()
        })
    
    try:
        index.add_documents(documents)
    except MeilisearchApiError as e:
        print(f"Failed to bulk index skills: {e}")

@router.get("", response_model=schemas.SearchResponse)
def search_skills(
    q: str = Query(..., description="Search query", min_length=1),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    author: Optional[str] = Query(None, description="Filter by author"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    min_security_score: Optional[float] = Query(None, ge=0, le=10, description="Minimum security score"),
    sort_by: str = Query("relevance", description="Sort by (relevance, download_count, star_count, created_at)"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Search skills with filters"""
    index = get_meilisearch_index()
    
    # Build filter conditions
    filter_conditions = []
    if category_id is not None:
        filter_conditions.append(f"category_id = {category_id}")
    if author is not None:
        filter_conditions.append(f"author = '{author}'")
    if is_verified is not None:
        filter_conditions.append(f"is_verified = {str(is_verified).lower()}")
    if is_featured is not None:
        filter_conditions.append(f"is_featured = {str(is_featured).lower()}")
    if min_security_score is not None:
        filter_conditions.append(f"security_score >= {min_security_score}")
    
    filter_string = " AND ".join(filter_conditions) if filter_conditions else None
    
    # Build sort parameters
    sort_params = []
    if sort_by != "relevance":
        sort_direction = "desc" if sort_order == "desc" else "asc"
        sort_params.append(f"{sort_by}:{sort_direction}")
    
    try:
        if index:
            # Use Meilisearch for full-text search
            search_params = {
                "limit": limit,
                "offset": offset,
                "filter": filter_string,
                "sort": sort_params,
                "show_ranking_score": True
            }
            
            results = index.search(q, search_params)
            
            # Get full skill details from database
            skill_ids = [hit["id"] for hit in results["hits"]]
            skills = []
            for skill_id in skill_ids:
                skill = crud.get_skill(db, skill_id=skill_id)
                if skill:
                    skills.append(skill)
            
            # Format response
            search_results = []
            for skill, hit in zip(skills, results["hits"]):
                search_results.append({
                    "type": "skill",
                    "item": schemas.Skill.from_orm(skill).dict(),
                    "score": hit.get("_rankingScore", 0.0)
                })
            
            return {
                "results": search_results,
                "total": results["estimatedTotalHits"],
                "took_ms": results["processingTimeMs"]
            }
        else:
            # Fallback to database search if Meilisearch is not available
            skills = crud.get_skills(
                db,
                skip=offset,
                limit=limit,
                category_id=category_id,
                author=author,
                is_verified=is_verified,
                is_featured=is_featured,
                min_security_score=min_security_score,
                sort_by=sort_by if sort_by != "relevance" else "created_at",
                sort_order=sort_order
            )
            
            # Simple keyword filter on name and description
            filtered_skills = []
            for skill in skills:
                if q.lower() in skill.name.lower() or (skill.description and q.lower() in skill.description.lower()):
                    filtered_skills.append(skill)
            
            search_results = [
                {
                    "type": "skill",
                    "item": schemas.Skill.from_orm(skill).dict(),
                    "score": 1.0
                }
                for skill in filtered_skills
            ]
            
            return {
                "results": search_results,
                "total": len(filtered_skills),
                "took_ms": 0
            }
    
    except Exception as e:
        # Fallback to database search on error
        skills = crud.get_skills(
            db,
            skip=offset,
            limit=limit,
            category_id=category_id,
            author=author,
            is_verified=is_verified,
            is_featured=is_featured,
            min_security_score=min_security_score,
            sort_by=sort_by if sort_by != "relevance" else "created_at",
            sort_order=sort_order
        )
        
        filtered_skills = []
        for skill in skills:
            if q.lower() in skill.name.lower() or (skill.description and q.lower() in skill.description.lower()):
                filtered_skills.append(skill)
        
        search_results = [
            {
                "type": "skill",
                "item": schemas.Skill.from_orm(skill).dict(),
                "score": 1.0
            }
            for skill in filtered_skills
        ]
        
        return {
            "results": search_results,
            "total": len(filtered_skills),
            "took_ms": 0
        }

@router.post("/reindex", status_code=status.HTTP_202_ACCEPTED)
async def reindex_all_skills(
    db: Session = Depends(get_db)
):
    """Reindex all skills in Meilisearch"""
    skills = crud.get_skills(db, limit=1000)  # Index first 1000 skills for MVP
    bulk_index_skills(skills)
    
    return {
        "status": "accepted",
        "message": f"Reindexing initiated for {len(skills)} skills"
    }

@router.get("/suggest", response_model=List[str])
def get_search_suggestions(
    q: str = Query(..., description="Search query prefix", min_length=2),
    limit: int = Query(10, ge=1, le=20, description="Number of suggestions"),
    db: Session = Depends(get_db)
):
    """Get search autocomplete suggestions"""
    index = get_meilisearch_index()
    
    try:
        if index:
            # Use Meilisearch for suggestions
            results = index.search(q, {
                "limit": limit,
                "attributesToRetrieve": ["name"],
                "showRankingScore": False
            })
            
            suggestions = [hit["name"] for hit in results["hits"]]
            return suggestions
        else:
            # Fallback to database query
            skills = db.query(models.Skill.name)\
                .filter(models.Skill.name.ilike(f"{q}%"))\
                .limit(limit)\
                .all()
            
            return [skill[0] for skill in skills]
    
    except Exception as e:
        # Fallback to database query
        skills = db.query(models.Skill.name)\
            .filter(models.Skill.name.ilike(f"{q}%"))\
            .limit(limit)\
            .all()
        
        return [skill[0] for skill in skills]
