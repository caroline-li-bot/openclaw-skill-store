import re
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Finding:
    rule_id: str
    description: str
    severity: RiskLevel
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    snippet: Optional[str] = None

@dataclass
class SecurityScanResult:
    score: float  # 0-10
    risk_level: RiskLevel
    findings: List[Finding]
    summary: str

class SecurityScanner:
    """Static security scanner for OpenClaw skill code"""
    
    # Regex patterns for dangerous patterns
    RULES = [
        # Shell commands
        (
            "SHELL_EXEC",
            r"(exec|system|popen|subprocess|os\.system|os\.popen|subprocess\.Popen|subprocess\.call|subprocess\.run|sh\s+-c|bash\s+-c)",
            RiskLevel.HIGH,
            "Execution of shell commands detected"
        ),
        # Network requests
        (
            "NETWORK_REQUEST",
            r"(curl|wget|requests\.|http\.|urllib|aiohttp|httpx\.|socket\.|fetch|axios)",
            RiskLevel.MEDIUM,
            "Network request detected"
        ),
        # File system operations
        (
            "FILE_SYSTEM_ACCESS",
            r"(open\(|os\.open|os\.remove|os\.rmdir|os\.mkdir|shutil\.|pathlib\.|write|append)",
            RiskLevel.MEDIUM,
            "File system access detected"
        ),
        # Environment variable access
        (
            "ENV_VAR_ACCESS",
            r"(os\.environ|os\.getenv|process\.env|env\.)",
            RiskLevel.LOW,
            "Environment variable access detected"
        ),
        # Potential credential leaks
        (
            "CREDENTIAL_PATTERN",
            r"(api_key|token|secret|password|auth|credential|key\s*=|token\s*=|secret\s*=|password\s*=)",
            RiskLevel.CRITICAL,
            "Potential credential hardcoding detected"
        ),
        # Dangerous imports
        (
            "DANGEROUS_IMPORT",
            r"(import\s+os|import\s+subprocess|import\s+requests|import\s+socket|import\s+paramiko|import\s+ftplib)",
            RiskLevel.LOW,
            "Import of potentially dangerous module detected"
        ),
        # Eval usage
        (
            "EVAL_USAGE",
            r"(eval\(|exec\(|compile\(|ast\.literal_eval)",
            RiskLevel.CRITICAL,
            "Dynamic code execution via eval/exec detected"
        ),
        # Privilege escalation
        (
            "PRIVILEGE_ESCALATION",
            r"(sudo|su\s+-|chmod\s+777|chown\s+root|setuid|setgid)",
            RiskLevel.CRITICAL,
            "Potential privilege escalation attempt detected"
        ),
    ]

    def __init__(self):
        self.compiled_rules = [
            (rule_id, re.compile(pattern, re.IGNORECASE), severity, description)
            for rule_id, pattern, severity, description in self.RULES
        ]

    def scan_content(self, content: str, file_path: str = "unknown") -> List[Finding]:
        """Scan a single file content for security issues"""
        findings = []
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            for rule_id, pattern, severity, description in self.compiled_rules:
                if pattern.search(line):
                    findings.append(Finding(
                        rule_id=rule_id,
                        description=description,
                        severity=severity,
                        line_number=line_num,
                        file_path=file_path,
                        snippet=line.strip()[:100]  # First 100 chars as snippet
                    ))
        
        return findings

    def scan_repository(self, repo_path: str) -> List[Finding]:
        """Scan an entire repository directory"""
        findings = []
        
        # Supported file extensions to scan
        supported_extensions = ('.py', '.js', '.ts', '.sh', '.bash', '.zsh', '.md', '.json', '.yaml', '.yml')
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(supported_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            file_findings = self.scan_content(content, file_path)
                            findings.extend(file_findings)
                    except Exception as e:
                        # Skip files that can't be read
                        pass
        
        return findings

    def calculate_score(self, findings: List[Finding]) -> Tuple[float, RiskLevel, str]:
        """Calculate security score based on findings"""
        if not findings:
            return 10.0, RiskLevel.SAFE, "No security issues detected"
        
        # Weighting for different severity levels
        weights = {
            RiskLevel.CRITICAL: 2.5,
            RiskLevel.HIGH: 1.5,
            RiskLevel.MEDIUM: 0.8,
            RiskLevel.LOW: 0.2,
            RiskLevel.SAFE: 0.0
        }
        
        total_penalty = 0.0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        
        for finding in findings:
            total_penalty += weights[finding.severity]
            if finding.severity == RiskLevel.CRITICAL:
                critical_count += 1
            elif finding.severity == RiskLevel.HIGH:
                high_count += 1
            elif finding.severity == RiskLevel.MEDIUM:
                medium_count += 1
            elif finding.severity == RiskLevel.LOW:
                low_count += 1
        
        # Calculate score (max 10)
        score = max(0.0, 10.0 - total_penalty)
        score = round(score, 1)
        
        # Determine overall risk level
        if critical_count > 0:
            risk_level = RiskLevel.CRITICAL
        elif high_count > 0:
            risk_level = RiskLevel.HIGH
        elif medium_count > 3:
            risk_level = RiskLevel.MEDIUM
        elif low_count > 5:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.SAFE
        
        # Generate summary
        summary_parts = []
        if critical_count > 0:
            summary_parts.append(f"{critical_count} critical issue{'s' if critical_count != 1 else ''}")
        if high_count > 0:
            summary_parts.append(f"{high_count} high risk issue{'s' if high_count != 1 else ''}")
        if medium_count > 0:
            summary_parts.append(f"{medium_count} medium risk issue{'s' if medium_count != 1 else ''}")
        if low_count > 0:
            summary_parts.append(f"{low_count} low risk issue{'s' if low_count != 1 else ''}")
        
        if not summary_parts:
            summary = "No security issues detected"
        else:
            summary = "Found: " + ", ".join(summary_parts)
        
        return score, risk_level, summary

    def scan_skill(self, repo_path: str) -> SecurityScanResult:
        """Scan a skill repository and return complete results"""
        findings = self.scan_repository(repo_path)
        score, risk_level, summary = self.calculate_score(findings)
        
        return SecurityScanResult(
            score=score,
            risk_level=risk_level,
            findings=findings,
            summary=summary
        )
