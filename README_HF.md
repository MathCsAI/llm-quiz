---
title: LLM Quiz Solver
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# LLM Quiz Solver

An intelligent application that automatically solves data analysis quizzes using Large Language Models.

## Features

- FastAPI endpoint for receiving quiz tasks
- LLM-powered script generation
- Web scraping with Playwright
- Background task processing
- 3-minute timeout management

## API Usage

### Health Check
```bash
curl https://YOUR-SPACE-NAME.hf.space/
```

### Submit Quiz
```bash
curl -X POST https://YOUR-SPACE-NAME.hf.space/receive_request \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your_email@example.com",
    "secret": "your_secret",
    "url": "https://quiz-url.com"
  }'
```

## Configuration

Set these secrets in your Space settings:
- `SECRET_KEY`: Your authentication secret
- `EMAIL`: Your email address
- `AI_PIPE_TOKEN`: Your AI Pipe API token

## Links

- [GitHub Repository](https://github.com/MathCsAI/llm-quiz)
- [Documentation](https://github.com/MathCsAI/llm-quiz/blob/main/README.md)
