"""
Level 4: Trust Verification

Verifies skill provenance and trust chain:
- Cryptographic signature verification
- Author reputation assessment
- Audit trail logging
"""

import os
import hashlib
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

from ..models.skill import Skill, Finding


@dataclass
class TrustConfig:
    """Configuration for trust verification."""
    require_signature: bool = False
    trusted_authors_file: Optional[str] = None
    audit_log_file: str = "audit.log"


class TrustVerifier:
    """
    Level 4 Security Analysis - Trust Verification
    
    Verifies:
    - Cryptographic signatures (if available)
    - Author reputation
    - Source attribution
    - Audit trail
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.trusted_authors = self._load_trusted_authors()
    
    def _load_config(self) -> TrustConfig:
        """Load trust verification configuration."""
        return TrustConfig(
            require_signature=os.getenv("REQUIRE_SIGNATURE", "false").lower() == "true",
            trusted_authors_file=os.getenv("TRUSTED_AUTHORS_FILE"),
            audit_log_file=os.getenv("AUDIT_LOG_FILE", "audit.log")
        )
    
    def _load_trusted_authors(self) -> Dict[str, Dict[str, Any]]:
        """Load trusted authors registry."""
        if not self.config.trusted_authors_file:
            return {}
        
        try:
            path = Path(self.config.trusted_authors_file)
            if path.exists():
                return json.loads(path.read_text())
        except Exception:
            pass
        
        return {}
    
    def verify(self, skill: Skill) -> List[Finding]:
        """
        Verify skill trust chain.
        
        Args:
            skill: Skill instance to verify
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        # 1. Check source attribution
        findings.extend(self._verify_source(skill))
        
        # 2. Check signature (if configured)
        if self.config.require_signature:
            findings.extend(self._verify_signature(skill))
        
        # 3. Check author trust level
        findings.extend(self._verify_author(skill))
        
        # 4. Calculate content hash for audit trail
        content_hash = self._calculate_hash(skill)
        
        # 5. Log to audit trail
        self._log_audit(skill, content_hash, findings)
        
        return findings
    
    def _verify_source(self, skill: Skill) -> List[Finding]:
        """Verify source attribution."""
        findings = []
        
        source = skill.source
        
        if source == "unknown" or not source:
            findings.append(Finding(
                level="L4",
                name="unknown_source",
                description="Skill has no source attribution",
                severity=0.40,
                mitigation="Add 'source' field with URL or 'self' if original work"
            ))
        elif source == "self":
            findings.append(Finding(
                level="L4",
                name="self_attributed",
                description="Skill is self-attributed (original work)",
                severity=0.10
            ))
        elif source.startswith("http"):
            # Check if source is from known trusted repositories
            trusted_domains = [
                "github.com/anthropics",
                "github.com/google",
                "github.com/microsoft",
                "github.com/openai",
            ]
            
            is_trusted = any(domain in source for domain in trusted_domains)
            
            if is_trusted:
                findings.append(Finding(
                    level="L4",
                    name="trusted_source",
                    description=f"Source from trusted repository: {source[:50]}",
                    severity=0.0
                ))
            else:
                findings.append(Finding(
                    level="L4",
                    name="external_source",
                    description=f"Source from external repository: {source[:50]}",
                    severity=0.20
                ))
        
        return findings
    
    def _verify_signature(self, skill: Skill) -> List[Finding]:
        """Verify cryptographic signature."""
        findings = []
        
        # Check for signature file
        sig_file = skill.path / "SKILL.md.sig"
        
        if not sig_file.exists():
            findings.append(Finding(
                level="L4",
                name="missing_signature",
                description="No signature file found (SKILL.md.sig)",
                severity=0.30,
                mitigation="Sign skill with: gpg --sign --armor SKILL.md"
            ))
            return findings
        
        # Verify signature (placeholder for actual GPG verification)
        try:
            # In production, this would use gpg --verify
            findings.append(Finding(
                level="L4",
                name="signature_found",
                description="Signature file exists (verification not implemented)",
                severity=0.05
            ))
        except Exception as e:
            findings.append(Finding(
                level="L4",
                name="signature_invalid",
                description=f"Signature verification failed: {e}",
                severity=0.60
            ))
        
        return findings
    
    def _verify_author(self, skill: Skill) -> List[Finding]:
        """Verify author trust level."""
        findings = []
        
        # Get author from metadata
        author = skill.metadata.get("author", "unknown")
        trust_level = skill.metadata.get("trust_level", "community")
        
        # Check against trusted authors registry
        if author in self.trusted_authors:
            author_info = self.trusted_authors[author]
            reputation = author_info.get("reputation", 0.5)
            verified = author_info.get("verified", False)
            
            if verified and reputation >= 0.8:
                findings.append(Finding(
                    level="L4",
                    name="trusted_author",
                    description=f"Author '{author}' is verified (reputation: {reputation})",
                    severity=0.0
                ))
            elif reputation >= 0.5:
                findings.append(Finding(
                    level="L4",
                    name="known_author",
                    description=f"Author '{author}' is known (reputation: {reputation})",
                    severity=0.10
                ))
            else:
                findings.append(Finding(
                    level="L4",
                    name="low_reputation",
                    description=f"Author '{author}' has low reputation ({reputation})",
                    severity=0.40
                ))
        else:
            # Unknown author
            if trust_level == "official":
                findings.append(Finding(
                    level="L4",
                    name="official_skill",
                    description="Skill marked as official",
                    severity=0.0
                ))
            elif trust_level == "verified":
                findings.append(Finding(
                    level="L4",
                    name="verified_skill",
                    description="Skill marked as verified",
                    severity=0.05
                ))
            else:
                findings.append(Finding(
                    level="L4",
                    name="community_skill",
                    description="Community-contributed skill (not individually verified)",
                    severity=0.15
                ))
        
        return findings
    
    def _calculate_hash(self, skill: Skill) -> str:
        """Calculate SHA-256 hash of skill content."""
        content = skill.content.encode('utf-8')
        return hashlib.sha256(content).hexdigest()
    
    def _log_audit(
        self,
        skill: Skill,
        content_hash: str,
        findings: List[Finding]
    ):
        """Log verification to audit trail."""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill_name": skill.name,
            "skill_path": str(skill.path),
            "content_hash": content_hash,
            "source": skill.source,
            "risk_level": skill.risk_level,
            "findings_count": len(findings),
            "max_severity": max([f.severity for f in findings], default=0),
        }
        
        # Append to audit log (in production, use proper logging)
        try:
            log_path = Path(self.config.audit_log_file)
            with open(log_path, 'a') as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception:
            pass  # Silently fail for audit logging
