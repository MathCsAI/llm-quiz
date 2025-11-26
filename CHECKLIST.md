# Project Completion Checklist

Use this checklist to ensure your project is ready for submission and evaluation.

## ✅ Code Implementation

- [x] FastAPI endpoint (`main.py`)
  - [x] POST `/receive_request` with JSON validation
  - [x] Secret verification (403 on failure)
  - [x] Invalid JSON handling (400 on failure)
  - [x] Background task processing
  - [x] Health check endpoint (`/`)

- [x] Quiz Solver (`quiz_solver.py`)
  - [x] LLM integration (AI Pipe)
  - [x] Script generation
  - [x] Script execution with subprocess
  - [x] Timeout management (3 minutes)
  - [x] Quiz chain processing
  - [x] Retry mechanism

- [x] Web Scraper (`scraper.py`)
  - [x] Playwright integration
  - [x] JavaScript rendering support
  - [x] Base64 decoding
  - [x] URL extraction
  - [x] File download link detection

- [x] Prompt Templates (`prompts.py`)
  - [x] System prompt (defense)
  - [x] User prompt (attack)
  - [x] Script generation prompt
  - [x] AI Pipe request formatting

## ✅ Configuration Files

- [x] `requirements.txt` - All dependencies listed
- [x] `.env.example` - Template for environment variables
- [x] `.gitignore` - Prevents committing secrets
- [x] `Dockerfile` - Container deployment
- [x] `docker-compose.yml` - ❌ (Optional, not created)
- [x] `render.yaml` - Render.com deployment
- [x] `Procfile` - Heroku deployment
- [x] `runtime.txt` - Python version specification

## ✅ Documentation

- [x] `README.md` - Comprehensive project documentation
- [x] `QUICKSTART.md` - 5-minute setup guide
- [x] `DEPLOYMENT.md` - Deployment instructions
- [x] `DESIGN.md` - Design decisions for viva
- [x] `LICENSE` - MIT License (required)

## ✅ Testing

- [x] `test_endpoint.py` - API endpoint tests
- [x] `test_components.py` - Component tests
- [x] `example_generated_script.py` - Example output

## ✅ Scripts

- [x] `setup.sh` - Automated setup
- [x] `start_server.sh` - Server startup
- [x] Scripts are executable (chmod +x)

## 📋 Pre-Submission Checklist

### Environment Setup

- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] `.env` file created from `.env.example`
- [ ] All environment variables configured:
  - [ ] `SECRET_KEY`
  - [ ] `EMAIL`
  - [ ] `AI_PIPE_TOKEN`

### Local Testing

- [ ] Server starts without errors (`./start_server.sh`)
- [ ] Health check works (`curl http://localhost:8000/`)
- [ ] Component tests pass (`python test_components.py`)
- [ ] Endpoint tests pass (`python test_endpoint.py`)
- [ ] Demo quiz request accepted
- [ ] Logs show quiz solving process

### Code Quality

- [ ] No syntax errors
- [ ] No hardcoded secrets
- [ ] Proper error handling
- [ ] Comprehensive logging
- [ ] Code is documented
- [ ] No TODO comments left

### Git Repository

- [ ] Code committed to git
- [ ] `.env` not committed (in .gitignore)
- [ ] Repository pushed to GitHub
- [ ] Repository is public (or will be before evaluation)
- [ ] MIT LICENSE file present
- [ ] README.md is complete and clear
- [ ] No sensitive data in commit history

### Deployment

- [ ] Deployed to chosen platform:
  - [ ] GitHub Codespaces
  - [ ] Render.com
  - [ ] Railway
  - [ ] Heroku
  - [ ] Other: _____________
  
- [ ] Deployment URL is accessible
- [ ] Deployment uses HTTPS (preferred)
- [ ] Environment variables configured on platform
- [ ] Health check endpoint responds
- [ ] Test request returns 200

### Google Form Submission

- [ ] Email address
- [ ] Secret string (matches deployment)
- [ ] System prompt (max 100 chars)
  - Strategy: ___________________________
  - [ ] Tested and working
  
