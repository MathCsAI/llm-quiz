# Testing Guide for LLM Quiz Solver

## Test Suite Overview

This project includes comprehensive test cases to verify both local functionality and Hugging Face deployment.

## Test Files

1. **`test_cases.py`** - Main test suite with 9 comprehensive tests
2. **`check_hf_deployment.py`** - Helper to check HF Space status
3. **`test_local.py`** - Quick local validation tests

## Running Tests

### 1. Local Tests Only

Test local functionality without HF deployment:

```bash
python3 test_cases.py --local-only
```

**Tests:**
- ✅ Module imports
- ✅ Configuration validation
- ✅ Prompt length constraints (≤100 chars)
- ✅ QuizSolver initialization

### 2. Check HF Deployment Status

Before running full tests, check if your HF Space is online:

```bash
# Option 1: Using HF username
python3 check_hf_deployment.py --username YOUR_HF_USERNAME

# Option 2: Using direct URL
python3 check_hf_deployment.py --url https://username-llm-quiz-solver.hf.space
```

### 3. Full Test Suite (Local + HF)

Run all tests including HF deployment:

```bash
python3 test_cases.py --hf-endpoint https://YOUR_USERNAME-llm-quiz-solver.hf.space
```

**HF Tests:**
- ✅ Health check (endpoint accessibility)
- ✅ Valid request validation
- ✅ Invalid secret rejection (403)
- ✅ Missing fields validation (422)
- ✅ Demo quiz processing

## Expected Results

### All Tests Passing ✅
```
======================================================================
                    TEST SUMMARY
======================================================================

✅ Passed: 9/9
❌ Failed: 0/9

======================================================================
🎉 ALL TESTS PASSED!
======================================================================
```

## Test Case Details

### Local Tests

| Test | Purpose | Expected |
|------|---------|----------|
| Module Imports | Verify all modules load | All imports successful |
| Configuration | Check model settings | gpt-4.1-nano configured |
| Prompt Constraints | Validate prompt lengths | Defense ≤100, Attack ≤100 |
| QuizSolver Init | Test class initialization | Creates solver instance |

### HF Deployment Tests

| Test | Purpose | Expected |
|------|---------|----------|
| Health Check | Verify Space is online | Status 200 |
| Endpoint Validation | Test valid requests | Status 200 |
| Invalid Secret | Test rejection | Status 403 |
| Missing Fields | Test validation | Status 422 |
| Demo Quiz | Test real quiz processing | Status 200 |

## Troubleshooting

### HF Space Returns 503
**Issue:** Space is still building  
**Solution:** Wait 5-10 minutes and try again

### Connection Timeout
**Issue:** Space URL incorrect or not accessible  
**Solution:** Verify URL at https://huggingface.co/spaces/USERNAME/SPACE

### 403 Forbidden (on valid request)
**Issue:** Secrets not configured in HF Space  
**Solution:** Add secrets in Space Settings → Repository secrets:
- `EMAIL`: 23f2003858@ds.study.iitm.ac.in
- `SECRET_KEY`: 12356789
- `AI_PIPE_TOKEN`: Your AI Pipe token

### Tests Fail Locally
**Issue:** Dependencies not installed  
**Solution:** `pip install -r requirements.txt`

## Manual Testing

You can also test the API manually with curl:

```bash
# Health check
curl https://USERNAME-llm-quiz-solver.hf.space/

# Test endpoint (valid request)
curl -X POST https://USERNAME-llm-quiz-solver.hf.space/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "23f2003858@ds.study.iitm.ac.in",
    "secret": "12356789",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'

# Test endpoint (invalid secret - should return 403)
curl -X POST https://USERNAME-llm-quiz-solver.hf.space/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "23f2003858@ds.study.iitm.ac.in",
    "secret": "wrong_secret",
    "url": "https://example.com"
  }'
```

## CI/CD Integration

The GitHub Actions workflow automatically deploys to HF Spaces on push to main:

1. Push code → Triggers workflow
2. Workflow pushes to HF Space
3. HF rebuilds Space (~5-10 min)
4. Run tests to verify deployment

## Submission Checklist

Before submitting:

- [ ] All local tests pass: `python3 test_cases.py --local-only`
- [ ] HF Space is online: Check at HF dashboard
- [ ] Secrets configured in HF Space
- [ ] Full tests pass: `python3 test_cases.py --hf-endpoint <URL>`
- [ ] Manual curl test works
- [ ] Submit HF Space URL to Google Form

## Support

If tests fail, check:
1. GitHub Actions logs: https://github.com/MathCsAI/llm-quiz/actions
2. HF Space logs: Space Settings → Logs
3. Dockerfile builds without errors
4. All secrets properly set in HF Space
