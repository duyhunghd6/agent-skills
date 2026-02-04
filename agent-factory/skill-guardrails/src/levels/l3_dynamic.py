"""
Level 3: Dynamic Analysis (Sandbox Execution)

Executes skills in isolated sandbox environment to detect:
- Runtime behavior anomalies
- File system access patterns
- Network call attempts
- Resource consumption
"""

import os
import subprocess
import tempfile
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from ..models.skill import Skill, Finding


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""
    enabled: bool = True
    image: str = "python:3.11-slim"
    memory_limit: str = "256m"
    cpu_limit: str = "0.5"
    timeout: int = 30
    network_disabled: bool = True


class DynamicAnalyzer:
    """
    Level 3 Security Analysis - Sandbox Execution
    
    Executes skill code blocks in isolated Docker container to detect:
    - File system access patterns
    - Network call attempts  
    - Resource consumption anomalies
    - Unexpected process spawning
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.docker_available = self._check_docker()
    
    def _load_config(self) -> SandboxConfig:
        """Load sandbox configuration from environment."""
        return SandboxConfig(
            enabled=os.getenv("SANDBOX_ENABLED", "true").lower() == "true",
            image=os.getenv("SANDBOX_IMAGE", "python:3.11-slim"),
            memory_limit=os.getenv("SANDBOX_MEMORY_LIMIT", "256m"),
            cpu_limit=os.getenv("SANDBOX_CPU_LIMIT", "0.5"),
            timeout=int(os.getenv("SCAN_TIMEOUT", "30")),
            network_disabled=True
        )
    
    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def analyze(self, skill: Skill) -> List[Finding]:
        """
        Run dynamic analysis on a skill.
        
        Args:
            skill: Skill instance to analyze
            
        Returns:
            List of Finding objects
        """
        findings = []
        
        # Check if sandbox is enabled and Docker available
        if not self.config.enabled:
            findings.append(Finding(
                level="L3",
                name="sandbox_disabled",
                description="Sandbox execution disabled",
                severity=0.0
            ))
            return findings
        
        if not self.docker_available:
            findings.append(Finding(
                level="L3",
                name="docker_unavailable",
                description="Docker not available - skipping dynamic analysis",
                severity=0.05,
                mitigation="Install Docker to enable sandbox execution"
            ))
            return findings
        
        # Extract testable code blocks
        code_blocks = self._extract_testable_code(skill)
        
        if not code_blocks:
            findings.append(Finding(
                level="L3",
                name="no_testable_code",
                description="No testable code blocks found",
                severity=0.0
            ))
            return findings
        
        # Run each code block in sandbox
        for i, block in enumerate(code_blocks):
            block_findings = self._run_in_sandbox(block, skill.name, i)
            findings.extend(block_findings)
        
        return findings
    
    def _extract_testable_code(self, skill: Skill) -> List[Dict[str, str]]:
        """Extract code blocks that can be tested."""
        testable = []
        
        for block in skill.code_blocks:
            lang = block["language"].lower()
            code = block["code"]
            
            # Only test Python and shell scripts
            if lang in ["python", "py", "bash", "sh", "shell"]:
                # Skip if code is too short or just comments
                lines = [l for l in code.strip().split('\n') if l.strip() and not l.strip().startswith('#')]
                if len(lines) > 0 and len(code.strip()) > 10:
                    testable.append({
                        "language": lang,
                        "code": code
                    })
        
        return testable[:5]  # Limit to first 5 blocks
    
    def _run_in_sandbox(
        self,
        code_block: Dict[str, str],
        skill_name: str,
        block_index: int
    ) -> List[Finding]:
        """Run code block in Docker sandbox."""
        findings = []
        lang = code_block["language"]
        code = code_block["code"]
        
        # Create temp file with code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py' if lang in ['python', 'py'] else '.sh',
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Build Docker command
            docker_cmd = [
                "docker", "run",
                "--rm",
                "--network=none" if self.config.network_disabled else "",
                f"--memory={self.config.memory_limit}",
                f"--cpus={self.config.cpu_limit}",
                "--read-only",
                "--security-opt=no-new-privileges",
                "-v", f"{temp_file}:/code/script:ro",
                self.config.image,
            ]
            
            # Add execution command
            if lang in ["python", "py"]:
                docker_cmd.extend(["python", "/code/script"])
            else:
                docker_cmd.extend(["sh", "/code/script"])
            
            # Filter empty strings
            docker_cmd = [c for c in docker_cmd if c]
            
            # Execute with timeout
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            # Analyze result
            findings.extend(
                self._analyze_execution_result(result, skill_name, block_index)
            )
            
        except subprocess.TimeoutExpired:
            findings.append(Finding(
                level="L3",
                name="execution_timeout",
                description=f"Code block {block_index} exceeded timeout ({self.config.timeout}s)",
                severity=0.60,
                mitigation="Review code for infinite loops or excessive computation"
            ))
        except Exception as e:
            findings.append(Finding(
                level="L3",
                name="sandbox_error",
                description=f"Sandbox execution error: {str(e)}",
                severity=0.10
            ))
        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return findings
    
    def _analyze_execution_result(
        self,
        result: subprocess.CompletedProcess,
        skill_name: str,
        block_index: int
    ) -> List[Finding]:
        """Analyze sandbox execution result."""
        findings = []
        
        # Check for suspicious stderr patterns
        stderr = result.stderr.lower()
        
        suspicious_patterns = [
            ("permission denied", "permission_denied", 0.40),
            ("network unreachable", "network_attempt", 0.70),
            ("connection refused", "network_attempt", 0.60),
            ("curl:", "external_request", 0.65),
            ("wget:", "external_request", 0.65),
            ("socket.error", "socket_usage", 0.55),
            ("subprocess", "subprocess_call", 0.50),
        ]
        
        for pattern, name, severity in suspicious_patterns:
            if pattern in stderr:
                findings.append(Finding(
                    level="L3",
                    name=name,
                    description=f"Suspicious activity detected in block {block_index}: {pattern}",
                    severity=severity,
                    code_snippet=stderr[:200]
                ))
        
        # Check for success/failure
        if result.returncode != 0 and result.returncode != 1:
            findings.append(Finding(
                level="L3",
                name="abnormal_exit",
                description=f"Code block {block_index} exited with code {result.returncode}",
                severity=0.30
            ))
        
        return findings
