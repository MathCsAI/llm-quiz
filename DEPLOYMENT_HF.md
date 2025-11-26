# Deploying to Hugging Face Spaces

## Automatic Deployment from GitHub

### Method 1: Connect GitHub Repository (Recommended)

1. **Go to Hugging Face Spaces**
   - Visit: https://huggingface.co/spaces
   - Click "Create new Space"

2. **Configure Space**
   - Owner: Your HF username
   - Space name: `llm-quiz-solver` (or your choice)
   - License: MIT
   - SDK: Docker
   - Space hardware: CPU basic (free) or upgrade if needed

3. **Connect to GitHub**
   - Select "Import from GitHub"
   - Authorize Hugging Face to access your GitHub
   - Select repository: `MathCsAI/llm-quiz`
   - Branch: `main`

4. **Set Environment Variables (Secrets)**
   - Go to Space Settings → Repository secrets
   - Add these secrets:
     ```
     SECRET_KEY=your_secret_here
     EMAIL=your_email@example.com
     AI_PIPE_TOKEN=your_aipipe_token_here
     ```

5. **Deploy**
   - HF will automatically build and deploy
   - Wait 5-10 minutes for initial build
   - Your Space URL: `https://YOUR-USERNAME-llm-quiz-solver.hf.space`

### Method 2: Manual Git Push

1. **Create Space on Hugging Face**
   - Visit: https://huggingface.co/spaces
   - Click "Create new Space"
   - Configure as above
   - Get the Space's git URL

2. **Add HF as Git Remote**
   ```bash
   cd /workspaces/llm-quiz
   git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/llm-quiz-solver
   ```

3. **Push to Hugging Face**
   ```bash
   git push hf main
   ```

4. **Set Secrets in HF Dashboard**
   - Go to Space Settings → Repository secrets
   - Add: SECRET_KEY, EMAIL, AI_PIPE_TOKEN

### Method 3: Use HF CLI

1. **Install HF CLI**
   ```bash
   pip install huggingface-hub
   ```

2. **Login to Hugging Face**
   ```bash
   huggingface-cli login
   ```

3. **Create and Push Space**
   ```bash
   cd /workspaces/llm-quiz
   
   # Create space
   huggingface-cli repo create llm-quiz-solver --type space --space_sdk docker
   
   # Add remote
   git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/llm-quiz-solver
   
   # Push
   git push hf main
   ```

## Files Required for HF Deployment

These files have been created for you:

- ✅ `README_HF.md` - Space README with metadata
- ✅ `Dockerfile.hf` - Optimized Dockerfile for HF
- ✅ `app.py` - Entry point for HF Spaces
- ✅ `.space` - HF Space configuration

## Dockerfile Configuration

The `Dockerfile.hf` is optimized for Hugging Face Spaces:
- Uses port 7860 (HF standard)
- Includes all Playwright dependencies
- Lightweight and cached layers
- Production-ready

## Setting Up Secrets

### In Hugging Face Dashboard:

1. Go to your Space
2. Click "Settings" tab
3. Scroll to "Repository secrets"
4. Add each secret:
   - Name: `SECRET_KEY`, Value: your secret
   - Name: `EMAIL`, Value: your email
   - Name: `AI_PIPE_TOKEN`, Value: your token

### Access Secrets in Code:

Secrets are automatically available as environment variables:
```python
import os
SECRET_KEY = os.getenv("SECRET_KEY")
EMAIL = os.getenv("EMAIL")
AI_PIPE_TOKEN = os.getenv("AI_PIPE_TOKEN")
```

## Monitoring Your Deployment

### Build Logs
- Go to your Space
- Click "Logs" tab
- Watch the build process

### Application Logs
- Runtime logs appear in the same "Logs" tab
- Check for errors or warnings

## Testing Your Deployment

### Health Check
```bash
curl https://YOUR-USERNAME-llm-quiz-solver.hf.space/
```

### Submit Test Quiz
```bash
curl -X POST https://YOUR-USERNAME-llm-quiz-solver.hf.space/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

## Automatic Updates

Once connected to GitHub:
- Any push to `main` branch automatically redeploys
- Changes take 5-10 minutes to reflect
- Check build status in Space logs

## Space Configuration

Your Space will use these settings from `README_HF.md`:
```yaml
---
title: LLM Quiz Solver
emoji: 🤖
sdk: docker
app_port: 7860
license: mit
---
```

## Upgrading Hardware

If you need more resources:
1. Go to Space Settings
2. Select "Hardware"
3. Upgrade to CPU/GPU options:
   - CPU basic (free)
   - CPU upgrade ($0.60/hour)
   - T4 small GPU ($0.60/hour)
   - A10G small GPU ($3.15/hour)

## Troubleshooting

### Build Fails
- Check Dockerfile.hf syntax
- Verify requirements.txt is valid
- Check logs for specific errors

### Space Crashes
- Check application logs
- Verify secrets are set correctly
- Ensure port 7860 is used

### Playwright Issues
- Dockerfile.hf includes all dependencies
- If issues persist, check system packages
- Consider upgrading to CPU upgrade hardware

## Cost Considerations

### Free Tier
- CPU basic hardware
- Space sleeps after 48h of inactivity
- Automatically wakes on request
- Sufficient for evaluation

### Paid Tier
- Always-on option available
- Better for production use
- No sleep timeout

## Post-Deployment

1. **Test thoroughly**
   ```bash
   python test_endpoint.py https://YOUR-SPACE.hf.space
   ```

2. **Update Google Form**
   - API Endpoint: `https://YOUR-SPACE.hf.space/receive_request`

3. **Monitor during evaluation**
   - Keep Logs tab open
   - Watch for incoming requests
   - Check for errors

## Space URL Format

Your deployed Space will be at:
```
https://YOUR-USERNAME-llm-quiz-solver.hf.space
```

Or with custom domain (Pro feature):
```
https://llm-quiz-solver.YOUR-USERNAME.hf.space
```

## Benefits of HF Spaces

✅ Free hosting with CPU
✅ Automatic HTTPS
✅ Built-in logging
✅ GitHub integration
✅ Easy secret management
✅ No credit card required for free tier
✅ Community visibility (if public)

## Making Space Private

If needed:
1. Go to Space Settings
2. Change visibility to "Private"
3. Access remains via URL with authentication

---

**Your Space is ready to deploy! Choose a method above and deploy now.** 🚀
