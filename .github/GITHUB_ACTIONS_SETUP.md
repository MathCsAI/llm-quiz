# GitHub Actions Setup for Hugging Face Deployment

## Overview

This repository uses GitHub Actions to automatically deploy to Hugging Face Spaces whenever you push to the `main` branch.

## Setup Instructions

### 1. Create Hugging Face Space

First, create a new Space on Hugging Face:

1. Go to https://huggingface.co/new-space
2. Choose a name: `llm-quiz-solver`
3. Select **Docker** as the SDK
4. Set visibility to **Public**
5. Click "Create Space"

### 2. Get Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `github-actions-deploy`
4. Role: **Write** (required for pushing to Space)
5. Copy the token (you won't see it again!)

### 3. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to your repository: https://github.com/MathCsAI/llm-quiz
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

#### Required Secrets:

**HF_USERNAME**
- Value: Your Hugging Face username (e.g., `MathCsAi`)
- This is the username shown in your HF profile URL

**HF_TOKEN**
- Value: The write token you created in step 2
- Format: `hf_xxxxxxxxxxxxxxxxxxxxx`

### 4. Configure Hugging Face Space Secrets

After the first deployment, configure secrets in your HF Space:

1. Go to https://huggingface.co/spaces/YOUR_USERNAME/llm-quiz-solver
2. Click **Settings** → **Repository secrets**
3. Add these secrets:

**EMAIL**
- Your email from Google Form submission
- Example: `student@example.com`

**SECRET_KEY**
- Your secret string from Google Form
- Example: `your-secret-123`

**GEMINI_API_KEY**
- Your Gemini API key
- Get from: https://ai.google.dev/
- Format: `AIza...`

## How It Works

### Automatic Deployment

The workflow (`.github/workflows/deploy-hf.yml`) automatically:

1. Triggers on every push to `main` branch
2. Checks out your repository
3. Pushes code to Hugging Face Space
4. HF automatically builds Docker image
5. Deploys updated application

### Workflow Trigger

```yaml
on:
  push:
    branches:
      - main
  workflow_dispatch:  # Manual trigger option
```

### Manual Deployment

You can also trigger deployment manually:

1. Go to **Actions** tab in GitHub
2. Select **Deploy to Hugging Face Spaces**
3. Click **Run workflow**

## Monitoring Deployment

### GitHub Actions

View deployment status:
1. Go to **Actions** tab
2. Click on the latest workflow run
3. View logs for each step

### Hugging Face Space

View build status:
1. Go to your Space: https://huggingface.co/spaces/YOUR_USERNAME/llm-quiz-solver
2. Check the **Build** tab for Docker build logs
3. Wait ~10 minutes for first build
4. Subsequent builds take ~2-5 minutes (cached)

## Testing Deployment

### 1. Health Check

```bash
curl https://YOUR_USERNAME-llm-quiz-solver.hf.space/
```

Expected response:
```json
{
  "status": "running",
  "message": "LLM Quiz Solver API is operational"
}
```

### 2. Test Quiz Endpoint

```bash
curl -X POST https://YOUR_USERNAME-llm-quiz-solver.hf.space/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "secret": "your-secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

Expected response (200):
```json
{
  "status": "accepted",
  "message": "Quiz task received and processing in background"
}
```

## Troubleshooting

### Workflow Fails

**Error: "remote: Invalid username or password"**
- Check `HF_USERNAME` is correct (case-sensitive)
- Verify `HF_TOKEN` has **Write** permissions
- Generate a new token if needed

**Error: "Repository not found"**
- Ensure Space exists: https://huggingface.co/spaces/YOUR_USERNAME/llm-quiz-solver
- Check Space name is exactly `llm-quiz-solver`
- Verify your username is correct

### Space Build Fails

**Error: "Dockerfile not found"**
- Ensure `Dockerfile` exists in repository root
- Check file is committed to main branch

**Error: "Port 7860 not accessible"**
- Verify `app_port: 7860` in README.md header
- Check Dockerfile exposes port 7860
- Ensure app.py runs on port 7860

### Runtime Errors

**503 Service Unavailable**
- Space is still building (wait 10 minutes)
- Check build logs in Space

**403 Forbidden on API**
- Configure secrets in HF Space settings
- Verify `EMAIL` and `SECRET_KEY` match your submission

**500 Internal Server Error**
- Check `GEMINI_API_KEY` is configured
- View application logs in Space
- Verify all dependencies are installed

## Updating Application

Simply push changes to main:

```bash
git add .
git commit -m "Update application"
git push origin main
```

GitHub Actions will automatically:
1. Detect the push
2. Deploy to Hugging Face
3. Rebuild Docker container
4. Restart application

## Security Notes

### Never Commit Secrets

❌ Don't commit:
- `.env` files with real tokens
- API keys in code
- Passwords or secrets

✅ Do commit:
- `.env.example` with placeholder values
- Configuration templates

### Secret Rotation

If you need to rotate secrets:

1. Generate new token on Hugging Face
2. Update `HF_TOKEN` in GitHub secrets
3. Update other secrets in HF Space settings

## Space URL Format

Your deployed API will be accessible at:

```
https://YOUR_USERNAME-llm-quiz-solver.hf.space/receive_request
```

Replace `YOUR_USERNAME` with your Hugging Face username.

Example:
- Username: `MathCsAi`
- URL: `https://MathCsAi-llm-quiz-solver.hf.space/receive_request`

## Google Form Submission

Use this URL in your Google Form:
```
https://YOUR_USERNAME-llm-quiz-solver.hf.space/receive_request
```

Make sure:
- ✅ Space is deployed and running
- ✅ Secrets are configured
- ✅ Endpoint returns 200 for valid requests
- ✅ Repository is public
- ✅ MIT LICENSE is present

## Workflow File Location

The workflow file is located at:
```
.github/workflows/deploy-hf.yml
```

You can customize:
- Trigger branches
- Deployment steps
- Space name
- Notification settings

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Docker Hub](https://hub.docker.com/)

## Support

If you encounter issues:

1. Check workflow logs in GitHub Actions
2. Review Space build logs on Hugging Face
3. Test locally with Docker first
4. Verify all secrets are configured correctly
