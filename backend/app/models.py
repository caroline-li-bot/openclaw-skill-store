from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    """Skill categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    skill_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    skills = relationship("Skill", back_populates="category")

class Skill(Base):
    """Skill model"""
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    long_description = Column(Text)
    author = Column(String(255), index=True)
    repository = Column(String(500), unique=True, nullable=False)
    homepage = Column(String(500))
    install_command = Column(String(500))
    required_tools = Column(JSON)  # List of required tools
    version = Column(String(50))
    category_id = Column(Integer, ForeignKey("categories.id"))
    download_count = Column(Integer, default=0)
    star_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    security_score = Column(Float)
    security_risk_level = Column(String(20))  # safe, low, medium, high, critical
    is_verified = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_deprecated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_synced_at = Column(DateTime)
    
    category = relationship("Category", back_populates="skills")
    versions = relationship("SkillVersion", back_populates="skill")
    security_scans = relationship("SecurityScan", back_populates="skill")
    usage_examples = relationship("UsageExample", back_populates="skill")
    compatible_skills = relationship(
        "Skill",
        secondary="skill_compatibility",
        primaryjoin="Skill.id == skill_compatibility.c.skill_id",
        secondaryjoin="Skill.id == skill_compatibility.c.compatible_skill_id",
        backref="compatible_with"
    )

class SkillVersion(Base):
    """Skill version history"""
    __tablename__ = "skill_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    version = Column(String(50), nullable=False)
    changelog = Column(Text)
    release_notes = Column(Text)
    released_at = Column(DateTime, default=datetime.utcnow)
    download_url = Column(String(500))
    
    skill = relationship("Skill", back_populates="versions")

class SecurityScan(Base):
    """Security scan results"""
    __tablename__ = "security_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    scan_version = Column(String(50))
    score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    summary = Column(Text)
    findings = Column(JSON)  # List of findings
    scanned_at = Column(DateTime, default=datetime.utcnow)
    scanner_version = Column(String(50))
    
    skill = relationship("Skill", back_populates="security_scans")

class UsageExample(Base):
    """Skill usage examples"""
    __tablename__ = "usage_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    code_example = Column(Text)
    input_example = Column(JSON)
    output_example = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    skill = relationship("Skill", back_populates="usage_examples")

class SkillCompatibility(Base):
    """Skill compatibility junction table"""
    __tablename__ = "skill_compatibility"
    
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    compatible_skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)
    compatibility_note = Column(String(500))

class WorkflowTemplate(Base):
    """Workflow templates"""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    category = Column(String(100), index=True)
    author = Column(String(255))
    steps = Column(JSON)  # List of workflow steps
    required_skills = Column(JSON)  # List of required skill IDs
    usage_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnalyticsEvent(Base):
    """Analytics events"""
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), index=True, nullable=False)  # view, download, install, search
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=True)
    user_agent = Column(String(500))
    ip_address = Column(String(50))
    referrer = Column(String(500))
    search_query = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