- [ ] User prompt (max 100 chars)
  - Strategy: ___________________________
  - [ ] Tested and working
  
- [ ] API endpoint URL
  - Format: `https://your-domain.com/receive_request`
  - [ ] Verified accessible
  - [ ] HTTPS (preferred)
  
- [ ] GitHub repository URL
  - [ ] Public repository
  - [ ] Contains all required files
  - [ ] MIT LICENSE present

### Viva Preparation

- [ ] Read DESIGN.md thoroughly
- [ ] Understand all design decisions
- [ ] Can explain:
  - [ ] Why FastAPI over Flask
  - [ ] Why Playwright over BeautifulSoup
  - [ ] Why script generation approach
  - [ ] How timeout management works
  - [ ] How error handling works
  - [ ] How background tasks work
  
- [ ] Prepared examples:
  - [ ] How a quiz is processed
  - [ ] What happens on error
  - [ ] How LLM generates scripts
  
- [ ] Know the codebase:
  - [ ] main.py structure
  - [ ] quiz_solver.py flow
  - [ ] scraper.py functionality
  - [ ] prompts.py strategy

## 🧪 Manual Testing Checklist

### Test Cases to Run

1. **Health Check**
```bash
curl https://your-url.com/
```
Expected: 200 with status info

2. **Invalid JSON**
```bash
curl -X POST https://your-url.com/receive_request \
  -H "Content-Type: application/json" \
  -d 'not json'
```
Expected: 400 Bad Request

3. **Missing Fields**
```bash
curl -X POST https://your-url.com/receive_request \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com"}'
```
Expected: 400 Bad Request

4. **Invalid Secret**
```bash
curl -X POST https://your-url.com/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "wrong_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```
Expected: 403 Forbidden

5. **Valid Request**
```bash
curl -X POST https://your-url.com/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'
```
Expected: 200 with accepted status

### Logs to Check

- [ ] Request received log
- [ ] Secret validation log
- [ ] Background task started log
- [ ] Quiz content fetched log
- [ ] LLM called log
- [ ] Script generated log
- [ ] Script executed log
- [ ] Answer submitted log
- [ ] Result received log

## 📅 Timeline

- **Now**: Complete setup and local testing
- **Before Nov 29**: 
  - Deploy application
  - Submit Google Form
  - Ensure repository is public
- **Nov 29, 3:00 PM IST**: Quiz evaluation starts
- **TBD**: Viva session

## 🆘 Troubleshooting

### Common Issues

**Issue**: "AI_PIPE_TOKEN not set"
- **Fix**: Check `.env` file exists and has token

**Issue**: "Playwright browser not found"
- **Fix**: Run `playwright install chromium`

**Issue**: "403 Forbidden" on test
- **Fix**: Verify secret in `.env` matches test request

**Issue**: Server won't start
- **Fix**: Check port 8000 isn't already in use

**Issue**: Deployment fails
- **Fix**: Check platform logs, verify environment variables

## 📞 Support Resources

- **Project Requirements**: Course materials
- **AI Pipe Docs**: https://docs.aipipe.ai/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Playwright Docs**: https://playwright.dev/python/
- **GitHub Issues**: Your repository issues page

## ✅ Final Verification

Before submission, verify:

1. [ ] Code works locally
2. [ ] Code works on deployment
3. [ ] All tests pass
4. [ ] Documentation is complete
5. [ ] Repository is public
6. [ ] MIT LICENSE is present
7. [ ] Google Form is submitted
8. [ ] Prepared for viva

## 🎯 Success Criteria

Your project is ready when:

- ✅ Server responds to all test cases correctly
- ✅ Quiz solving works end-to-end
- ✅ Deployment is accessible via HTTPS
- ✅ Repository is complete and public
- ✅ Google Form is submitted
- ✅ You understand all design decisions

---

**Good luck with your submission and evaluation! 🚀**

**Remember**: The evaluation is on Nov 29, 2025 from 3:00-4:00 PM IST. Make sure everything is ready before then!
