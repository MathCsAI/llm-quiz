# Hugging Face Spaces - GitHub Actions Setup

## Automatic Deployment Configuration

I've created GitHub Actions workflows for automatic deployment to Hugging Face Spaces.

### Files Created

1. **`.github/workflows/deploy-hf.yml`** - Main deployment workflow
2. **`.github/workflows/sync-hf.yml`** - Alternative sync workflow

### Setup Instructions

#### Step 1: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Configure:
   - Name: `llm-quiz-solver`
   - License: MIT
   - SDK: Docker
   - Keep it public or private

#### Step 2: Get Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: `GitHub Actions Deploy`
4. Type: Write
5. Copy the token (starts with `hf_`)

#### Step 3: Add GitHub Secrets

1. Go to your GitHub repo: https://github.com/MathCsAI/llm-quiz
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add these secrets:

   **Secret 1:**
   - Name: `HF_TOKEN`
   - Value: Your Hugging Face token (from Step 2)

   **Secret 2:**
   - Name: `HF_USERNAME`
   - Value: Your Hugging Face username

#### Step 4: Configure HF Space Secrets

1. Go to your Space: https://huggingface.co/spaces/YOUR-USERNAME/llm-quiz-solver
2. Click "Settings" tab
3. Scroll to "Repository secrets"
4. Add these secrets:
   - `SECRET_KEY`: Your quiz secret key
   - `EMAIL`: Your email (23f2003858@ds.study.iitm.ac.in)
   - `AI_PIPE_TOKEN`: Your AI Pipe token

#### Step 5: Test Deployment

1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Add GitHub Actions for HF deployment"
   git push origin main
   ```

2. Check GitHub Actions:
   - Go to repo → "Actions" tab
   - Watch the workflow run
   - Should complete in ~1 minute

3. Check HF Space:
   - Go to your Space
   - Click "Building" to see logs
   - Wait 5-10 minutes for build
   - Your API will be at: `https://YOUR-USERNAME-llm-quiz-solver.hf.space`

### How It Works

1. **Trigger**: Any push to `main` branch
2. **Action**: Workflow runs automatically
3. **Process**: 
   - Checks out code
   - Configures git
   - Adds HF remote
   - Force pushes to HF Space
4. **Result**: HF Space rebuilds automatically

### Workflow Features

- ✅ Automatic deployment on every push
- ✅ Manual trigger option (workflow_dispatch)
- ✅ Force push to handle conflicts
- ✅ Configurable via GitHub secrets
- ✅ No local setup required

### Testing Automatic Deployment

After setup, make any change and push:

```bash
# Make a small change
echo "# Test" >> test.txt

# Commit and push
git add test.txt
git commit -m "Test automatic deployment"
git push origin main

# Watch in GitHub Actions tab
```

### Monitoring

**GitHub Actions:**
- Repo → Actions tab
- See deployment status
- View logs if failed

**Hugging Face:**
- Space → Building/Running status
- Click on status for logs
- Check for errors

### Troubleshooting

**Workflow fails with "Authentication failed":**
- Verify `HF_TOKEN` is correct and has write access
- Regenerate token if needed

**Space doesn't update:**
- Check HF Space logs for build errors
- Verify Dockerfile.hf is valid
- Check if Space exists at correct path

**Push conflicts:**
- Workflow uses `--force` to override
- If issues persist, check HF Space git history

### Alternative: Manual Setup

If you prefer not to use GitHub Actions:

```bash
# Add HF remote manually
git remote add hf https://huggingface.co/spaces/YOUR-USERNAME/llm-quiz-solver

# Push manually when needed
git push hf main
```

### Your Space URL

Once deployed, your API will be accessible at:
```
https://YOUR-USERNAME-llm-quiz-solver.hf.space/receive_request
```

Use this URL in your Google Form submission!

### Next Steps

1. ✅ Create HF Space
2. ✅ Get HF token  
3. ✅ Add GitHub secrets
4. ✅ Configure HF Space secrets
5. ✅ Push to GitHub (triggers deployment)
6. ⏳ Wait for build (~10 min)
7. ✅ Test API endpoint
8. ✅ Submit Google Form

---

**Your automatic deployment is ready! Just push to main and it deploys.** 🚀
