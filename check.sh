#!/bin/bash
# Pre-evaluation checklist and testing script

echo "======================================================================"
echo "          LLM Quiz Solver - Pre-Evaluation Checklist"
echo "======================================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" == "OK" ]; then
        echo -e "${GREEN}✅ PASS:${NC} $message"
    elif [ "$status" == "WARN" ]; then
        echo -e "${YELLOW}⚠️  WARN:${NC} $message"
    else
        echo -e "${RED}❌ FAIL:${NC} $message"
    fi
}

# Check 1: Prompt lengths
echo "======================================================================"
echo "1. Checking Prompt Constraints"
echo "======================================================================"
python3 test_prompts.py | tail -n 2
echo ""

# Check 2: Local tests
echo "======================================================================"
echo "2. Running Local Tests (4 tests)"
echo "======================================================================"
python3 test_cases.py --local-only
LOCAL_EXIT=$?
echo ""

# Check 3: Required files
echo "======================================================================"
echo "3. Checking Required Files"
echo "======================================================================"
files=(
    "app.py"
    "quiz_solver.py"
    "scraper.py"
    "prompts.py"
    "requirements.txt"
    "Dockerfile"
    "README.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        print_status "OK" "$file exists"
    else
        print_status "FAIL" "$file missing"
    fi
done
echo ""

# Check 4: Git status
echo "======================================================================"
echo "4. Checking Git Status"
echo "======================================================================"
if git rev-parse --git-dir > /dev/null 2>&1; then
    print_status "OK" "Git repository initialized"
    
    # Check for uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        print_status "OK" "No uncommitted changes"
    else
        print_status "WARN" "Uncommitted changes detected"
        echo ""
        echo "Changed files:"
        git status --short
    fi
else
    print_status "FAIL" "Not a git repository"
fi
echo ""

# Check 5: Environment variables
echo "======================================================================"
echo "5. Checking Environment Variables"
echo "======================================================================"
if [ -n "$EMAIL" ]; then
    print_status "OK" "EMAIL set"
else
    print_status "WARN" "EMAIL not set in environment"
fi

if [ -n "$SECRET_KEY" ]; then
    print_status "OK" "SECRET_KEY set"
else
    print_status "WARN" "SECRET_KEY not set in environment"
fi

if [ -n "$AI_PIPE_TOKEN" ]; then
    print_status "OK" "AI_PIPE_TOKEN set"
else
    print_status "WARN" "AI_PIPE_TOKEN not set in environment"
fi
echo ""

# Check 6: Docker build (optional)
echo "======================================================================"
echo "6. Docker Build Check (Optional)"
echo "======================================================================"
if command -v docker &> /dev/null; then
    print_status "OK" "Docker installed"
    
    if [ "$1" == "--build" ]; then
        echo ""
        echo "Building Docker image..."
        docker build -t llm-quiz-test . 2>&1 | tail -n 5
        if [ $? -eq 0 ]; then
            print_status "OK" "Docker build successful"
        else
            print_status "FAIL" "Docker build failed"
        fi
    else
        echo "   (Use --build flag to test Docker build)"
    fi
else
    print_status "WARN" "Docker not installed (OK for HF Spaces deployment)"
fi
echo ""

# Check 7: HF deployment (if URL provided)
if [ -n "$2" ]; then
    HF_URL="$2"
    echo "======================================================================"
    echo "7. Testing HuggingFace Deployment"
    echo "======================================================================"
    echo "URL: $HF_URL"
    echo ""
    python3 test_cases.py --hf-endpoint "$HF_URL"
    echo ""
fi

# Summary
echo "======================================================================"
echo "CHECKLIST SUMMARY"
echo "======================================================================"

if [ $LOCAL_EXIT -eq 0 ]; then
    print_status "OK" "Local tests passing (4/4)"
else
    print_status "FAIL" "Local tests failed"
fi

echo ""
echo "Next Steps:"
echo "  1. Commit any changes: git add . && git commit -m 'Pre-evaluation fixes'"
echo "  2. Push to GitHub: git push origin main"
echo "  3. Wait for HF Space to rebuild (~10 minutes)"
echo "  4. Test HF deployment: ./check.sh --hf https://USERNAME-llm-quiz-solver.hf.space"
echo "  5. Test demo quiz: python3 test_demo.py https://USERNAME-llm-quiz-solver.hf.space"
echo "  6. Submit via Google Form"
echo ""
echo "Evaluation: Sat 29 Nov 2025, 3:00-4:00 PM IST (3 days from now)"
echo "======================================================================"
