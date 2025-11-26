# Copilot Instructions for llm-quiz

Purpose: Help AI coding agents work productively in this repo by codifying the architecture, workflows, and project-specific conventions.

## Big Picture
- API-first service using FastAPI (`main.py`). Two endpoints: `GET /` (health) and `POST /receive_request` (accepts quiz job, returns 200 immediately). An alias `POST /webhook` maps to the same handler.
- Background processing via FastAPI `BackgroundTasks` calls `solve_quiz_task` in `quiz_solver.py` (never block the request handler).
- Orchestrator `QuizSolver` performs a sequential chain: scrape quiz → generate Python script via AI Pipe → save to `generated_script.py` → execute in a subprocess (timeout 150s) → submit answer → optionally follow next quiz URL. Overall time budget: 3 minutes.
- Scraping with Playwright + BeautifulSoup in `scraper.py`. Handles JS-rendered pages and decodes base64 payloads (look for atob()).
- LLM integration via AI Pipe chat completions (`prompts.get_aipipe_request`). Default model is `gpt-4o-mini`; max_tokens ≈ 4000; temperature 0.1.

## Core Files & Responsibilities
- `main.py`: request validation (Pydantic), secret/email checks, immediate 200, enqueue background task.
- `quiz_solver.py`:
  - `QuizSolver.solve_quiz_chain(url)`: sequentially solves up to 10 quizzes; enforces 3-minute limit.
  - `QuizSolver.generate_and_execute_script(...)`: builds prompt from scraped content and calls AI Pipe; writes `generated_script.py`; executes with `asyncio.create_subprocess_exec` (no `shell=True`). Retries up to `MAX_RETRIES=2`.
  - `QuizSolver.execute_script(path)`: sets env vars `AI_PIPE_TOKEN`, `EMAIL`, `SECRET` for the script; captures stdout/stderr; enforces `SCRIPT_TIMEOUT=150` seconds.
  - Detects next quiz via regex on stdout: looks for JSON like `"url": "https://..."`.
- `scraper.py`:
  - `QuizScraper.fetch_quiz_content(url)`: waits for JS, extracts `text`, `html`, `scripts`, `download_links`, `submit_url`, and decoded `base64_content`.
  - `fetch_quiz_sync(url)`: convenience sync wrapper (used by orchestrator).
- `prompts.py`: prompt templates. Script generation prompt requires the LLM to emit ONLY a complete Python script, using env vars and posting to submit URL.
- `example_generated_script.py`: example of what the LLM should output.

## Project Conventions (do this, not that)
- Immediate 200: Keep `POST /receive_request` fast; push heavy work to `BackgroundTasks.add_task(...)` with `solve_quiz_task(email, secret, url)`.
- Secrets & identity come from env: `.env` holds `SECRET_KEY`, `EMAIL`, `AI_PIPE_TOKEN`. Do not hardcode or log secrets.
- Generated scripts must:
  - Use env vars `EMAIL`, `SECRET`, `AI_PIPE_TOKEN` (exact names).
  - Use `httpx.post(submit_url, json=payload)` where payload includes `email`, `secret`, `url`, and computed `answer`.
  - Print the API response JSON; include next `url` if present.
- Execution safety: run scripts via `asyncio.create_subprocess_exec(sys.executable, script)` with a timeout; never use `shell=True`.
- Time limits: respect 3-minute overall window (`QuizSolver._check_time_limit`) and `SCRIPT_TIMEOUT=150` seconds.
- Model choice: default to `gpt-4o-mini`; swap to heavier models only when necessary and via `call_llm(..., model=...)`.

## Developer Workflows
- Setup
  - `./setup.sh` (creates venv, installs deps, installs Playwright Chromium, creates `.env` from `.env.example`).
- Run locally
  - `./start_server.sh` (uses `uvicorn main:app --reload` on port 8000). Requires `.env`.
- Quick checks
  - Health: `curl http://localhost:8000/`
  - Submit demo: `curl -X POST http://localhost:8000/receive_request -H 'Content-Type: application/json' -d '{"email":"<EMAIL>","secret":"<SECRET_KEY>","url":"https://tds-llm-analysis.s-anand.net/demo"}'`
- Tests
  - Components: `python test_components.py`
  - Endpoints: `python test_endpoint.py`
- Deployment
  - Render: `render.yaml` (uses `uvicorn main:app --port $PORT`; installs Playwright deps)
  - Heroku: `Procfile` + `runtime.txt`
  - HF Spaces: `Dockerfile.hf` + `app.py` (port 7860)

## Patterns to Reuse
- Prompting: use `prompts.get_script_generation_prompt(...)` and `prompts.get_aipipe_request(...)` to keep request shape consistent with AI Pipe.
- Scraper outputs: include decoded base64 segments (`base64_content[].decoded`) and `submit_url` when assembling the script-generation prompt to improve accuracy.
- Next-URL chaining: keep emitting/printing the API response JSON from the generated script so `QuizSolver` can regex-match `"url": "..."`.

## Extending the System (examples)
- Add another endpoint: implement in `main.py` with Pydantic validation and delegate long work via `BackgroundTasks`.
- Add a new tool or provider: wrap calls in an async function like `call_llm`, keep timeouts ≤ 60s, and preserve the “generate-only-code” requirement in prompts.
- Enhance scraping: extend `_extract_submit_url` or `_extract_download_links` in `scraper.py` (keep regexes conservative and avoid blocking operations).

## Gotchas
- Playwright must have Chromium installed (`playwright install chromium`); CI/containers use `playwright install-deps chromium`.
- Ensure `.env` exists before starting; `start_server.sh` will exit otherwise.
- Do not return the generated answer from the HTTP handler; all solving happens after 200 response.
- Keep outputs small enough for AI Pipe limits; `max_tokens` is set to 4000.

Questions or unclear areas? Tell us what’s missing or ambiguous (e.g., script output parsing, prompt boundaries, or deployment nuances), and I’ll refine these instructions.
