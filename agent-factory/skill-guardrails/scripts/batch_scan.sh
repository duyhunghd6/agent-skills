#!/bin/bash
# Batch Skill Scanning Script
# Scans all skills and generates comprehensive report

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="${SKILLS_DIR:-../../skills}"
REPORT_DIR="${REPORT_DIR:-$PROJECT_DIR/reports}"
LEVEL="${LEVEL:-all}"
STRICT="${STRICT:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️ Skill Guardrails Batch Scanner${NC}"
echo "=================================="

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

# Setup virtual environment if not exists
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$PROJECT_DIR/.venv"
fi

# Activate venv
source "$PROJECT_DIR/.venv/bin/activate"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r "$PROJECT_DIR/requirements.txt"

# Create reports directory
mkdir -p "$REPORT_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Run scan
echo -e "${GREEN}Starting security scan...${NC}"
echo "Skills Directory: $SKILLS_DIR"
echo "Security Level: $LEVEL"
echo ""

cd "$PROJECT_DIR"

if [ "$STRICT" = "true" ]; then
    python -m src.main scan \
        --skills-dir "$SKILLS_DIR" \
        --level "$LEVEL" \
        --output "$REPORT_DIR/scan_$TIMESTAMP.json" \
        --strict \
        --verbose
else
    python -m src.main scan \
        --skills-dir "$SKILLS_DIR" \
        --level "$LEVEL" \
        --output "$REPORT_DIR/scan_$TIMESTAMP.json" \
        --verbose
fi

# Generate markdown report
echo ""
echo -e "${GREEN}Generating markdown report...${NC}"
python -m src.main report \
    --skills-dir "$SKILLS_DIR" \
    --output "$REPORT_DIR/report_$TIMESTAMP.md" \
    --format markdown

echo ""
echo -e "${GREEN}✅ Scan complete!${NC}"
echo "JSON Report: $REPORT_DIR/scan_$TIMESTAMP.json"
echo "Markdown Report: $REPORT_DIR/report_$TIMESTAMP.md"
