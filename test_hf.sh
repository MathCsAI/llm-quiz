#!/bin/bash
# Quick test script for Hugging Face deployment

echo "======================================================================"
echo "          LLM Quiz Solver - Deployment Testing"
echo "======================================================================"
echo ""

# Check if HF username is provided
if [ -z "$1" ]; then
    echo "❌ Please provide your Hugging Face username"
    echo ""
    echo "Usage: ./test_hf.sh YOUR_HF_USERNAME"
    echo ""
    echo "Example: ./test_hf.sh john-doe"
    echo ""
    echo "Or test with direct URL:"
    echo "  python3 check_hf_deployment.py --url https://username-llm-quiz-solver.hf.space"
    exit 1
fi

HF_USERNAME="$1"
SPACE_NAME="llm-quiz-solver"
HF_URL="https://${HF_USERNAME}-${SPACE_NAME}.hf.space"

echo "📋 Configuration:"
echo "   Username: $HF_USERNAME"
echo "   Space: $SPACE_NAME"
echo "   URL: $HF_URL"
echo ""

# Check Space status
echo "🔍 Checking Space status..."
python3 check_hf_deployment.py --username "$HF_USERNAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo "✅ Space is online! Running full test suite..."
    echo "======================================================================"
    echo ""
    python3 test_cases.py --hf-endpoint "$HF_URL"
else
    echo ""
    echo "⏳ Space not ready yet. To check status:"
    echo "   https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"
    echo ""
    echo "Once ready, run full tests with:"
    echo "   python3 test_cases.py --hf-endpoint $HF_URL"
fi
