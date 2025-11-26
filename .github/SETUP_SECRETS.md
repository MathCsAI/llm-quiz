# GitHub Actions Secrets Setup

To enable automatic deployment to Hugging Face Spaces, configure these secrets in your GitHub repository.

## Required Secrets

### 1. HF_TOKEN
Your Hugging Face access token with write permissions.

**How to get it:**
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it (e.g., "GitHub Actions Deploy")
4. Select **Write** permission
5. Click "Generate token"
6. Copy the token (starts with `hf_...`)

### 2. HF_USERNAME
Your Hugging Face username.

**For this repo:**
```
MathCsAi
```

The Space name is hardcoded in the workflow as `llm-quiz-solver`.

## Adding Secrets to GitHub

### Via Web UI
1. Go to: https://github.com/MathCsAI/llm-quiz/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret:
   - Name: `HF_TOKEN`, Value: `hf_xxxxxxxxxxxxx`
   - Name: `HF_USERNAME`, Value: `MathCsAi`

### Via GitHub CLI (if available)
```bash
# Set HF_TOKEN
gh secret set HF_TOKEN --body "hf_xxxxxxxxxxxxx"

# Set HF_USERNAME
gh secret set HF_USERNAME --body "MathCsAi"
```

## Verify Deployment

Once secrets are added:
1. Push any commit to `main` branch (or manually trigger workflow)
2. Go to: https://github.com/MathCsAI/llm-quiz/actions
3. Check "Deploy to Hugging Face Spaces" workflow
4. Wait for green checkmark ✓
5. Visit your Space: https://huggingface.co/spaces/MathCsAi/llm-quiz-solver

## Troubleshooting

### Workflow fails with "HF_USERNAME is not set"
- Double-check secret names match exactly (case-sensitive)
- Verify secrets are added at repository level, not environment level

### Workflow fails with authentication error
- Ensure HF_TOKEN has **Write** permission (not just Read)
- Try generating a new token if the old one is invalid

### Space build fails
- Check Space build logs at: https://huggingface.co/spaces/MathCsAi/llm-quiz-solver/settings
- Look for Docker build errors
- Verify `Dockerfile.hf` syntax is valid
