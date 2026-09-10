# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack

- **Python** / **Streamlit** UI (`app.py` is the sole entry point)
- **IBM watsonx.ai** (Granite model) via `ibm-watsonx-ai` SDK
- **RAG**: TF-IDF (`scikit-learn`) over `knowledge_base/*.md` — no embeddings API, no vector DB
- `.bob/`, `.vscode/`, `workspace_config.yaml`, and `venv/` are all `.gitignore`d — dev tooling only, not part of the application

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Run tests (no pytest — plain Python runner)
python tests/test_agent.py
```

## Required env vars (`.env`)

| Variable | Notes |
|---|---|
| `WATSONX_API_KEY` | IBM Cloud API key |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID |
| `WATSONX_URL` | Region URL, default `https://us-south.ml.cloud.ibm.com` |
| `WATSONX_MODEL_ID` | Default `ibm/granite-3-8b-instruct`, overridable |

Missing credentials do **not** crash the app — `watsonx_client.generate()` returns a labelled offline fallback string. Always check `is_configured()` before assuming live Granite output.

## Architecture

```
app.py  →  agent/orchestrator.py  (intent detection + multi-intent routing)
                │
                ├── agent/classifier.py   (8-intent keyword classifier + ReadinessReport scorer)
                ├── agent/rag.py          (TF-IDF retrieval over knowledge_base/*.md)
                ├── agent/prompts.py      (all prompt templates + BASE_SYSTEM_PROMPT)
                └── agent/watsonx_client.py  (lazy-init Granite client, graceful fallback)

agent/handlers.py   (form-tab helpers; wrap rag + prompts + generate for non-chat tabs)
```

## Critical non-obvious patterns

- **Intent classifier lives in `agent/classifier.py`**, not in `orchestrator.py`. `detect_intents()` returns a list of intent constants; `INTENT_*` constants and `INTENT_LABELS` dict are importable from there.
- **Intent routing is keyword-based** (`_KEYWORD_MAP` in `classifier.py`). Multi-intent messages generate one LLM call *per detected intent* and concatenate the answers. A message with no keyword match falls through to `GENERAL_VENDOR_HELP`.
- **`get_kb()` is a module-level singleton** (`agent/rag.py`). Adding/editing a `.md` file requires a process restart to take effect.
- **RAG chunks on `## ` headings**, then sub-chunks sections longer than 1800 chars on `### `. Chunk quality depends on consistent markdown heading structure in `knowledge_base/*.md`.
- **Language is injected at call time**, not in `BASE_SYSTEM_PROMPT`. Pattern: `system = prompts.BASE_SYSTEM_PROMPT + f"\nRespond in: {language}\n"`.
- **`handlers.*` functions return `(answer, context, sources)` — a 3-tuple.** `orchestrator.handle_message()` returns a dict `{intents, sections, context_used, sources, is_grounded}`. These are different shapes — don't mix them up in `app.py` tab code.
- **Streamlit theme** is fixed via `.streamlit/config.toml` (orange primary `#F97316`). Do not override inline.
- **Windows PowerShell** console is cp1252 — emoji chars crash `print()`. Run tests with `$env:PYTHONUTF8=1 python tests/test_agent.py` or use ASCII-only test output.

## Adding a new capability

1. Add keywords to `_KEYWORD_MAP` and a new `INTENT_*` constant in `agent/classifier.py`.
2. Add the intent to `ALL_INTENTS` and `INTENT_LABELS` in the same file.
3. Add a prompt builder function in `agent/prompts.py`.
4. Add the intent branch in `orchestrator.handle_message()` (and optionally a handler in `agent/handlers.py` for a dedicated tab).
5. Add a new `## ` section to the relevant `knowledge_base/*.md` (or a new file) and **restart the process** to reload the KB singleton.

## Code style (observed conventions)

- `from __future__ import annotations` at the top of every `agent/` module
- Relative imports within the `agent` package (`from . import prompts`, `from .rag import get_kb`)
- Module-level globals for lazy singletons (`_model`, `_kb_instance`) guarded with `if x is None`
- No type annotations on function parameters; return types omitted; docstrings on public functions only
- f-strings for all prompt construction (multi-line with explicit `\n` breaks)
- All `ibm_watsonx_ai` imports are inside try/lazy blocks in `watsonx_client.py` — never at module level elsewhere
