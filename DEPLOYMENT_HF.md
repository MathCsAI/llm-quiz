# Hugging Face Spaces Deployment Guide

## Quick Start

1. **Create a new Space** on Hugging Face:
   - Go to https://huggingface.co/new-space
   - Choose "Docker" as SDK
   - Name it `llm-quiz-solver`

2. **Clone and push this repository**:
   ```bash
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/llm-quiz-solver
   git push hf main
   ```

3. **Configure Secrets** in Space Settings → Repository secrets:
   - `EMAIL`: Your email from Google Form
   - `SECRET_KEY`: Your secret string from Google Form
   - `AI_PIPE_TOKEN`: Your AI Pipe token

4. **Wait for build** (~10 minutes)

5. **Test your endpoint**:
   ```bash
   curl -X POST https://YOUR_USERNAME-llm-quiz-solver.hf.space/receive_request \
     -H "Content-Type: application/json" \
     -d '{"email":"your-email","secret":"your-secret","url":"https://tds-llm-analysis.s-anand.net/demo"}'
   ```

## Configuration Details

### README.md Header

The YAML header in README.md configures the Space:
```yaml
---
title: LLM Quiz Solver
emoji: 🤖
sdk: docker
app_port: 7860
---
```

### Dockerfile

The Dockerfile installs:
- Python 3.11
- Playwright with Chromium browser
- All Python dependencies
- System dependencies for headless browsing

### Environment Variables

Set these in Space Settings:
- `EMAIL`: Validates incoming requests
- `SECRET_KEY`: Authenticates requests
- `AI_PIPE_TOKEN`: Enables LLM API calls

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Ensure all dependencies are in requirements.txt
- Review build logs in Space

### Runtime Errors
- Verify secrets are configured
- Check application logs in Space
- Test locally first with Docker

### Timeout Issues
- Playwright installation is slow (~5 min)
- First build takes ~10 minutes
- Subsequent builds use cache (~2 min)

## Testing

### Local Testing with Docker
```bash
docker build -t llm-quiz-solver .
docker run -p 7860:7860 \
  -e EMAIL=your-email \
  -e SECRET_KEY=your-secret \
  -e AI_PIPE_TOKEN=your-token \
  llm-quiz-solver
```

### Test Endpoint
```bash
curl http://localhost:7860/
curl -X POST http://localhost:7860/receive_request \
  -H "Content-Type: application/json" \
  -d '{"email":"your-email","secret":"your-secret","url":"https://tds-llm-analysis.s-anand.net/demo"}'
```

## Monitoring

Check logs in Hugging Face Space:
- Application logs show quiz processing
- Error logs help debug issues
- Request logs track API calls

## Updating

To update your deployment:
```bash
git add .
git commit -m "Update application"
git push hf main
```

The Space will automatically rebuild and redeploy.
