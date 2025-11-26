# System Architecture Diagrams

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (Evaluator)                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ POST /receive_request
                 │ { email, secret, url }
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Server (main.py)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  1. Validate JSON (Pydantic)                              │  │
│  │  2. Verify Secret Key                                     │  │
│  │  3. Return 200 OK immediately                             │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ BackgroundTasks.add_task()
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              Background Task (quiz_solver.py)                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     Quiz Solver                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  1. Fetch Quiz (Playwright)                         │  │  │
│  │  │  2. Extract Content (BeautifulSoup)                 │  │  │
│  │  │  3. Generate Script (AI Pipe LLM)                   │  │  │
│  │  │  4. Execute Script (Subprocess)                     │  │  │
│  │  │  5. Submit Answer (HTTPX)                           │  │  │
│  │  │  6. Check for Next Quiz                             │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Request Flow Sequence

```
Client          FastAPI         Background      Scraper        LLM          Subprocess      Quiz Server
  │                │                │              │            │               │                │
  │─POST request──▶│                │              │            │               │                │
  │                │                │              │            │               │                │
  │                │─Validate JSON──▶              │            │               │                │
  │                │                │              │            │               │                │
  │                │─Check Secret───▶              │            │               │                │
  │                │                │              │            │               │                │
  │◀──200 OK──────│                │              │            │               │                │
  │                │                │              │            │               │                │
  │                │─Start BG Task──▶              │            │               │                │
  │                │                │              │            │               │                │
  │                │                │─Fetch Quiz──▶│            │               │                │
  │                │                │              │            │               │                │
  │                │                │◀─HTML + JS───│            │               │                │
  │                │                │              │            │               │                │
  │                │                │─Generate─────────────────▶│               │                │
  │                │                │  Prompt      │            │               │                │
  │                │                │              │            │               │                │
  │                │                │◀─Python──────────────────│               │                │
  │                │                │  Script      │            │               │                │
  │                │                │              │            │               │                │
  │                │                │─Execute──────────────────────────────────▶│                │
  │                │                │  Script      │            │               │                │
  │                │                │              │            │               │                │
  │                │                │              │            │               │─Submit Answer─▶│
  │                │                │              │            │               │                │
  │                │                │              │            │               │◀─Result + URL──│
  │                │                │              │            │               │                │
  │                │                │◀─Completed───────────────────────────────│                │
  │                │                │              │            │               │                │
  │                │                │─(Repeat if next URL)      │               │                │
  │                │                │              │            │               │                │
```

## 3. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FastAPI Endpoints                                       │   │
│  │  • POST /receive_request  (Quiz intake)                  │   │
│  │  • GET  /                 (Health check)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  QuizSolver (quiz_solver.py)                             │   │
│  │  • solve_quiz_chain()      - Main orchestrator           │   │
│  │  • call_llm()              - LLM interaction              │   │
│  │  • execute_script()        - Run generated code           │   │
│  │  • _check_time_limit()     - Time management              │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ├──────────────┬──────────────┬─────────────┐
                       ▼              ▼              ▼             ▼
┌────────────────────────┐ ┌────────────────┐ ┌───────────┐ ┌──────────┐
│   Data Access Layer    │ │  External APIs │ │ Execution │ │  Utils   │
│                        │ │                │ │  Engine   │ │          │
│ ┌────────────────────┐ │ │ ┌────────────┐ │ │ ┌───────┐ │ │ ┌──────┐ │
│ │ QuizScraper        │ │ │ │ AI Pipe    │ │ │ │Subproc│ │ │ │Prompt│ │
│ │ (scraper.py)       │ │ │ │ API        │ │ │ │Manager│ │ │ │Engine│ │
│ │                    │ │ │ │            │ │ │ │       │ │ │ │      │ │
│ │ • Playwright       │ │ │ │ • GPT-4o   │ │ │ │ • Run │ │ │ │Templates│
│ │ • BeautifulSoup    │ │ │ │ • Claude   │ │ │ │ • Kill│ │ │ │Format│ │
│ │ • Base64 decode    │ │ │ │ • Timeout  │ │ │ │ • Log │ │ │ │Params│ │
│ └────────────────────┘ │ │ └────────────┘ │ │ └───────┘ │ │ └──────┘ │
└────────────────────────┘ └────────────────┘ └───────────┘ └──────────┘
```

## 4. Data Flow Diagram

```
┌──────────┐
│  Quiz    │
│  URL     │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│   Playwright    │───┐
│   Fetch Page    │   │ JavaScript Rendering
└────┬────────────┘   │ Base64 Decoding
     │                │ Dynamic Content
     ▼                │
┌─────────────────┐◀──┘
│  HTML Content   │
│  + Scripts      │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ BeautifulSoup   │───┐
│   Parse HTML    │   │ Extract text
└────┬────────────┘   │ Find URLs
     │                │ Decode base64
     ▼                │
┌─────────────────┐◀──┘
│  Structured     │
│  Quiz Data      │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Prompt         │───┐
│  Generation     │   │ Include quiz content
└────┬────────────┘   │ Add requirements
     │                │ Specify format
     ▼                │
┌─────────────────┐◀──┘
│  LLM Prompt     │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│   AI Pipe       │───┐
│   LLM API       │   │ Model: gpt-4o-mini
└────┬────────────┘   │ Max tokens: 4000
     │                │ Temperature: 0.1
     ▼                │
