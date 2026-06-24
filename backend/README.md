# SafeGen Backend

FastAPI service responsible for:

- local sanitization via Ollama + `phi3:mini`;
- external semantic analysis via Gemini;
- exposing the HTTP endpoints for the hybrid flow.

Recommended execution path: run it through the Docker stack at the repository root.

## Evaluators

The evaluator entrypoint is split into:

- `python avaliar_analisadores.py semantic_analysis`
- `python avaliar_analisadores.py local_analysis`

The `semantic_analysis` evaluator uses `prompts_analise_semantica_gemini.json`, sends each item's `prompt` directly to Gemini, and compares the returned `security_risk` against the reference value.

Gemini requests rotate between `GEMINI_API_KEY1` and `GEMINI_API_KEY6`, enforcing `5 RPM` and `20 RPD` per key in code, with automatic retries for transient failures such as `503`.

The `local_analysis` evaluator uses `prompts_analise_local_phi3.json`, sends each item's `prompt` to the local Phi-3/Ollama sanitizer, and compares the returned `sensitive_data` against the reference value.
