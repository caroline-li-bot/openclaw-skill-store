from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevelEnum(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    skill_count: int = 0

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Usage Example schemas
class UsageExampleBase(BaseModel):
    title: str
    description: Optional[str] = None
    code_example: Optional[str] = None
    input_example: Optional[Dict[str, Any]] = None
    output_example: Optional[Dict[str, Any]] = None

class UsageExampleCreate(UsageExampleBase):
    pass

class UsageExample(UsageExampleBase):
    id: int
    skill_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Skill schemas
class SkillBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    long_description: Optional[str] = None
    author: Optional[str] = None
    repository: HttpUrl
    homepage: Optional[HttpUrl] = None
    install_command: Optional[str] = None
    required_tools: Optional[List[str]] = None
    version: Optional[str] = None
    category_id: Optional[int] = None
    download_count: int = 0
    star_count: int = 0
    view_count: int = 0
    security_score: Optional[float] = None
    security_risk_level: Optional[RiskLevelEnum] = None
    is_verified: bool = False
    is_featured: bool = False
    is_deprecated: bool = False

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = None
    slug: Optional[str] = None
    repository: Optional[HttpUrl] = None

class Skill(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_synced_at: Optional[datetime] = None
    category: Optional[Category] = None
    usage_examples: List[UsageExample] = []
    
    class Config:
        from_attributes = True

class SkillList(BaseModel):
    items: List[Skill]
    total: int
    page: int
    size: int
    pages: int

# Security Scan schemas
class FindingBase(BaseModel):
    rule_id: str
    description: str
    severity: RiskLevelEnum
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    snippet: Optional[str] = None

class SecurityScanBase(BaseModel):
    scan_version: str
    score: float
    risk_level: RiskLevelEnum
    summary: str
    findings: List[FindingBase]
    scanner_version: str

class SecurityScanCreate(SecurityScanBase):
    pass

class SecurityScan(SecurityScanBase):
    id: int
    skill_id: int
    scanned_at: datetime
    
    class Config:
        from_attributes = True

# Workflow Template schemas
class WorkflowTemplateBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    steps: List[Dict[str, Any]]
    required_skills: List[int]
    usage_count: int = 0
    is_featured: bool = False

class WorkflowTemplateCreate(WorkflowTemplateBase):
    pass

class WorkflowTemplate(WorkflowTemplateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Search schemas
class SearchResult(BaseModel):
    type: str  # skill or workflow
    item: Dict[str, Any]
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    took_ms: int

# Stats schemas
class MarketplaceStats(BaseModel):
    total_skills: int
    total_categories: int
    total_workflows: int
    total_downloads: int
    total_views: int
    trending_skills: List[Skill]
    popular_categories: List[Category]
