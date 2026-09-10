# VendorSetu AI — Demo Guide

## Demo Setup (5 minutes)

### Step 1: Load demo vendor
Click **"🎯 Load Demo Vendor"** in the sidebar. This populates:
- **Business**: Sharma Fresh Fruits
- **Type**: Fruits & Vegetables
- **Location**: Sector 14, Gurugram
- **Products**: Fresh seasonal fruits — Apple, Banana, Mango, Orange, Papaya
- **Language**: Hinglish

### Step 2: Check connection status
- **Green "IBM Granite Connected"** = live AI responses
- **Orange "Offline Mode"** = fallback mode (still demos all features)

---

## Demo Walkthrough (8 minutes)

### Scene 1: Multi-intent Agentic Chat (2 min)
Go to **💬 AI Agent Chat** tab.

Type:
> "Main Sector 14 Gurugram mein fresh fruits bechta hoon. Mujhe UPI setup karna hai aur online bhi dikhna hai."

**Point out to judges:**
- The 🎯 intent badges shown (DIGITAL_PAYMENT + LOCAL_SEO detected simultaneously)
- Both answers appear as separate sections
- The "📚 Retrieved knowledge-base context (RAG)" expander showing which documents were used
- The grounding indicator confirming this is not a hallucinated response

### Scene 2: Business Profile (1 min)
Go to **🪪 Business Profile** tab.

Click **"🪪 Generate Business Profile"**.

**Point out:**
- Tagline, description, keywords, WhatsApp greeting all generated
- No facts invented — everything based on sidebar input
- "📋 Copy as plain text" for easy copy-paste

### Scene 3: Government Schemes — RAG Demo (2 min)
Go to **🏛️ Govt Schemes** tab.

Ask:
> "PM SVANidhi kya hai aur mujhe kaise apply karna chahiye?"

**Point out:**
- The disclaimer banner (scheme details change — always verify officially)
- The "📚 Knowledge Base Sources (RAG)" expander showing `govt_schemes.md` source
- Loan amounts are stated as per retrieved document, not invented
- Answer ends with official portal reference

Now try a fake scheme:
> "VendorBharat Gold Scheme 2025 ke baare mein batao"

**Point out:** The agent does NOT confirm a fake scheme. This demonstrates anti-hallucination.

### Scene 4: Digital Readiness Assessment (1 min)
Go to **🔍 Readiness** tab.

Uncheck all boxes → Score shows 0/100, Beginner.

Click **"🔍 Generate Full Readiness Report"**.

**Point out:**
- Scored assessment across 8 digital areas
- Personalised action plan
- Encouraging, non-condescending tone

### Scene 5: Marketing Generator (1 min)
Go to **📣 Marketing** tab.

Type in: "Fresh mangoes arrived — special Diwali price"
Platform: WhatsApp, Tone: Festive / celebratory

Click **"📣 Generate Promotional Content"**.

**Point out:** Ready-to-send message in Hinglish, copy-paste ready.

### Scene 6: Digital Onboarding (1 min)
Go to **🚀 Onboarding** tab.

Click **"📋 Generate My Checklist"**.

**Point out:** Personalised numbered checklist with ⬜ checkboxes, official links, time estimate.

---

## Key Talking Points for Judges

### "How is this Agentic AI?"
The orchestrator (`agent/orchestrator.py`) automatically:
1. Classifies intent from free text (8 intent types)
2. Handles multi-intent messages (one message → multiple answers)
3. Decides when to retrieve from knowledge base vs. use direct prompting
4. Chains: Intent detection → RAG retrieval → Prompt construction → IBM Granite → Response

It's not a single prompt → single answer system. It routes, retrieves, and orchestrates.

### "How is RAG used?"
- `knowledge_base/` contains 6 verified documents (49 chunks)
- TF-IDF cosine similarity retrieves relevant chunks per query
- Retrieved context is injected into every factual prompt
- UI shows exactly which documents were retrieved (transparent RAG)
- The agent is instructed to ONLY use retrieved facts for schemes, UPI, and prices

### "How is IBM Granite used?"
- `ibm-watsonx-ai` SDK calls `ibm/granite-3-8b-instruct`
- All 11 capabilities route through IBM Granite for generation
- System prompt + user prompt pattern with Granite's chat format
- Configurable model ID via `WATSONX_MODEL_ID` environment variable

### "How do you prevent hallucination?"
5 layers: system prompt rules → per-prompt domain rules → RAG grounding → confidence language → UI disclaimers. Demo the fake scheme query to show it live.

### "What about local languages?"
Language is injected at call time: `Respond in: Hinglish`. The model matches the vendor's language register. Test with pure Hindi: "मुझे UPI सेटअप करना है" — the response comes back in Hindi.

---

## Common Demo Questions

**Q: Can the agent actually set up UPI for me?**
A: No — it guides the vendor through the steps. It cannot and does not create accounts, transfer money, or perform any action on the vendor's behalf. This is by design per the anti-hallucination rules.

**Q: Is the scheme information accurate?**
A: It's sourced from the PM SVANidhi official portal and Ministry documents, embedded in the knowledge base. The agent retrieves it and cites it, but always directs vendors to verify current details at the official portal since scheme parameters can change.

**Q: What happens with no internet/API key?**
A: The app runs in offline-fallback mode. Every tab still renders, every button works, the RAG retrieval still runs — only the IBM Granite generation step shows a labelled offline placeholder showing what would be sent.
