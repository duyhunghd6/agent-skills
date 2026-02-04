# 🛡️ Skill Guardrails - AI Security Framework

> **Multi-Level Security Verification System for Agent Skills**

This module provides a comprehensive security verification framework for validating agent skills before they are loaded into IDE coding environments. It implements a Defense-in-Depth architecture with 4 security levels.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SKILL GUARDRAILS PIPELINE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📥 Input Skill ──► 🔵 L1 ──► 🟠 L2 ──► 🔴 L3 ──► 🟣 L4 ──► ✅ Output │
│                     Static   Semantic  Dynamic   Trust              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Security Levels

| Level | Name               | Description                               | Auto-Run          |
| ----- | ------------------ | ----------------------------------------- | ----------------- |
| 🔵 L1 | Static Analysis    | Pattern detection, metadata validation    | ✅ Yes            |
| 🟠 L2 | Semantic Analysis  | AI-powered intent classification (Gemini) | ✅ Yes            |
| 🔴 L3 | Dynamic Analysis   | Sandbox execution, behavior monitoring    | ⚠️ High-risk only |
| 🟣 L4 | Trust Verification | Signature verification, audit trail       | ✅ Yes            |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure Gemini API
cp .env.example .env
# Edit .env with your Gemini API URL and key

# Run full scan on all skills
python -m src.main scan --skills-dir ../../skills

# Run quick scan (L1 only)
python -m src.main scan --level L1 --skills-dir ../../skills

# Scan single skill
python -m src.main scan --skill ../../skills/python-pro

# Generate security report
python -m src.main report --output reports/security-report.json
```

## Directory Structure

```
skill-guardrails/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── scanner.py           # Main orchestrator
│   ├── levels/
│   │   ├── __init__.py
│   │   ├── l1_static.py     # Pattern detection
│   │   ├── l2_semantic.py   # AI classification (Gemini)
│   │   ├── l3_dynamic.py    # Sandbox execution
│   │   └── l4_trust.py      # Signature verification
│   ├── models/
│   │   ├── __init__.py
│   │   ├── skill.py         # Skill data model
│   │   └── report.py        # Report data model
│   └── utils/
│       ├── __init__.py
│       ├── gemini_client.py # Gemini API wrapper
│       └── patterns.py      # Dangerous pattern library
├── config/
│   ├── patterns.yaml        # Pattern detection rules
│   └── thresholds.yaml      # Risk score thresholds
├── tests/
│   ├── __init__.py
│   ├── test_l1_static.py
│   ├── test_l2_semantic.py
│   └── fixtures/            # Test skill fixtures
├── scripts/
│   └── batch_scan.sh        # Batch scanning script
├── reports/                  # Generated reports (gitignored)
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

### Environment Variables (.env)

```bash
# Gemini API Configuration
GEMINI_API_URL=https://your-gemini-endpoint.com
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.0-flash

# Scanning Configuration
SCAN_PARALLEL=4
SCAN_TIMEOUT=30
LOG_LEVEL=INFO

# Risk Thresholds
RISK_THRESHOLD_HIGH=0.6
RISK_THRESHOLD_CRITICAL=0.8
```

### Pattern Configuration (config/patterns.yaml)

```yaml
patterns:
  critical:
    - name: code_execution
      pattern: 'eval\s*\('
      severity: 0.9
    - name: shell_execution
      pattern: 'subprocess\.'
      severity: 0.9
  high:
    - name: prompt_injection
      pattern: 'ignore\s+(previous|prior)\s+(instructions?|prompts?)'
      severity: 0.7
```

## Risk Scoring

```
Risk Score = (
    0.40 × Pattern Severity +
    0.30 × Permission Scope +
    0.20 × Source Trust +
    0.10 × Community Reports
)
```

| Score   | Classification | Action               |
| ------- | -------------- | -------------------- |
| 0.0-0.3 | 🟢 Low Risk    | Auto-approve         |
| 0.3-0.6 | 🟡 Medium Risk | Flag for review      |
| 0.6-0.8 | 🟠 High Risk   | Require human review |
| 0.8-1.0 | 🔴 Critical    | Block & quarantine   |

## Output Formats

### JSON Report

```json
{
  "scan_id": "uuid",
  "timestamp": "2025-02-04T18:00:00Z",
  "total_skills": 629,
  "results": {
    "passed": 580,
    "flagged": 40,
    "blocked": 9
  },
  "high_risk_skills": [...]
}
```

### Console Output

```
🔍 Skill Guardrails Scan
========================
📊 Scanned: 629 skills
✅ Passed: 580 (92.2%)
⚠️ Flagged: 40 (6.4%)
🚨 Blocked: 9 (1.4%)

High-Risk Skills Requiring Review:
  1. 🔴 active-directory-attacks (0.85) - offensive tool
  2. 🔴 sql-injection-testing (0.82) - offensive tool
  ...
```

## Integration with CI/CD

Add to `.github/workflows/ci.yml`:

```yaml
- name: 🛡️ Security Scan
  run: |
    cd agent-factory/skill-guardrails
    pip install -r requirements.txt
    python -m src.main scan --skills-dir ../../skills --strict
```

## License

MIT - Same as parent repository