┌─────────────────┐◀──┘
│  Python Script  │
│  (Generated)    │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Save to File   │
│  generated_     │
│  script.py      │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Subprocess     │───┐
│  Execute        │   │ Environment vars
└────┬────────────┘   │ Timeout: 150s
     │                │ Capture output
     ▼                │
┌─────────────────┐◀──┘
│  Script Output  │
│  + Answer       │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  POST Answer    │───┐
│  to Submit URL  │   │ JSON payload
└────┬────────────┘   │ Email + Secret
     │                │ URL + Answer
     ▼                │
┌─────────────────┐◀──┘
│  Quiz Result    │
│  + Next URL?    │
└─────────────────┘
```

## 5. Error Handling Flow

```
┌─────────────────┐
│  Try Operation  │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Success?       │─────YES─────▶ Continue
└────┬────────────┘
     │
     NO
     │
     ▼
┌─────────────────┐
│  Log Error      │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│  Retry Count    │
│  < MAX_RETRIES? │
└────┬────────────┘
     │
     ├──YES──▶ Increment Counter ──▶ Retry
     │
     NO
     │
     ▼
┌─────────────────┐
│  Return Failure │
└─────────────────┘
```

## 6. Time Management Flow

```
Start Time = Now
Time Limit = 3 minutes

Every Operation:
│
├─▶ Calculate Elapsed = Now - Start Time
│
├─▶ Calculate Remaining = Time Limit - Elapsed
│
├─▶ Remaining > 0?
│   │
│   ├──YES──▶ Continue
│   │
│   └──NO───▶ Stop & Return
│
└─▶ Log Time Remaining
```

## 7. Quiz Chain Processing

```
Initial URL
    │
    ▼
┌────────────────┐
│ Solve Quiz #1  │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│ Submit Answer  │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│ Response       │
│ correct: true  │
│ url: Quiz #2   │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│ Solve Quiz #2  │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│ Submit Answer  │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│ Response       │
│ correct: true  │
│ url: Quiz #3   │
└────┬───────────┘
     │
     ▼
    ...
     │
     ▼
┌────────────────┐
│ Response       │
│ correct: true  │
│ url: null      │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│    Complete    │
└────────────────┘
```

## 8. Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    GitHub Repository                      │
│  • Source Code                                           │
│  • Documentation                                         │
│  • Configuration Files                                   │
└──────────────────┬───────────────────────────────────────┘
                   │
                   │ git push
                   │
         ┌─────────┴──────────┬────────────┬──────────────┐
         │                    │            │              │
         ▼                    ▼            ▼              ▼
┌─────────────────┐ ┌─────────────┐ ┌──────────┐ ┌─────────────┐
│    Codespaces   │ │  Render.com │ │ Railway  │ │   Heroku    │
│                 │ │             │ │          │ │             │
│ • Dev Env       │ │ • Auto Deploy│ │• Easy    │ │• Classic    │
│ • Port Forward  │ │ • Free Tier │ │• Fast    │ │• Mature     │
│ • Public URL    │ │ • HTTPS     │ │• Modern  │ │• Addons     │
└─────────────────┘ └─────────────┘ └──────────┘ └─────────────┘
         │                    │            │              │
         │                    │            │              │
         └────────────────────┴────────────┴──────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   HTTPS Endpoint     │
                   │  /receive_request    │
                   └──────────────────────┘
```

## 9. Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Request Security                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  1. HTTPS Transport                                   │  │
│  │  2. JSON Schema Validation (Pydantic)                 │  │
│  │  3. Secret Key Verification                           │  │
│  │  4. Email Verification                                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Environment Security                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  • Secrets in .env file (not in code)                 │  │
│  │  • .env in .gitignore                                 │  │
│  │  • Environment variables in deployment platform       │  │
│  │  • No secrets in logs                                 │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 Execution Security                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  • Subprocess isolation                               │  │
│  │  • Execution timeout (150s)                           │  │
│  │  • No shell=True                                      │  │
│  │  • Controlled environment variables                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 10. Testing Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Test Pyramid                            │
│                                                              │
│                         ┌─────────┐                          │
│                         │  E2E    │  (Manual)                │
│                         │  Tests  │                          │
│                         └─────────┘                          │
│                      ┌──────────────┐                        │
│                      │  Integration │  (Partial)             │
│                      │    Tests     │                        │
│                      └──────────────┘                        │
│                 ┌──────────────────────┐                     │
│                 │   Component Tests    │  (test_components)  │
│                 │  • Environment       │                     │
│                 │  • Dependencies      │                     │
│                 │  • Playwright        │                     │
│                 │  • Scraper           │                     │
│                 │  • AI Pipe API       │                     │
│                 └──────────────────────┘                     │
│            ┌─────────────────────────────────┐               │
│            │      API Endpoint Tests         │  (test_endpoint)│
│            │  • Health check                 │               │
│            │  • Valid request (200)          │               │
│            │  • Invalid JSON (400)           │               │
│            │  • Missing fields (400)         │               │
│            │  • Invalid secret (403)         │               │
│            └─────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

These diagrams visualize the complete system architecture. Use them to:
- Understand the request flow
- Explain design decisions in viva
- Debug issues
- Plan improvements
