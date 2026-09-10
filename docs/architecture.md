# VendorSetu AI — Architecture

## System Overview

VendorSetu AI implements an Agentic AI + RAG pipeline for street vendor digitalization per AICTE PS#29.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                  │
│  11 tabs: Chat | Profile | SEO | UPI | Schemes |          │
│           Marketing | Engagement | Pricing | Growth |     │
│           Readiness | Onboarding                          │
│  Sidebar: Business context, language, demo loader         │
└─────────────────────────┬────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│               Agentic Orchestrator                        │
│               (agent/orchestrator.py)                     │
│                                                           │
│  1. Receive vendor message + business context             │
│  2. Classify intent(s) via classifier.py                  │
│  3. For each intent:                                      │
│     a. Retrieve from knowledge base (RAG)                 │
│     b. Build grounded prompt (prompts.py)                 │
│     c. Call IBM Granite (watsonx_client.py)               │
│     d. Collect answer + source metadata                   │
│  4. Return multi-section result with grounding info       │
└──────────┬───────────────────────┬───────────────────────┘
           │                       │
           ▼                       ▼
┌─────────────────┐     ┌──────────────────────────┐
│  Intent         │     │   RAG Retriever           │
│  Classifier     │     │   (agent/rag.py)          │
│  (classifier.py)│     │                          │
│                 │     │  - TF-IDF vectorizer      │
│  8 intents:     │     │  - Cosine similarity      │
│  DIGITAL_PAYMENT│     │  - 49 chunks from 6 docs  │
│  MSME_SCHEME    │     │  - Singleton (lazy init)  │
│  LOCAL_SEO      │     │  - Source metadata        │
│  MARKETING      │     └──────────┬───────────────┘
│  BUSINESS_PROFILE│               │
│  BUSINESS_GROWTH│                ▼
│  DIGITAL_        │    ┌──────────────────────────┐
│  READINESS       │    │   Knowledge Base          │
│  GENERAL_VENDOR_ │    │   knowledge_base/*.md     │
│  HELP            │    │                          │
└─────────────────┘     │  govt_schemes.md          │
                        │  upi_setup.md             │
                        │  local_seo.md             │
                        │  digital_onboarding.md    │
                        │  pricing_engagement.md    │
                        │  business_growth.md       │
                        └──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│               IBM Granite via watsonx.ai                  │
│               (agent/watsonx_client.py)                   │
│                                                           │
│  Model: ibm/granite-3-8b-instruct (default)               │
│  SDK: ibm-watsonx-ai                                     │
│  Params: greedy decoding, max_new_tokens=600             │
│  Fallback: returns offline message if unconfigured        │
└──────────────────────────────────────────────────────────┘
```

## Intent Classification

`agent/classifier.py` uses keyword-based intent detection with extensive Hindi/Hinglish/English
keyword lists per intent. 8 intent classes:

| Intent | Keywords include |
|---|---|
| `DIGITAL_PAYMENT` | upi, payment, qr, phonepe, paytm, gpay, online payment, paise |
| `MSME_SCHEME` | scheme, yojana, svanidhi, loan, government, mudra, vishwakarma |
| `LOCAL_SEO` | seo, google, search, online dikhna, maps, visible, google listing |
| `MARKETING` | promotion, promo, advertise, whatsapp message, flyer, poster |
| `BUSINESS_PROFILE` | profile, business profile, business card, describe my business |
| `BUSINESS_GROWTH` | grow, badhana, customer engagement, loyalty, hyperlocal, ondc |
| `DIGITAL_READINESS` | digital readiness, assessment, digital score, checklist |
| `GENERAL_VENDOR_HELP` | help, vendor, stall, sell, fruit, food, business |

Multi-intent: a message touching 2+ domains returns multiple intents; each gets independent
RAG retrieval and IBM Granite call.

## RAG Architecture

**Retriever**: `agent/rag.py`
- Chunks markdown files at `## ` headings, sub-chunks at `### ` for sections > 1800 chars
- Builds TF-IDF matrix at startup (singleton, loaded once)
- Query: transform query, compute cosine similarity, return top-k chunks above min_score=0.05
- Returns: `list[Chunk]` with `source`, `heading`, `text` fields
- 49 total chunks from 6 knowledge files

**Knowledge metadata**: Each `.md` file has YAML frontmatter:
```yaml
---
title: Document title
source: Original source name
organization: Issuing organization
topic: Topics covered
version: Date/version
url: Official URL
---
```

## Anti-Hallucination Layers

1. **System prompt** — 7 core rules, prohibits inventing schemes/prices/stats/actions
2. **Per-prompt rules** — domain-specific rules in each prompt function in `prompts.py`
3. **RAG grounding** — factual prompts receive retrieved context and are instructed to use only it
4. **Confidence language** — prompts require "According to...", "The available information..."
5. **UI warnings** — government scheme tab shows verification disclaimer
6. **Source display** — UI shows which KB files were retrieved for each response

## Digital Readiness Scoring

`assess_digital_readiness()` in `classifier.py`:
- 8 boolean inputs (UPI, Google Profile, WhatsApp Business, etc.)
- Score = (done / 8) × 100
- Levels: Beginner (0–25), Growing (26–62), Established (63–100)
- Returns `ReadinessReport` with score, level, per-area status, top priorities

## Data Flow for a Form Tab (e.g., Govt Schemes)

```
1. User submits question in tab_scheme
2. app.py calls handlers.scheme_lookup(question, language)
3. handlers.scheme_lookup calls _retrieve(question + " SVANidhi MSME...", top_k=4)
4. rag.get_kb() returns singleton KnowledgeBase
5. KB.retrieve() computes TF-IDF cosine similarity, returns top 4 chunks
6. handlers builds context string and source metadata list
7. prompts.scheme_guidance_prompt(question, context) builds grounded prompt
8. watsonx_client.generate(system, prompt) calls IBM Granite
9. Returns (answer, context, sources) → app.py displays answer + RAG expander
```

## Security Design

- No credentials in source code — environment variables only
- No user credentials collected (UPI PIN, OTP, bank passwords, Aadhaar)
- System prompt rule: "Never ask for or accept passwords, OTPs, UPI PINs..."
- UPI tab displays explicit security reminder banner
- `.env` in `.gitignore`, only `.env.example` committed

## Extension Points

- **New KB document**: Add `.md` to `knowledge_base/` → restart app
- **New intent**: Add keywords to `_KEYWORD_MAP` in `classifier.py` → add branch in `orchestrator.py` → add prompt in `prompts.py` → add handler in `handlers.py` → add tab in `app.py`
- **Semantic retrieval**: Replace `TfidfVectorizer` in `rag.py` with watsonx.ai embeddings
- **New model**: Change `WATSONX_MODEL_ID` in `.env`
