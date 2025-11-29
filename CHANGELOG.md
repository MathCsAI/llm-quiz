# Changelog

All notable changes to this project are documented here.

## v1.0-final (2025-11-29)
### Added
- `SUBMISSION.md` providing endpoint, prompts, models, test evidence, security notes.
- Script sanitizer enhancements: auto-fix missing colons, unclosed parentheses, stray identifiers, empty blocks with `pass`, logging of applied fixes.
- Email/secret log redaction (emails masked, secrets never logged).
- Attack prompt tuned (87 chars) for multi-step extraction scenario.
- Comprehensive submission & verification section in README.
- Release tag `v1.0-final` pushed to repository.

### Changed
- README: Updated attack prompt; added security bullet list; added production submission instructions.
- Prompts: Replaced original attack prompt with tuned variant.
- Application: Logging improvements; sanitizer logging; redaction applied in `app.py` and `quiz_solver.py`.

### Removed / Cleaned
- Legacy stress/demo test scripts (`test_api_live.py`, `test_big_quiz_stress.py`, `test_multiple_quizzes.py`).
- Redundant trigger file `TRIGGER.md`.
- Stale OpenAI/AI Pipe references replaced with Gemini REST usage.

### Security & Compliance
- Secrets kept only in `.env` (non-tracked) and HF Space secrets.
- No hardcoded API keys in tracked files.
- Logs avoid exposing full email or secret.

### Testing
- Local test suite: 4/4 passing.
- HF comprehensive suite: 10/10 passing (concurrency, validation, performance < 1.2s; recent run ~0.78s).
- Prompt constraints: Defense 100 chars; Attack 87 chars.

### Operational Notes
- Fallback model chain: `gemini-2.5-pro`, `gemini-3-pro-preview`, `gemini-2.0-flash-lite`, `gemini-2.0-flash`, `gemini-2.5-flash-lite`.
- Deterministic fallback for origin-based quiz patterns if LLM unreachable.

### Next Potential Improvements (Not Implemented)
- Enhanced per-fix sanitizer audit logging (line-level before/after snapshots).
- Additional rate limiting or request queue.
- Release automation via GitHub Actions (draft release on tag push).
- More aggressive attack prompt experimentation (semantic variants within 100 chars).

---
