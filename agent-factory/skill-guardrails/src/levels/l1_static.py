"""
Level 1: Static Analysis

Pattern-based detection of dangerous code patterns, prompt injections,
and metadata validation.
"""

import re
from typing import List, Dict, Any
from pathlib import Path

from ..models.skill import Skill, Finding


class StaticAnalyzer:
    """
    Level 1 Security Analysis - Static Pattern Detection
    
    Scans skill content for:
    - Dangerous code execution patterns
    - Prompt injection attempts
    - Obfuscated content
    - Missing security disclaimers
    - Metadata integrity issues
    """
    
    def __init__(self, patterns_config: Dict[str, Any]):
        self.config = patterns_config
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for performance."""
        self.patterns = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for severity, patterns in self.config.get("patterns", {}).items():
            if severity in self.patterns:
                for p in patterns:
                    try:
                        compiled = re.compile(p["pattern"], re.IGNORECASE | re.MULTILINE)
                        self.patterns[severity].append({
                            "name": p["name"],
                            "regex": compiled,
                            "severity": p["severity"],
                            "description": p.get("description", ""),
                            "mitigation": p.get("mitigation", "")
                        })
                    except re.error as e:
                        print(f"Warning: Invalid pattern '{p['name']}': {e}")
    
    def analyze(self, skill: Skill) -> List[Finding]:
        """
        Run static analysis on a skill.
        
        Args:
            skill: Skill instance to analyze
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        # 1. Metadata validation
        findings.extend(self._check_metadata(skill))
        
        # 2. Pattern detection on full content
        findings.extend(self._detect_patterns(skill))
        
        # 3. Code block analysis
        findings.extend(self._analyze_code_blocks(skill))
        
        # 4. Security disclaimer check for offensive skills
        if skill.is_offensive and not skill.has_disclaimer:
            findings.append(Finding(
                level="L1",
                name="missing_disclaimer",
                description="Offensive skill missing 'AUTHORIZED USE ONLY' disclaimer",
                severity=0.90,
                mitigation="Add required security disclaimer at the top of SKILL.md"
            ))
        
        # Sort by severity (highest first)
        findings.sort(key=lambda f: f.severity, reverse=True)
        
        return findings
    
    def _check_metadata(self, skill: Skill) -> List[Finding]:
        """Validate skill metadata/frontmatter."""
        findings = []
        
        # Required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in skill.metadata:
                findings.append(Finding(
                    level="L1",
                    name=f"missing_{field}",
                    description=f"Missing required metadata field: {field}",
                    severity=0.30,
                    mitigation=f"Add '{field}' to frontmatter"
                ))
        
        # Name matches folder
        if skill.metadata.get("name") != skill.path.name:
            findings.append(Finding(
                level="L1",
                name="name_mismatch",
                description=f"Name '{skill.metadata.get('name')}' doesn't match folder '{skill.path.name}'",
                severity=0.20,
                mitigation="Ensure 'name' in frontmatter matches folder name"
            ))
        
        # Risk label present
        if "risk" not in skill.metadata:
            findings.append(Finding(
                level="L1",
                name="missing_risk",
                description="Missing 'risk' classification label",
                severity=0.35,
                mitigation="Add 'risk' field with value: none, safe, critical, or offensive"
            ))
        elif skill.metadata["risk"] not in ["none", "safe", "critical", "offensive"]:
            findings.append(Finding(
                level="L1",
                name="invalid_risk",
                description=f"Invalid risk level: {skill.metadata['risk']}",
                severity=0.40,
                mitigation="Use valid risk level: none, safe, critical, or offensive"
            ))
        
        # Source attribution
        if "source" not in skill.metadata:
            findings.append(Finding(
                level="L1",
                name="missing_source",
                description="Missing source attribution",
                severity=0.15,
                mitigation="Add 'source' field with URL or 'self' if original"
            ))
        
        return findings
    
    def _detect_patterns(self, skill: Skill) -> List[Finding]:
        """Detect dangerous patterns in skill content."""
        findings = []
        content = skill.content
        
        for severity_level in ["critical", "high", "medium", "low"]:
            for pattern in self.patterns.get(severity_level, []):
                matches = pattern["regex"].finditer(content)
                
                for match in matches:
                    # Get line number
                    line_number = content[:match.start()].count('\n') + 1
                    
                    # Get code snippet (surrounding context)
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    snippet = content[start:end].strip()
                    
                    # Check allowlist
                    if self._is_allowed(pattern["name"], skill):
                        continue
                    
                    findings.append(Finding(
                        level="L1",
                        name=pattern["name"],
                        description=pattern["description"],
                        severity=pattern["severity"],
                        line_number=line_number,
                        code_snippet=snippet[:200],  # Limit snippet length
                        mitigation=pattern["mitigation"]
                    ))
        
        return findings
    
    def _analyze_code_blocks(self, skill: Skill) -> List[Finding]:
        """Analyze code blocks for dangerous patterns."""
        findings = []
        
        # Additional checks on code blocks
        for i, block in enumerate(skill.code_blocks):
            code = block["code"]
            lang = block["language"]
            
            # Shell script checks
            if lang in ["bash", "sh", "shell", "zsh"]:
                # Dangerous shell patterns
                if re.search(r'rm\s+-rf\s+/', code):
                    findings.append(Finding(
                        level="L1",
                        name="destructive_shell",
                        description="Potentially destructive shell command (rm -rf /)",
                        severity=0.95,
                        code_snippet=code[:100],
                        mitigation="Remove or add safety guards"
                    ))
            
            # Python checks
            if lang in ["python", "py"]:
                if re.search(r'__import__\s*\(', code):
                    findings.append(Finding(
                        level="L1",
                        name="dynamic_import",
                        description="Dynamic import pattern detected",
                        severity=0.50,
                        code_snippet=code[:100],
                        mitigation="Use explicit imports when possible"
                    ))
        
        return findings
    
    def _is_allowed(self, pattern_name: str, skill: Skill) -> bool:
        """Check if pattern is in allowlist for skill context."""
        allowlist = self.config.get("allowlist", [])
        
        for entry in allowlist:
            if pattern_name in entry.get("patterns", []):
                # Check if context matches
                if entry.get("context") == "offensive" and skill.is_offensive:
                    if skill.has_disclaimer or not entry.get("requires_disclaimer", False):
                        return True
                elif entry.get("context") == "defensive" and skill.risk_level in ["safe", "critical"]:
                    return True
        
        return False
