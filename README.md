# VendorSetu AI

**Your Digital Business Assistant for Street Vendors & Micro-Entrepreneurs**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai%20Granite-1F70C1.svg)](https://www.ibm.com/products/watsonx-ai)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![AICTE PS#29](https://img.shields.io/badge/AICTE-Problem%20%2329-orange.svg)](#)

> **AICTE 2026 Problem Statement #29** — Street Vendor Digitalization Agent  
> Category: Agentic AI / RAG-based | Technology: IBM Cloud Lite + IBM Granite

---

## What is VendorSetu AI?

VendorSetu AI is a production-quality Agentic AI digital assistant that helps Indian street vendors, hawkers, and micro-entrepreneurs become digitally visible and access real opportunities.

It combines:
- **IBM watsonx.ai (Granite)** for natural language generation
- **RAG (Retrieval-Augmented Generation)** over verified government/MSME/digital documents
- **Multi-intent agentic routing** — one message, multiple relevant answers
- **Anti-hallucination enforcement** — only verified facts, confidence-aware language
- **Multilingual support** — Hindi, Hinglish, English

---

## Features

| Capability | Description |
|---|---|
| 🪪 **Business Profile Builder** | Generates tagline, description, keywords, WhatsApp greeting |
| 💳 **UPI / Digital Payment Guidance** | Step-by-step UPI setup, QR code, PM SVANidhi cashback |
| 📍 **Local SEO Assistant** | Google Business Profile content, hyperlocal keywords, action plan |
| 📣 **Marketing Generator** | WhatsApp/Instagram/SMS/flyer promotional content |
| 🏛️ **Govt / MSME Scheme Finder** | RAG-grounded PM SVANidhi, Mudra, Vishwakarma, e-Shram info |
| 📈 **Business Growth Advisor** | Hyperlocal growth path, digital presence stages, credit pathway |
| 🤝 **Customer Engagement** | Loyalty ideas, WhatsApp broadcasts, retention strategies |
| 💰 **Pricing Strategy Advisor** | Display tips, bundle pricing, trust-building (no live prices) |
| 🔍 **Digital Readiness Assessment** | 8-area scored assessment with personalised action plan |
| 🚀 **Digital Onboarding** | Personalised checklist + free-text Q&A for going digital |
| 💬 **AI Agent Chat** | Multi-intent free-text chat with RAG grounding and source display |

---

## Architecture

```
                    Vendor Message (Hindi/Hinglish/English)
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   Intent Classifier            │
                    │   (agent/classifier.py)        │
                    │   8 intents: PROFILE, PAYMENT, │
                    │   SEO, MARKETING, MSME_SCHEME, │
                    │   GROWTH, READINESS, GENERAL   │
                    └───────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │   (one branch per intent)      │
                    ▼                               ▼
        ┌─────────────────┐             ┌─────────────────┐
        │   RAG Retrieval  │             │  Direct Prompt   │
        │  (agent/rag.py) │             │  (marketing,     │
        │  TF-IDF over    │             │   profile)       │
        │  knowledge_base/│             └────────┬────────┘
        └────────┬────────┘                      │
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  IBM watsonx.ai         │
                    │  Granite (ibm/granite-  │
                    │  3-8b-instruct)         │
                    │  agent/watsonx_client   │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    Grounded, Anti-hallucination
                    Checked Response + Sources
```

### Key components

| File | Role |
|---|---|
| `app.py` | Streamlit UI — 11 tabs, hero banner, sidebar, readiness scorer |
| `agent/classifier.py` | 8-intent keyword classifier + digital readiness scorer |
| `agent/orchestrator.py` | Multi-intent agentic loop with RAG retrieval per intent |
| `agent/handlers.py` | Form-based tab handlers (all return `(answer, context, sources)`) |
| `agent/prompts.py` | All prompt templates with embedded anti-hallucination rules |
| `agent/rag.py` | TF-IDF RAG over `knowledge_base/*.md` (singleton, 49 chunks) |
| `agent/watsonx_client.py` | IBM Granite client with graceful offline fallback |
| `knowledge_base/` | 6 verified knowledge documents with metadata headers |

---

## Quick Start

### Prerequisites
- Python 3.9+
- IBM Cloud Lite account + watsonx.ai project (free tier)

### Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env.example .env
# Edit .env — add your WATSONX_API_KEY and WATSONX_PROJECT_ID

# 3. Run
streamlit run app.py
```

Open http://localhost:8501

> **No credentials yet?** The app runs in offline-fallback mode — every tab still works,
> showing what would be sent to IBM Granite. You can demo the full UI and RAG pipeline
> without live API access.

### Load the demo vendor

Click **"🎯 Load Demo Vendor"** in the sidebar to instantly populate with:
- Business: Sharma Fresh Fruits
- Location: Sector 14, Gurugram
- Products: Apple, Banana, Mango, Orange, Papaya

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WATSONX_API_KEY` | Yes | — | IBM Cloud API key |
| `WATSONX_PROJECT_ID` | Yes | — | watsonx.ai project ID |
| `WATSONX_URL` | No | `https://us-south.ml.cloud.ibm.com` | Region URL |
| `WATSONX_MODEL_ID` | No | `ibm/granite-3-8b-instruct` | Granite model ID |

Get credentials: https://cloud.ibm.com → watsonx.ai → your project → Manage

---

## Knowledge Base

The RAG knowledge base (`knowledge_base/`) contains 6 verified documents (49 chunks):

| File | Source | Topics |
|---|---|---|
| `govt_schemes.md` | PM SVANidhi portal, MoHUA | PM SVANidhi, Mudra, Vishwakarma, e-Shram |
| `upi_setup.md` | NPCI / RBI guidelines | UPI setup, QR codes, best practices |
| `local_seo.md` | Google Business Profile docs | Local SEO, WhatsApp Business, keywords |
| `digital_onboarding.md` | Meta / Google / eshram.gov.in | WhatsApp Business, Google Profile, e-Shram |
| `pricing_and_engagement.md` | General SME guidance | Pricing strategy, customer loyalty |
| `business_growth.md` | General SME guidance | Hyperlocal economy, growth stages, ONDC |

Each document includes a YAML frontmatter metadata header (title, source, organization, topic, URL).

To add knowledge: create a new `.md` file in `knowledge_base/` and restart the app.

---

## Anti-Hallucination Design

VendorSetu AI enforces grounding at multiple layers:

1. **System prompt rules**: Explicit prohibitions on inventing schemes, prices, statistics
2. **Per-prompt rules**: Each prompt template has domain-specific anti-hallucination instructions
3. **RAG grounding**: Factual answers always pass through retrieved context first
4. **Confidence language**: Responses use "According to...", "The available information indicates..."
5. **Source display**: UI shows which knowledge base files were retrieved for each answer
6. **Disclaimer reminders**: Government scheme and pricing tabs show verification warnings

Hallucination test response (e.g., made-up scheme):
> "I could not verify this from available trusted sources. Please check the official portal or contact your nearest ULB/bank/CSC."

---

## IBM Granite & watsonx.ai

- **Model**: `ibm/granite-3-8b-instruct` (configurable via `WATSONX_MODEL_ID`)
- **SDK**: `ibm-watsonx-ai>=1.1.2`
- **Parameters**: `decoding_method: greedy`, `max_new_tokens: 600`, `repetition_penalty: 1.05`
- **Lazy initialization**: Client loads only when first needed; never crashes if unconfigured
- **Offline fallback**: Returns clearly-labelled offline message showing system/user prompts

---

## Testing

See [`tests/test_agent.py`](tests/test_agent.py) for 14 evaluation scenarios covering:
intent detection, Hindi input, Hinglish input, hallucination resistance, grounded answers,
missing information handling, and end-to-end demo scenario.

Run tests:
```bash
python tests/test_agent.py
```

---

## Project Structure

```
street-vendor-agent/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── AGENTS.md                       # AI agent guidance
├── app.py                          # Streamlit UI entry point
├── agent/
│   ├── __init__.py
│   ├── classifier.py               # Intent classifier + readiness scorer
│   ├── orchestrator.py             # Agentic multi-intent loop
│   ├── handlers.py                 # Tab-specific handlers
│   ├── prompts.py                  # All prompt templates
│   ├── rag.py                      # TF-IDF RAG retriever
│   └── watsonx_client.py           # IBM Granite client
├── knowledge_base/
│   ├── govt_schemes.md
│   ├── upi_setup.md
│   ├── local_seo.md
│   ├── digital_onboarding.md
│   ├── pricing_and_engagement.md
│   └── business_growth.md
├── docs/
│   ├── architecture.md
│   └── demo-guide.md
├── tests/
│   └── test_agent.py
└── .streamlit/
    └── config.toml                 # Streamlit theme (orange brand palette)
```

---

## Limitations

- **No real-time data**: Mandi prices, live government scheme updates, and live business listings are not available.
- **TF-IDF retrieval**: Uses lexical matching, not semantic embeddings. Can be upgraded to watsonx.ai embeddings.
- **Offline fallback**: No IBM Granite connection shows prompts instead of live responses.
- **English-dominant KB**: Knowledge base is in English; responses in Hindi/Hinglish depend on model translation.
- **No persistence**: Vendor profiles and chat history exist only in the current browser session.

---

## Future Enhancements

- Swap TF-IDF for watsonx.ai embeddings API for semantic retrieval
- Add speech-to-text (IBM Speech to Text) for voice input
- SQLite/cloud persistence for vendor profiles across sessions
- WhatsApp Business API bot front-end
- ONDC integration for actual digital listing
- State-specific scheme knowledge bases

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Built With

- **IBM watsonx.ai** — Granite foundation model
- **IBM Cloud Lite** — Free tier credentials
- **Streamlit** — UI framework
- **scikit-learn** — TF-IDF RAG retrieval
- **python-dotenv** — Credential management
