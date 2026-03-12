from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
import tempfile
import os
import git

from .. import crud, models, schemas
from ..database import get_db
from ..scanner.security_scanner import SecurityScanner, SecurityScanResult

router = APIRouter()

scanner = SecurityScanner()

@router.post("/scan/{skill_id}", response_model=schemas.SecurityScan, status_code=status.HTTP_202_ACCEPTED)
async def scan_skill(
    skill_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Initiate a security scan for a skill"""
    skill = crud.get_skill(db, skill_id=skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Add scan task to background
    background_tasks.add_task(perform_security_scan, db, skill_id, str(skill.repository))
    
    return {
        "status": "accepted",
        "message": "Security scan initiated",
        "skill_id": skill_id,
        "skill_name": skill.name
    }

@router.get("/scan-results/{skill_id}", response_model=List[schemas.SecurityScan])
async def get_scan_results(
    skill_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get security scan results for a skill"""
    skill = crud.get_skill(db, skill_id=skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    scans = crud.get_security_scans_for_skill(db, skill_id=skill_id, limit=limit)
    return scans

@router.get("/latest-scan/{skill_id}", response_model=schemas.SecurityScan)
async def get_latest_scan(
    skill_id: int,
    db: Session = Depends(get_db)
):
    """Get the latest security scan for a skill"""
    scan = crud.get_latest_security_scan(db, skill_id=skill_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No security scans found for this skill"
        )
    return scan

def perform_security_scan(db: Session, skill_id: int, repository_url: str) -> None:
    """Perform security scan on a skill repository"""
    temp_dir = None
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="openclaw-skill-scan-")
        
        # Clone the repository
        repo = git.Repo.clone_from(repository_url, temp_dir, depth=1)
        
        # Scan the repository
        scan_result = scanner.scan_skill(temp_dir)
        
        # Convert findings to schema format
        findings = [
            schemas.FindingBase(
                rule_id=f.rule_id,
                description=f.description,
                severity=f.severity.value,
                line_number=f.line_number,
                file_path=f.file_path,
                snippet=f.snippet
            )
            for f in scan_result.findings
        ]
        
        # Create scan record
        scan_create = schemas.SecurityScanCreate(
            scan_version=repo.head.commit.hexsha[:7],
            score=scan_result.score,
            risk_level=scan_result.risk_level.value,
            summary=scan_result.summary,
            findings=findings,
            scanner_version="1.0.0"
        )
        
        # Save to database
        crud.create_security_scan(db, skill_id=skill_id, scan=scan_create)
        
    except Exception as e:
        # Log the error
        print(f"Error scanning skill {skill_id}: {str(e)}")
        # Create failed scan record
        scan_create = schemas.SecurityScanCreate(
            scan_version="unknown",
            score=0.0,
            risk_level="critical",
            summary=f"Scan failed: {str(e)}",
            findings=[],
            scanner_version="1.0.0"
        )
        crud.create_security_scan(db, skill_id=skill_id, scan=scan_create)
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

@router.post("/scan-content", response_model=schemas.SecurityScan)
async def scan_content(
    content: str,
    file_path: str = "unknown"
):
    """Scan a single file content for security issues (for demo purposes)"""
    findings = scanner.scan_content(content, file_path)
    score, risk_level, summary = scanner.calculate_score(findings)
    
    # Convert findings to schema format
    finding_schemas = [
        schemas.FindingBase(
            rule_id=f.rule_id,
            description=f.description,
            severity=f.severity.value,
            line_number=f.line_number,
            file_path=f.file_path,
            snippet=f.snippet
        )
        for f in findings
    ]
    
    return {
        "score": score,
        "risk_level": risk_level.value,
        "summary": summary,
        "findings": finding_schemas,
        "scan_version": "adhoc",
        "scanner_version": "1.0.0",
        "scanned_at": "now"
    }
