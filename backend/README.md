# SafeGen Backend

FastAPI service responsible for:

- local sanitization via Ollama + `phi3:mini`;
- external semantic analysis via Gemini;
- exposing the HTTP endpoints for the hybrid flow.

Recommended execution path: run it through the Docker stack at the repository root.
