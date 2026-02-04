"""
Scan Report Data Model

Represents the output of a security scan.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from uuid import uuid4

from .skill import SkillResult


@dataclass
class ScanReport:
    """
    Comprehensive security scan report.
    """
    scan_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    total_skills: int = 0
    passed_count: int = 0
    flagged_count: int = 0
    blocked_count: int = 0
    
    results: List[SkillResult] = field(default_factory=list)
    high_risk_skills: List[SkillResult] = field(default_factory=list)
    
    summary: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_results(cls, results: List[SkillResult]) -> "ScanReport":
        """
        Create a report from scan results.
        """
        total = len(results)
        passed = sum(1 for r in results if r.classification == "low")
        flagged = sum(1 for r in results if r.classification in ["medium", "high"])
        blocked = sum(1 for r in results if r.classification == "critical")
        
        high_risk = sorted(
            [r for r in results if r.risk_score >= 0.6],
            key=lambda x: x.risk_score,
            reverse=True
        )
        
        return cls(
            total_skills=total,
            passed_count=passed,
            flagged_count=flagged,
            blocked_count=blocked,
            results=results,
            high_risk_skills=high_risk,
            summary={
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
                "high_risk_count": len(high_risk),
                "most_common_issues": cls._get_common_issues(results)
            }
        )
    
    @staticmethod
    def _get_common_issues(results: List[SkillResult]) -> List[Dict[str, Any]]:
        """Get most common security issues found."""
        issue_counts: Dict[str, int] = {}
        
        for result in results:
            for finding in result.findings:
                issue_counts[finding.name] = issue_counts.get(finding.name, 0) + 1
        
        sorted_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"name": name, "count": count}
            for name, count in sorted_issues[:10]
        ]
    
    def to_json(self) -> str:
        """Convert report to JSON string."""
        data = {
            "scan_id": self.scan_id,
            "timestamp": self.timestamp,
            "summary": {
                "total_skills": self.total_skills,
                "passed": self.passed_count,
                "flagged": self.flagged_count,
                "blocked": self.blocked_count,
                **self.summary
            },
            "high_risk_skills": [
                {
                    "name": s.name,
                    "path": s.path,
                    "risk_score": s.risk_score,
                    "classification": s.classification,
                    "top_finding": s.top_finding,
                    "findings_count": len(s.findings)
                }
                for s in self.high_risk_skills
            ],
            "all_results": [
                {
                    "name": r.name,
                    "risk_score": r.risk_score,
                    "classification": r.classification,
                    "findings_count": len(r.findings)
                }
                for r in self.results
            ]
        }
        return json.dumps(data, indent=2)
    
    def to_markdown(self) -> str:
        """Convert report to Markdown format."""
        lines = [
            f"# 🛡️ Security Scan Report",
            f"",
            f"**Scan ID:** `{self.scan_id}`",
            f"**Timestamp:** {self.timestamp}",
            f"",
            f"## Summary",
            f"",
            f"| Metric | Count | Percentage |",
            f"|--------|-------|------------|",
            f"| Total Scanned | {self.total_skills} | 100% |",
            f"| ✅ Passed | {self.passed_count} | {self.passed_count/self.total_skills*100:.1f}% |" if self.total_skills > 0 else "",
            f"| ⚠️ Flagged | {self.flagged_count} | {self.flagged_count/self.total_skills*100:.1f}% |" if self.total_skills > 0 else "",
            f"| 🚨 Blocked | {self.blocked_count} | {self.blocked_count/self.total_skills*100:.1f}% |" if self.total_skills > 0 else "",
            f"",
        ]
        
        if self.high_risk_skills:
            lines.extend([
                f"## High-Risk Skills",
                f"",
                f"| # | Skill | Score | Finding |",
                f"|---|-------|-------|---------|",
            ])
            
            for i, skill in enumerate(self.high_risk_skills[:20], 1):
                badge = "🔴" if skill.risk_score >= 0.8 else "🟠"
                lines.append(
                    f"| {i} | {badge} {skill.name} | {skill.risk_score:.2f} | {skill.top_finding or 'N/A'} |"
                )
        
        if self.summary.get("most_common_issues"):
            lines.extend([
                f"",
                f"## Most Common Issues",
                f"",
            ])
            for issue in self.summary["most_common_issues"][:5]:
                lines.append(f"- **{issue['name']}**: {issue['count']} occurrences")
        
        return "\n".join(lines)
