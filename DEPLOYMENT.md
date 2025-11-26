# Deployment Guide

## Deployment Options

### Option 1: GitHub Codespaces (Recommended)

GitHub Codespaces provides a complete development environment in the cloud with all dependencies pre-installed.

#### Steps:

1. **Push code to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Create Codespace:**
   - Go to your GitHub repository
   - Click "Code" → "Codespaces" → "Create codespace on main"
   - Wait for environment to initialize

3. **Configure environment:**
```bash
cp .env.example .env
nano .env
```

4. **Install dependencies:**
```bash
./setup.sh
```

5. **Start server:**
```bash
./start_server.sh
```

6. **Get public URL:**
   - VS Code will show "Port 8000 forwarded"
   - Click "Ports" tab → Right-click 8000 → "Port Visibility" → "Public"
   - Copy the forwarded URL (e.g., `https://xxx-8000.app.github.dev`)
   - Use this URL as your API endpoint

### Option 2: Render.com (Free Tier)

Render provides free hosting for web services with automatic deployments from GitHub.

#### Steps:

1. **Prepare for deployment:**

Create `render.yaml`:
```yaml
services:
  - type: web
    name: llm-quiz-solver
    env: python
    buildCommand: pip install -r requirements.txt && playwright install chromium
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SECRET_KEY
        sync: false
      - key: EMAIL
        sync: false
      - key: AI_PIPE_TOKEN
        sync: false
```

2. **Deploy:**
   - Go to [render.com](https://render.com)
   - Sign in with GitHub
   - Click "New" → "Web Service"
   - Select your repository
   - Render will auto-detect the configuration
   - Add environment variables in dashboard
   - Click "Create Web Service"

3. **Get URL:**
   - Your service URL will be: `https://llm-quiz-solver.onrender.com`

### Option 3: Railway.app

Railway offers simple deployment with generous free tier.

#### Steps:

1. **Deploy:**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python

2. **Configure:**
   - Click on your service → "Variables"
   - Add environment variables:
     - `SECRET_KEY`
     - `EMAIL`
     - `AI_PIPE_TOKEN`
   - Click "Settings" → "Deploy"

3. **Add startup command:**
   - In Settings → "Deploy" → "Custom Start Command"
   - Enter: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Get URL:**
   - Click "Settings" → "Networking" → "Generate Domain"

### Option 4: Heroku

Classic platform with free tier (requires credit card verification).

#### Steps:

1. **Create Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. **Create runtime.txt:**
```
python-3.11.6
```

3. **Deploy:**
```bash
heroku login
heroku create llm-quiz-solver
heroku config:set SECRET_KEY=your_secret
heroku config:set EMAIL=your_email
heroku config:set AI_PIPE_TOKEN=your_token
git push heroku main
```

4. **Install Playwright:**
```bash
heroku buildpacks:add --index 1 https://github.com/mxschmitt/heroku-playwright-buildpack.git
```

### Option 5: Google Cloud Run

Serverless deployment with generous free tier.

#### Steps:

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps

COPY . .

CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. **Deploy:**
```bash
gcloud run deploy llm-quiz-solver \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Set environment variables:**
```bash
gcloud run services update llm-quiz-solver \
  --set-env-vars SECRET_KEY=xxx,EMAIL=xxx,AI_PIPE_TOKEN=xxx
```

### Option 6: ngrok (Local Testing)

Perfect for development and testing before deploying.

#### Steps:

1. **Install ngrok:**
```bash
# Download from https://ngrok.com/download
# Or use snap:
snap install ngrok
```

2. **Start server locally:**
```bash
./start_server.sh
```

3. **Create tunnel:**
```bash
ngrok http 8000
```

4. **Use the ngrok URL:**
   - Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
   - Use this as your temporary API endpoint
   - **Note**: URL changes on each restart (use paid plan for static URL)

## Environment Variables

All deployment platforms need these environment variables:

```
SECRET_KEY=your_secret_string_here
EMAIL=your_email@example.com
AI_PIPE_TOKEN=your_aipipe_token_here
HOST=0.0.0.0
PORT=8000
```

## Testing Your Deployment

After deployment, test with:

```bash
# Health check
curl https://your-url.com/

# Quiz request
curl -X POST https://your-url.com/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```

Expected response:
```json
{
  "status": "accepted",
  "message": "Quiz task accepted and processing in background",
  "url": "https://tds-llm-analysis.s-anand.net/demo"
}
```

## Troubleshooting Deployment

### "Application Error" or crashes
- Check logs: `heroku logs --tail` or platform-specific log viewer
- Verify all environment variables are set
- Ensure Playwright is installed: `playwright install chromium`

### "Port already in use"
- Use `$PORT` environment variable (provided by platform)
- Don't hardcode port 8000

### "Module not found"
- Verify `requirements.txt` is complete
- Check build logs for installation errors

### Playwright browser issues
- Ensure system dependencies are installed
- On Heroku: Use playwright buildpack
- On Docker: Run `playwright install-deps`

### Memory issues
- LLM responses can be large
- Consider upgrading to paid tier if needed
- Implement response streaming for large outputs

## Production Checklist

Before going live:

- [ ] Environment variables configured
- [ ] API endpoint is HTTPS
- [ ] Health check endpoint responds
- [ ] Test with invalid secret (should return 403)
- [ ] Test with invalid JSON (should return 400)
- [ ] Test with demo quiz URL
- [ ] Monitor logs for errors
- [ ] Set up error alerting
- [ ] Document your endpoint URL
- [ ] Submit to Google Form

## Monitoring

### View Logs

**Codespaces/Local:**
```bash
# Server logs appear in terminal
```

**Render:**
- Dashboard → Your Service → Logs tab

**Railway:**
- Dashboard → Your Service → Deployments → View Logs

**Heroku:**
```bash
heroku logs --tail
```

### Health Check

Set up a monitoring service to ping your health endpoint:
- [UptimeRobot](https://uptimerobot.com/) (Free)
- [Pingdom](https://www.pingdom.com/) (Free tier)

Configure to check: `https://your-url.com/` every 5 minutes

## Cost Considerations

### Free Tiers

- **GitHub Codespaces**: 120 core-hours/month free
- **Render**: 750 hours/month free
- **Railway**: $5 credit/month
- **Heroku**: 1000 dyno hours/month (with verification)
- **Google Cloud Run**: 2M requests/month free

### AI Pipe Costs

- Check [AI Pipe pricing](https://aipipe.ai/pricing)
- `gpt-4o-mini` is the most cost-effective model
- Monitor token usage in AI Pipe dashboard

## Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Use platform environment variables

2. **Use HTTPS endpoints**
   - All platforms provide HTTPS by default

3. **Rotate secrets regularly**
   - Change `SECRET_KEY` if compromised

4. **Monitor API usage**
   - Check for unusual patterns
   - Set up rate limiting if needed

5. **Keep dependencies updated**
```bash
pip list --outdated
pip install --upgrade <package>
```

## Support

If you encounter deployment issues:

1. Check platform-specific documentation
2. Review logs carefully
3. Test locally first with ngrok
4. Verify environment variables
5. Check GitHub Issues for similar problems

---

**Choose the deployment option that works best for you and good luck! 🚀**
