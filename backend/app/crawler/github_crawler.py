import os
import re
import yaml
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from github import Github, Auth
from github.Repository import Repository
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from ..database import settings, get_db
from .. import crud, models, schemas
from ..scanner.security_scanner import SecurityScanner

class GitHubCrawler:
    """Crawler to fetch OpenClaw skills from GitHub repositories"""
    
    def __init__(self):
        self.github_token = settings.GITHUB_TOKEN
        if self.github_token:
            auth = Auth.Token(self.github_token)
            self.github = Github(auth=auth)
        else:
            self.github = Github()
        
        self.scanner = SecurityScanner()
        
        # Search queries for OpenClaw skills
        self.search_queries = [
            "topic:openclaw-skill",
            "topic:openclaw",
            "openclaw skill in:readme",
            "openclaw plugin in:readme",
            "openclaw extension in:readme",
        ]
        
        # Common skill repository file patterns
        self.skill_indicators = [
            "SKILL.md",
            "skill.yaml",
            "skill.yml",
            "skill.json",
            "manifest.yaml",
            "manifest.yml",
        ]

    def is_openclaw_skill_repo(self, repo: Repository) -> bool:
        """Check if a repository is an OpenClaw skill"""
        try:
            # Check topics
            topics = repo.get_topics()
            if "openclaw-skill" in topics or "openclaw-plugin" in topics:
                return True
            
            # Check for skill indicator files
            for indicator in self.skill_indicators:
                try:
                    repo.get_contents(indicator)
                    return True
                except Exception:
                    continue
            
            # Check README for OpenClaw mentions
            try:
                readme = repo.get_readme()
                if readme:
                    readme_content = readme.decoded_content.decode("utf-8").lower()
                    if "openclaw" in readme_content and ("skill" in readme_content or "plugin" in readme_content or "extension" in readme_content):
                        return True
            except Exception:
                pass
            
            return False
        except Exception:
            return False

    def extract_skill_metadata(self, repo: Repository) -> Dict[str, Any]:
        """Extract skill metadata from repository"""
        metadata = {
            "name": repo.name,
            "description": repo.description or "",
            "author": repo.owner.login,
            "repository": repo.clone_url,
            "homepage": repo.homepage or "",
            "version": self._extract_version(repo),
            "required_tools": [],
            "install_command": f"openclaw install {repo.owner.login}/{repo.name}",
        }
        
        # Try to get metadata from skill manifest files
        for indicator in self.skill_indicators:
            try:
                content = repo.get_contents(indicator)
                if content:
                    file_content = content.decoded_content.decode("utf-8")
                    if indicator.endswith((".yaml", ".yml")):
                        yaml_data = yaml.safe_load(file_content)
                        if yaml_data and isinstance(yaml_data, dict):
                            metadata.update(self._parse_skill_yaml(yaml_data))
                    elif indicator.endswith(".json"):
                        json_data = json.loads(file_content)
                        if json_data and isinstance(json_data, dict):
                            metadata.update(self._parse_skill_json(json_data))
                    elif indicator == "SKILL.md":
                        metadata.update(self._parse_skill_md(file_content))
                    break
            except Exception:
                continue
        
        # Generate slug from name
        metadata["slug"] = self._slugify(metadata["name"])
        
        return metadata

    def _parse_skill_yaml(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse skill metadata from YAML format"""
        parsed = {}
        if "name" in yaml_data:
            parsed["name"] = yaml_data["name"]
        if "description" in yaml_data:
            parsed["description"] = yaml_data["description"]
        if "version" in yaml_data:
            parsed["version"] = yaml_data["version"]
        if "author" in yaml_data:
            parsed["author"] = yaml_data["author"]
        if "install_command" in yaml_data:
            parsed["install_command"] = yaml_data["install_command"]
        if "required_tools" in yaml_data and isinstance(yaml_data["required_tools"], list):
            parsed["required_tools"] = yaml_data["required_tools"]
        if "homepage" in yaml_data:
            parsed["homepage"] = yaml_data["homepage"]
        return parsed

    def _parse_skill_json(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse skill metadata from JSON format"""
        return self._parse_skill_yaml(json_data)  # Same structure as YAML

    def _parse_skill_md(self, content: str) -> Dict[str, Any]:
        """Parse basic metadata from SKILL.md"""
        parsed = {}
        
        # Try to extract title
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            parsed["name"] = title_match.group(1).strip()
        
        # Try to extract description (first paragraph after title)
        desc_match = re.search(r"^#\s+.+$\n\n(.+?)(?=\n#|\Z)", content, re.MULTILINE | re.DOTALL)
        if desc_match:
            parsed["description"] = desc_match.group(1).strip()
        
        # Try to extract version
        version_match = re.search(r"version:\s*([\d.]+)", content, re.IGNORECASE)
        if version_match:
            parsed["version"] = version_match.group(1).strip()
        
        # Try to extract author
        author_match = re.search(r"author:\s*(.+)", content, re.IGNORECASE)
        if author_match:
            parsed["author"] = author_match.group(1).strip()
        
        return parsed

    def _extract_version(self, repo: Repository) -> str:
        """Extract version from repository tags or releases"""
        try:
            releases = repo.get_releases()
            if releases.totalCount > 0:
                latest_release = releases[0]
                return latest_release.tag_name.lstrip("v")
            
            tags = repo.get_tags()
            if tags.totalCount > 0:
                latest_tag = tags[0]
                return latest_tag.name.lstrip("v")
        except Exception:
            pass
        
        return "0.1.0"

    def _slugify(self, name: str) -> str:
        """Convert name to URL-friendly slug"""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug

    def crawl_repository(self, repo_url: str, db: Session) -> Optional[models.Skill]:
        """Crawl a specific repository and add it to the database"""
        try:
            repo = self.github.get_repo(repo_url.replace("https://github.com/", "").replace(".git", ""))
            
            if not self.is_openclaw_skill_repo(repo):
                return None
            
            # Extract metadata
            metadata = self.extract_skill_metadata(repo)
            
            # Check if skill already exists
            existing_skill = crud.get_skill_by_repository(db, repository=metadata["repository"])
            if existing_skill:
                # Update existing skill
                skill_update = schemas.SkillUpdate(**metadata)
                skill = crud.update_skill(db, skill_id=existing_skill.id, skill_update=skill_update)
            else:
                # Create new skill
                skill_create = schemas.SkillCreate(**metadata)
                skill = crud.create_skill(db, skill=skill_create)
            
            # Update star count
            skill.star_count = repo.stargazers_count
            skill.last_synced_at = datetime.utcnow()
            db.commit()
            db.refresh(skill)
            
            return skill
            
        except Exception as e:
            print(f"Error crawling repository {repo_url}: {str(e)}")
            return None

    def search_and_crawl(self, db: Session, max_results: int = 100) -> List[models.Skill]:
        """Search GitHub for OpenClaw skills and crawl them"""
        skills = []
        
        for query in self.search_queries:
            try:
                print(f"Searching GitHub with query: {query}")
                repositories = self.github.search_repositories(query, sort="stars", order="desc")
                
                for repo in repositories[:max_results]:
                    if self.is_openclaw_skill_repo(repo):
                        print(f"Found skill repository: {repo.full_name}")
                        skill = self.crawl_repository(repo.clone_url, db)
                        if skill:
                            skills.append(skill)
                            
            except Exception as e:
                print(f"Error with search query '{query}': {str(e)}")
                continue
        
        return skills

    def get_awesome_openclaw_skills(self, db: Session) -> List[models.Skill]:
        """Fetch skills from awesome-openclaw-skills list"""
        skills = []
        try:
            # Get the awesome list repo
            repo = self.github.get_repo("openclaw/awesome-openclaw-skills")
            readme = repo.get_readme()
            
            if readme:
                content = readme.decoded_content.decode("utf-8")
                # Extract repository URLs from markdown links
                repo_urls = re.findall(r"https?://github\.com/[^\s/]+/[^\s/)]+", content)
                
                for url in set(repo_urls):
                    try:
                        skill = self.crawl_repository(url, db)
                        if skill:
                            skills.append(skill)
                    except Exception as e:
                        print(f"Error crawling {url}: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error fetching awesome list: {str(e)}")
        
        return skills

# Global crawler instance
crawler = GitHubCrawler()

def run_full_crawl(db: Session) -> Dict[str, Any]:
    """Run a full crawl of all skill sources"""
    print("Starting full GitHub crawl...")
    
    # Crawl from search results
    search_skills = crawler.search_and_crawl(db, max_results=50)
    print(f"Found {len(search_skills)} skills from GitHub search")
    
    # Crawl from awesome list
    awesome_skills = crawler.get_awesome_openclaw_skills(db)
    print(f"Found {len(awesome_skills)} skills from awesome list")
    
    total_skills = len(set(search_skills + awesome_skills))
    
    return {
        "status": "success",
        "total_found": total_skills,
        "from_search": len(search_skills),
        "from_awesome_list": len(awesome_skills)
    }

def schedule_crawl(background_tasks: BackgroundTasks) -> None:
    """Schedule a crawl in the background"""
    db = next(get_db())
    background_tasks.add_task(run_full_crawl, db)
