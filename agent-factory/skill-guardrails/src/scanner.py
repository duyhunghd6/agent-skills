"""
Skill Scanner - Main Orchestrator

Coordinates all security levels and aggregates results.
"""

import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import yaml

from .models.skill import Skill, SkillResult
from .models.report import ScanReport
from .levels.l1_static import StaticAnalyzer
from .levels.l2_semantic import SemanticAnalyzer
from .levels.l3_dynamic import DynamicAnalyzer
from .levels.l4_trust import TrustVerifier


class SkillScanner:
    """
    Main scanner orchestrator for multi-level security analysis.
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._load_config()
        
        # Initialize analyzers
        self.l1_analyzer = StaticAnalyzer(self.patterns_config)
        self.l2_analyzer = SemanticAnalyzer()
        self.l3_analyzer = DynamicAnalyzer()
        self.l4_verifier = TrustVerifier()
        
    def _load_config(self):
        """Load configuration files."""
        config_dir = Path(__file__).parent.parent / "config"
        
        with open(config_dir / "patterns.yaml") as f:
            self.patterns_config = yaml.safe_load(f)
            
        with open(config_dir / "thresholds.yaml") as f:
            self.thresholds_config = yaml.safe_load(f)
    
    def scan_skill(
        self,
        skill_path: Path,
        level: str = "all"
    ) -> SkillResult:
        """
        Scan a single skill through specified security levels.
        
        Args:
            skill_path: Path to skill directory
            level: Security level to run (L1, L2, L3, L4, or all)
            
        Returns:
            SkillResult with findings and risk score
        """
        # Parse skill
        skill = Skill.from_path(skill_path)
        
        if not skill.is_valid:
            return SkillResult(
                name=skill_path.name,
                path=str(skill_path),
                is_valid=False,
                error="Invalid skill: Missing or malformed SKILL.md"
            )
        
        findings = []
        
        # Level 1: Static Analysis (always run)
        if level in ["all", "L1", "l1"]:
            l1_findings = self.l1_analyzer.analyze(skill)
            findings.extend(l1_findings)
        
        # Level 2: Semantic Analysis (AI)
        if level in ["all", "L2", "l2"]:
            # Only run L2 if L1 found medium+ severity issues or skill is offensive
            should_run_l2 = (
                skill.metadata.get("risk") == "offensive" or
                any(f.severity >= 0.3 for f in findings)
            )
            if should_run_l2:
                l2_findings = self.l2_analyzer.analyze(skill)
                findings.extend(l2_findings)
        
        # Level 3: Dynamic Analysis (sandbox)
        if level in ["all", "L3", "l3"]:
            # Only run L3 for high-risk skills
            max_severity = max([f.severity for f in findings], default=0)
            if max_severity >= 0.6:
                l3_findings = self.l3_analyzer.analyze(skill)
                findings.extend(l3_findings)
        
        # Level 4: Trust Verification
        if level in ["all", "L4", "l4"]:
            l4_findings = self.l4_verifier.verify(skill)
            findings.extend(l4_findings)
        
        # Calculate composite risk score
        risk_score = self._calculate_risk_score(skill, findings)
        
        # Determine classification
        classification = self._classify_risk(risk_score)
        
        return SkillResult(
            name=skill.name,
            path=str(skill_path),
            is_valid=True,
            risk_score=risk_score,
            classification=classification,
            findings=findings,
            top_finding=findings[0].description if findings else None,
            metadata=skill.metadata
        )
    
    def _calculate_risk_score(self, skill: Skill, findings: list) -> float:
        """
        Calculate composite risk score based on weights.
        
        Score = 0.40 × Pattern Severity +
                0.30 × Permission Scope +
                0.20 × Source Trust +
                0.10 × Community Reports
        """
        weights = self.thresholds_config["weights"]
        
        # Pattern severity (max finding severity)
        pattern_score = max([f.severity for f in findings], default=0.0)
        
        # Permission scope (from declared permissions)
        permission_score = self._get_permission_score(skill)
        
        # Source trust (from metadata)
        source_score = self._get_source_trust_score(skill)
        
        # Community reports (placeholder - would connect to DB)
        community_score = 0.0
        
        # Weighted sum
        risk_score = (
            weights["pattern_severity"] * pattern_score +
            weights["permission_scope"] * permission_score +
            weights["source_trust"] * source_score +
            weights["community_reports"] * community_score
        )
        
        return min(1.0, risk_score)
    
    def _get_permission_score(self, skill: Skill) -> float:
        """Calculate permission scope score."""
        permissions = skill.metadata.get("permissions", [])
        if not permissions:
            # Infer from risk level
            risk = skill.metadata.get("risk", "unknown")
            risk_scores = {
                "none": 0.0,
                "safe": 0.2,
                "critical": 0.6,
                "offensive": 0.9,
                "unknown": 0.5
            }
            return risk_scores.get(risk, 0.5)
        
        # Calculate from declared permissions
        permission_scores = self.thresholds_config["permissions"]
        max_score = 0.0
        for perm in permissions:
            if perm in permission_scores:
                max_score = max(max_score, permission_scores[perm]["score"])
        
        return max_score
    
    def _get_source_trust_score(self, skill: Skill) -> float:
        """Calculate source trust score."""
        source = skill.metadata.get("source", "unknown")
        trust_level = skill.metadata.get("trust_level", "community")
        
        trust_scores = self.thresholds_config["source_trust"]
        
        if trust_level in trust_scores:
            return trust_scores[trust_level]["score"]
        
        # Unknown source
        return 0.5
    
    def _classify_risk(self, score: float) -> str:
        """Classify risk level based on score."""
        thresholds = self.thresholds_config["thresholds"]
        
        if score >= thresholds["critical"]["min"]:
            return "critical"
        elif score >= thresholds["high"]["min"]:
            return "high"
        elif score >= thresholds["medium"]["min"]:
            return "medium"
        else:
            return "low"
    
    def full_scan(self, skills_dir: Path) -> ScanReport:
        """
        Run full security scan on all skills in directory.
        """
        results = []
        
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir() and not skill_path.name.startswith('.'):
                result = self.scan_skill(skill_path, level="all")
                results.append(result)
        
        return ScanReport.from_results(results)
