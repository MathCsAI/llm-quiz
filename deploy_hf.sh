#!/bin/bash

# Quick Deployment Setup Script for Hugging Face

echo "=========================================="
echo "Hugging Face Spaces Deployment Setup"
echo "=========================================="
echo ""

# Check if HF CLI is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "Installing Hugging Face CLI..."
    pip install -q huggingface-hub
fi

echo "Step 1: Login to Hugging Face"
echo "You'll be prompted for your HF token"
echo "Get it from: https://huggingface.co/settings/tokens"
echo ""
huggingface-cli login

# Get HF username
echo ""
echo "Enter your Hugging Face username:"
read HF_USERNAME

# Create Space
echo ""
echo "Step 2: Creating Hugging Face Space..."
huggingface-cli repo create llm-quiz-solver --type space --space_sdk docker --org $HF_USERNAME 2>/dev/null || echo "Space already exists (this is fine)"

# Add HF remote
echo ""
echo "Step 3: Adding Hugging Face remote..."
cd /workspaces/llm-quiz
git remote remove hf 2>/dev/null || true
git remote add hf https://huggingface.co/spaces/$HF_USERNAME/llm-quiz-solver

# Push to HF
echo ""
echo "Step 4: Pushing to Hugging Face Space..."
git push hf main --force

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Your Space: https://huggingface.co/spaces/$HF_USERNAME/llm-quiz-solver"
echo ""
echo "Next Steps:"
echo "1. Go to your Space settings"
echo "2. Add these secrets:"
echo "   - SECRET_KEY: Your quiz secret"
echo "   - EMAIL: 23f2003858@ds.study.iitm.ac.in"
echo "   - AI_PIPE_TOKEN: Your AI Pipe token"
echo ""
echo "3. Wait 5-10 minutes for build"
echo "4. Your API: https://$HF_USERNAME-llm-quiz-solver.hf.space"
echo ""
echo "=========================================="
