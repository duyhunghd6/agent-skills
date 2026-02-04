"""
Skill Data Model

Represents an agent skill for security analysis.
"""

import re
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from pydantic import BaseModel


@dataclass
class Finding:
    """A single security finding."""
    level: str  # L1, L2, L3, L4
    name: str
    description: str
    severity: float  # 0.0 - 1.0
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    mitigation: Optional[str] = None


@dataclass
class SkillResult:
    """Result of scanning a skill."""
    name: str
    path: str
    is_valid: bool
    risk_score: float = 0.0
    classification: str = "low"  # low, medium, high, critical
    findings: List[Finding] = field(default_factory=list)
    top_finding: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Skill:
    """
    Represents an agent skill with its content and metadata.
    """
    
    def __init__(
        self,
        path: Path,
        name: str,
        content: str,
        metadata: Dict[str, Any],
        is_valid: bool = True
    ):
        self.path = path
        self.name = name
        self.content = content
        self.metadata = metadata
        self.is_valid = is_valid
        
        # Parsed content sections
        self.frontmatter = metadata
        self.body = self._extract_body(content)
        self.code_blocks = self._extract_code_blocks(content)
    
    @classmethod
    def from_path(cls, skill_path: Path) -> "Skill":
        """
        Load a skill from its directory path.
        
        Args:
            skill_path: Path to skill directory
            
        Returns:
            Skill instance
        """
        skill_md = skill_path / "SKILL.md"
        
        if not skill_md.exists():
            return cls(
                path=skill_path,
                name=skill_path.name,
                content="",
                metadata={},
                is_valid=False
            )
        
        try:
            content = skill_md.read_text(encoding="utf-8")
        except Exception as e:
            return cls(
                path=skill_path,
                name=skill_path.name,
                content="",
                metadata={"error": str(e)},
                is_valid=False
            )
        
        # Parse frontmatter
        metadata = cls._parse_frontmatter(content)
        
        if metadata is None:
            return cls(
                path=skill_path,
                name=skill_path.name,
                content=content,
                metadata={},
                is_valid=False
            )
        
        return cls(
            path=skill_path,
            name=metadata.get("name", skill_path.name),
            content=content,
            metadata=metadata,
            is_valid=True
        )
    
    @staticmethod
    def _parse_frontmatter(content: str) -> Optional[Dict[str, Any]]:
        """
        Parse YAML frontmatter from SKILL.md content.
        """
        fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            return None
        
        fm_text = fm_match.group(1)
        metadata = {}
        
        for line in fm_text.split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                val = val.strip().strip('"').strip("'")
                metadata[key.strip()] = val
        
        return metadata
    
    @staticmethod
    def _extract_body(content: str) -> str:
        """Extract body content after frontmatter."""
        fm_match = re.search(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        if fm_match:
            return content[fm_match.end():]
        return content
    
    @staticmethod
    def _extract_code_blocks(content: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown content."""
        code_blocks = []
        pattern = r'```(\w*)\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            code_blocks.append({
                "language": match.group(1) or "unknown",
                "code": match.group(2)
            })
        
        return code_blocks
    
    def has_section(self, section_name: str) -> bool:
        """Check if skill has a specific section."""
        pattern = rf'^##\s+{re.escape(section_name)}'
        return bool(re.search(pattern, self.content, re.MULTILINE | re.IGNORECASE))
    
    def get_section_content(self, section_name: str) -> Optional[str]:
        """Get content of a specific section."""
        pattern = rf'^##\s+{re.escape(section_name)}\s*\n(.*?)(?=^##|\Z)'
        match = re.search(pattern, self.content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    @property
    def risk_level(self) -> str:
        """Get declared risk level."""
        return self.metadata.get("risk", "unknown")
    
    @property
    def is_offensive(self) -> bool:
        """Check if skill is marked as offensive."""
        return self.risk_level == "offensive"
    
    @property
    def has_disclaimer(self) -> bool:
        """Check if skill has required security disclaimer."""
        return "AUTHORIZED USE ONLY" in self.content.upper()
    
    @property
    def source(self) -> str:
        """Get source attribution."""
        return self.metadata.get("source", "unknown")
    
    @property
    def permissions(self) -> List[str]:
        """Get declared permissions."""
        perms = self.metadata.get("permissions", "")
        if isinstance(perms, str):
            return [p.strip() for p in perms.split(",") if p.strip()]
        return perms if isinstance(perms, list) else []
