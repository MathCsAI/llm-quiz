# Hugging Face Space Deployment Fix Guide

## Current Issue

Your Space at https://mathcsai-llm-quiz-solve.hf.space returns:
- **Status**: 404 Not Found
- **Response**: Generic Hugging Face HTML (not your FastAPI app)
- **Root cause**: Space not properly configured as Docker or build failed

## How to Fix

### Step 1: Verify Space Configuration

Go to: https://huggingface.co/spaces/MathCsAi/llm-quiz-solve/settings

Check these settings:

#### Space SDK
- **Current**: Likely set to "Gradio" or "Streamlit"
- **Required**: Must be **"Docker"**
- **Fix**: Click "Settings" → "Change Space hardware" → Select "Docker" as SDK

#### Space Hardware
- **Recommended**: CPU basic (free tier works fine)
- **Note**: First build takes ~10-15 minutes

### Step 2: Link to GitHub Repository

In Space Settings → Repository:
- **GitHub Repository**: MathCsAI/llm-quiz
- **Branch**: main
- **Enable**: "Sync with GitHub" (auto-deploy on push)

### Step 3: Configure Secrets

In Space Settings → Repository secrets, add:

```
EMAIL = 23f2003858@ds.study.iitm.ac.in
SECRET_KEY = 12356789
AI_PIPE_TOKEN = eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDM4NThAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.Lsap03tUtUxz3_rF2c4EQpByfAegYVp0JdllPE_bPKc
```

**Important**: These must match exactly (case-sensitive).

### Step 4: Verify Files in Space

Ensure these files are in the Space repository:
```
✅ Dockerfile
✅ app.py
✅ quiz_solver.py
✅ scraper.py
✅ prompts.py
✅ requirements.txt
✅ README.md (optional but recommended)
```

### Step 5: Check Dockerfile

Your `Dockerfile` should have:

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# System dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates \
    fonts-liberation fonts-noto fonts-noto-color-emoji \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    ... (other libs)
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright (NO --with-deps flag!)
RUN playwright install chromium

# Copy app code
COPY app.py quiz_solver.py scraper.py prompts.py ./

# Expose port
EXPOSE 7860
ENV PORT=7860

# Run FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
```

**Critical**: Must have `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]`

### Step 6: Force Rebuild

After changing SDK to Docker:
1. Click "Settings" → "Factory reboot" (this clears cache)
2. Or: Make a small commit to trigger rebuild:
   ```bash
   echo "# trigger rebuild" >> README.md
   git add README.md
   git commit -m "Trigger HF rebuild"
   git push origin main
   ```

### Step 7: Monitor Build Logs

In your Space page:
- Click "Logs" tab
- Watch for:
  ```
  Building Docker image...
  Installing dependencies...
  playwright install chromium
  INFO:     Started server process [1]
  INFO:     Uvicorn running on http://0.0.0.0:7860
  ```

**Build time**: ~10-15 minutes for first build

### Step 8: Test When Live

Once logs show "Uvicorn running on http://0.0.0.0:7860":

```bash
# Health check
curl https://mathcsai-llm-quiz-solve.hf.space/

# Full test suite
python3 test_cases.py --hf-endpoint https://mathcsai-llm-quiz-solve.hf.space

# Quick validation
curl -X POST https://mathcsai-llm-quiz-solve.hf.space/receive_request \
  -H "Content-Type: application/json" \
  -d '{"email":"23f2003858@ds.study.iitm.ac.in","secret":"12356789","url":"https://tds-llm-analysis.s-anand.net/demo"}'
```

Expected response:
```json
{
  "status": "accepted",
  "message": "Quiz request accepted. Processing in background.",
  "quiz_url": "https://tds-llm-analysis.s-anand.net/demo",
  "email": "23f2003858@ds.study.iitm.ac.in"
}
```

## Common Issues and Solutions

### Issue: 404 Not Found
**Cause**: Wrong SDK (Gradio instead of Docker)
**Fix**: Change to Docker SDK in Settings

### Issue: 503 Service Unavailable
**Cause**: Space is building or sleeping
**Fix**: Wait for build to complete (~10 min) or wake up Space by visiting URL

### Issue: 500 Internal Server Error
**Cause**: Missing environment variables or Playwright not installed
**Fix**: 
- Check secrets are configured
- Verify Dockerfile has `playwright install chromium` (no --with-deps)
- Check logs for errors

### Issue: Build fails with "ttf-ubuntu-font-family not found"
**Cause**: Old Dockerfile with Ubuntu packages on Debian
**Fix**: Use `fonts-noto` and `fonts-noto-color-emoji` instead

### Issue: "SECRET_KEY not configured"
**Cause**: Environment variables not set in Space
**Fix**: Add secrets in Space Settings → Repository secrets

## Verification Checklist

Before submitting to evaluation:

- [ ] Space SDK set to Docker
- [ ] Secrets configured (EMAIL, SECRET_KEY, AI_PIPE_TOKEN)
- [ ] Build logs show "Uvicorn running on http://0.0.0.0:7860"
- [ ] Health check returns 200 OK with JSON
- [ ] Valid request returns 200 OK
- [ ] Invalid secret returns 403 Forbidden
- [ ] Missing fields returns 400 Bad Request
- [ ] All 9 tests pass in test suite

## Quick Test Commands

```bash
# Status check
python3 check_hf_deployment.py --url https://mathcsai-llm-quiz-solve.hf.space

# Full validation
python3 test_cases.py --hf-endpoint https://mathcsai-llm-quiz-solve.hf.space

# Manual curl test
curl -X POST https://mathcsai-llm-quiz-solve.hf.space/receive_request \
  -H "Content-Type: application/json" \
  -d '{"email":"23f2003858@ds.study.iitm.ac.in","secret":"12356789","url":"https://tds-llm-analysis.s-anand.net/demo"}'
```

## Need Help?

If still not working:
1. Share Space logs (Settings → Logs → Copy all)
2. Confirm SDK is Docker
3. Verify Dockerfile exists in Space repository
4. Check secrets are set correctly

## Next Steps After Fixing

Once all tests pass (9/9):
1. Submit API endpoint to evaluation form: `https://mathcsai-llm-quiz-solve.hf.space/receive_request`
2. Include GitHub repo: https://github.com/MathCsAI/llm-quiz
3. Add your prompts (100 chars defense, 89 chars attack)
4. Prepare for viva

**Deadline**: Saturday, November 29, 2025, 3:00-4:00 PM IST
