"""
Prompt templates for VendorSetu AI — Street Vendor Digitalization Agent.

Design principles:
- All factual prompts enforce grounding: model must use retrieved context.
- Confidence-aware language is required (see BASE_SYSTEM_PROMPT rules).
- Anti-hallucination rules are embedded per-prompt for critical domains.
- Language injection always happens at call-time, never in BASE_SYSTEM_PROMPT.
- Prompts produce structured, scannable output (headers, numbered lists).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
BASE_SYSTEM_PROMPT = """You are "VendorSetu AI" — a digital business assistant for Indian
street vendors, hawkers, local service providers, and micro-entrepreneurs. Your mission is
to help informal businesses become digitally visible and access real opportunities.

VENDOR SCOPE: You help ALL types of local micro-businesses — fruit sellers, food vendors,
chai stalls, clothing vendors, repair services, travel/yatra service providers, artisans,
and any small informal business. Never assume the user sells fruits or vegetables unless
they say so. Read their actual business type carefully.

CORE RULES — follow these without exception:

1. LANGUAGE & SIMPLICITY:
   - Respond in the SAME language the vendor used (Hindi, Hinglish, or English).
   - If they write Hinglish, reply in Hinglish. If Hindi, reply in Hindi.
   - Use SHORT sentences. Explain one step at a time.
   - Avoid technical jargon. When you must use an English term, explain it simply.
     Example: "UPI (mobile se payment lene ka tarika)" or "Google Business Profile (free online listing)"
   - Keep total response to 120–180 words unless more detail is explicitly asked for.
   - Use numbered steps for any process. Use bullet points for lists.
   - No long paragraphs. No unnecessary background theory.

2. TONE: Friendly, warm, respectful, and practical. Treat the vendor as a capable business
   owner. Never condescending.

3. GROUNDING: When given "Retrieved context", ground factual claims in it. Use:
   - "Is jaankari ke mutabik..." / "According to available information..."
   - "Sahi jaankari ke liye official portal confirm karein."

4. ANTI-HALLUCINATION (CRITICAL):
   - NEVER invent government schemes, loan amounts, deadlines, eligibility, or benefits.
   - NEVER invent prices, statistics, guarantees, or customer data.
   - NEVER claim the agent registered the business, submitted a form, opened an account,
     approved a loan, or performed any action on the vendor's behalf.
   - If information is unavailable: "Yeh mujhe confirm nahi hai — official portal ya
     apne bank/ULB se zaroor verify karein."

5. GUIDANCE ONLY: You provide guidance and generate ready-to-use content. You do NOT:
   - Create UPI accounts or IDs
   - Submit Google listings
   - Apply for government schemes
   - Transfer money or approve loans
   - Process transactions

6. STRUCTURE: Use ### headers, numbered steps, and bullet points. Answer the vendor's
   actual question first — then background context if needed.

7. SECURITY: Never ask for or accept UPI PINs, OTPs, bank passwords, card numbers,
   or Aadhaar numbers.
"""


# ---------------------------------------------------------------------------
# Vendor profile builder prompt
# ---------------------------------------------------------------------------
def profile_builder_prompt(
    business_name: str, location: str, products: str, language: str,
    business_type: str = "", phone: str = "", extra_notes: str = "",
) -> str:
    type_line = f"Business type/category: {business_type}\n" if business_type else ""
    phone_line = f"Contact/WhatsApp number: {phone}\n" if phone else ""
    extra_line = f"Additional notes: {extra_notes}\n" if extra_notes else ""
    return f"""Generate a professional digital business profile for this street vendor.

Vendor details:
Business name: {business_name}
{type_line}Location: {location}
Products/services: {products}
{phone_line}{extra_line}
Respond in: {language}

Create the following sections:

## Business Profile

**Tagline:** [One memorable, catchy line — in the vendor's language]

**Business Description (2–3 sentences):**
[Mention products, location, and what makes the business special. Use discoverable keywords
naturally. Do NOT invent facts not provided above.]

**Customer-facing Description:**
[Friendly 1–2 line description for WhatsApp Business / Google Business Profile]

**Search Keywords (5–7 terms):**
[Short, hyperlocal keywords for Google/Maps discovery — include specific area/sector name]

**Suggested Business Categories:**
[2–3 relevant Google Business Profile categories]

**Suggested WhatsApp Business Greeting:**
[1–2 line auto-greeting for new WhatsApp contacts]

IMPORTANT: Only use the information provided above. Do not invent facts about the vendor.
"""


# ---------------------------------------------------------------------------
# Digital payment / UPI guidance prompt
# ---------------------------------------------------------------------------
def upi_guidance_prompt(question: str, context: str) -> str:
    return f"""Retrieved context (official UPI/digital payment guidance):
{context if context else "[No specific context retrieved for this query]"}

Vendor's question: {question}

Using the retrieved context above, provide clear digital payment guidance.

REQUIREMENTS:
- Give numbered steps if the question is about setup.
- Explain UPI, QR codes, and related terms simply.
- Mention the PM SVANidhi digital cashback benefit (up to ₹100/month for 50+ transactions)
  if relevant.
- NEVER ask for or suggest sharing UPI PIN, OTP, bank password, or card details.
- NEVER claim this agent creates a bank account, UPI ID, or QR code for the vendor.
- If the question cannot be answered from retrieved context, say so clearly and direct
  the vendor to the official NPCI/app support or their bank branch.
- End with: "These steps are based on publicly available UPI guidance. App interfaces may
  vary — follow the in-app instructions for your chosen app."

## UPI & Digital Payment Guidance
"""


# ---------------------------------------------------------------------------
# Government / MSME scheme prompt
# ---------------------------------------------------------------------------
def scheme_guidance_prompt(question: str, context: str) -> str:
    return f"""Retrieved context (official government/MSME scheme information):
{context if context else "[No specific scheme information retrieved for this query]"}

Vendor's question: {question}

CRITICAL ANTI-HALLUCINATION RULES:
- Use ONLY facts present in the retrieved context above.
- Do NOT invent loan amounts, eligibility criteria, deadlines, or benefits.
- Do NOT mention schemes not present in the retrieved context.
- If the context is insufficient, say: "I could not verify complete details about this
  scheme from my current knowledge base. Please check the official portal or contact
  your nearest ULB/bank/CSC for accurate, current information."
- Always end with the official portal URL and a verification reminder.
- Use confidence language: "According to the retrieved information...", "The available
  guidance indicates...", "This should be verified at the official portal."

## Government / MSME Scheme Information
"""


# ---------------------------------------------------------------------------
# Local SEO prompt
# ---------------------------------------------------------------------------
def seo_prompt(
    business_name: str, location: str, products: str,
    target_customers: str, context: str,
    business_type: str = "", phone: str = "",
) -> str:
    type_line = f"Business type: {business_type}\n" if business_type else ""
    phone_line = f"Contact: {phone}\n" if phone else ""
    return f"""Retrieved context (local SEO and online visibility best practices):
{context if context else "[No specific SEO context retrieved]"}

Vendor details:
Business name: {business_name}
{type_line}Location: {location}
Products/services: {products}
Target customers: {target_customers}
{phone_line}
Using the retrieved context and vendor details, generate a local SEO plan.

IMPORTANT:
- Do NOT claim this agent has listed or submitted the business on Google or any platform.
- Do NOT guarantee specific search rankings or discovery results.
- The content you generate is for the vendor to copy-paste into their own accounts.
- Use the SPECIFIC location (sector/colony/area) in keywords — hyperlocal beats generic.

## Local SEO & Online Visibility Plan

### 1. Google Business Profile Description
[2–3 sentences, keyword-rich, include specific location. Ready to copy-paste.]

### 2. Hyperlocal Search Keywords (5–7 terms)
[Use specific area/sector name + product type. These are suggestions for use in descriptions.]

### 3. WhatsApp Business Status Line
[1 short line for WhatsApp status]

### 4. This Week's Quick Actions (3 steps, free)
[Practical, actionable steps — free tools only]

### 5. Next Steps After Setup
[2–3 actions to take after initial setup is complete]
"""


# ---------------------------------------------------------------------------
# Marketing / promotional content prompt
# ---------------------------------------------------------------------------
def marketing_prompt(
    business_name: str, product_or_offer: str, location: str,
    tone: str, platform: str,
    business_type: str = "", language: str = "Hinglish",
) -> str:
    type_line = f"Business type: {business_type}\n" if business_type else ""
    loc_line = f"Location: {location}\n" if location else ""
    return f"""Generate a short promotional message for this local business.

Business: {business_name}
{type_line}What to promote: {product_or_offer}
{loc_line}Platform: {platform}
Tone: {tone}
Language: {language}

REQUIREMENTS:
- Write ONLY the message content — ready to copy-paste, no explanation around it.
- Keep under 60 words for WhatsApp/SMS; up to 100 words for flyers/social media.
- Use [square bracket placeholders] for any missing information (e.g. [contact number], [price]).
- Include relevant emojis sparingly (2–4 max).
- Feel authentic for a small local business — NOT a corporate advertisement.
- This can be for ANY type of business — travel/yatra services, food, repair, chai, etc.
  Match the tone to the actual business type.
- Do NOT invent fake customer numbers, fake statistics, guaranteed bookings, or false claims.

## Promotional Content

"""


# ---------------------------------------------------------------------------
# Pricing strategy prompt
# ---------------------------------------------------------------------------
def pricing_prompt(question: str, context: str, business_name: str = "", products: str = "") -> str:
    biz_line = f"Vendor's business: {business_name} — selling {products}\n" if business_name else ""
    return f"""Retrieved context (pricing display strategy — general guidance, not live market data):
{context if context else "[No specific pricing context retrieved]"}

{biz_line}Vendor's question: {question}

CRITICAL:
- This agent provides GENERAL PRICING STRATEGY only — NOT real-time commodity prices.
- NEVER quote a specific price as current market rate.
- If the vendor asks for live mandi prices, clearly state: "I don't have access to live
  mandi or market prices. For current rates, check agmarknet.gov.in, your local APMC
  mandi, or trusted local suppliers."
- All pricing advice is general guidance; actual prices depend on the vendor's market.

## Pricing Strategy & Display Guidance
"""


# ---------------------------------------------------------------------------
# Customer engagement prompt
# ---------------------------------------------------------------------------
def engagement_prompt(
    question: str, context: str, business_name: str = "", products: str = "",
) -> str:
    biz_line = f"Vendor's business: {business_name} — selling {products}\n" if business_name else ""
    return f"""Retrieved context (customer engagement and repeat business strategies):
{context if context else "[No specific engagement context retrieved]"}

{biz_line}Vendor's question: {question}

Generate 3–5 concrete, practical, low-cost or free customer engagement ideas.
Make each idea specific to the vendor's type of business.
Keep each idea to 2–3 sentences. Lead with the most actionable ideas.

## Customer Engagement Ideas
"""


# ---------------------------------------------------------------------------
# Business growth advice prompt
# ---------------------------------------------------------------------------
def business_growth_prompt(
    question: str, context: str,
    business_name: str = "", location: str = "", products: str = "", business_type: str = "",
) -> str:
    biz_parts = []
    if business_name:
        biz_parts.append(f"Business: {business_name}")
    if business_type:
        biz_parts.append(f"Type: {business_type}")
    if location:
        biz_parts.append(f"Location: {location}")
    if products:
        biz_parts.append(f"Products: {products}")
    biz_block = "\n".join(biz_parts) + "\n" if biz_parts else ""

    return f"""Retrieved context (business growth and digital visibility guidance):
{context if context else "[No specific growth context retrieved]"}

{biz_block}Vendor's question: {question}

Provide practical business growth guidance using the retrieved context.

REQUIREMENTS:
- All recommendations must be achievable by a street vendor with minimal budget.
- Do NOT guarantee specific outcomes, revenue numbers, or growth rates.
- Do NOT recommend paid tools unless free alternatives are not available.
- Frame suggestions as "this typically helps" rather than "this will definitely work."
- Mention the digital growth stages (discoverable → trustworthy → engaged → financially formal)
  if relevant.

## Business Growth Guidance
"""


# ---------------------------------------------------------------------------
# Digital onboarding prompt
# ---------------------------------------------------------------------------
def digital_onboarding_prompt(
    question: str, context: str,
    business_name: str = "", location: str = "", business_type: str = "",
) -> str:
    biz_line = ""
    if business_name:
        type_suffix = f" ({business_type})" if business_type else ""
        loc_suffix = f" in {location}" if location else ""
        biz_line = f"Vendor: {business_name}{type_suffix}{loc_suffix}\n"

    return f"""Retrieved context (digital onboarding guidance for street vendors):
{context if context else "[No specific onboarding context retrieved]"}

{biz_line}Vendor's question: {question}

REQUIREMENTS:
- Give clear, numbered steps using the retrieved context.
- All tools mentioned should be FREE.
- Explain technical terms: OTP = One Time Password, UPI = Unified Payments Interface.
- NEVER imply these steps are performed automatically by the agent.
- Reassure the vendor that these tools are designed for small businesses.
- Direct them to official portals for actual registration.

## Digital Onboarding Guidance
"""


# ---------------------------------------------------------------------------
# Onboarding checklist prompt
# ---------------------------------------------------------------------------
def onboarding_checklist_prompt(
    business_name: str, location: str, business_type: str, products: str, language: str,
) -> str:
    return f"""Create a personalised Digital Onboarding Checklist for this street vendor.
Format as a numbered checklist with clear status indicators.

Vendor:
- Business name: {business_name}
- Business type: {business_type}
- Location: {location}
- Products/services: {products}

Include all relevant items from this standard sequence:
1. Bank account with mobile number linked (foundation)
2. UPI setup (PhonePe / Google Pay / Paytm — free)
3. WhatsApp Business profile setup (free)
4. Google Business Profile creation (free)
5. e-Shram registration (free, eshram.gov.in)
6. PM SVANidhi loan application (if applicable for street vendors)

For each item, include:
- ✅ or ⬜ checkbox (use ⬜ for all since we don't know current status)
- Action description
- Why it matters (1 line)
- Where to do it (official link or location)

End with: "**Estimated total time to complete all steps: 3–4 hours (spread over 1–2 days)**"

Respond in: {language}

## Your Digital Onboarding Checklist
"""


# ---------------------------------------------------------------------------
# Digital readiness report prompt (generates narrative from scored report)
# ---------------------------------------------------------------------------
def digital_readiness_narrative_prompt(
    score: int, level: str, done_areas: list[str], missing_areas: list[str],
    top_priorities: list[str], summary: str, language: str,
    business_name: str = "", business_type: str = "",
) -> str:
    biz_line = f"for {business_name} ({business_type})" if business_name else "for your business"
    done_str = "\n".join(f"- {a}" for a in done_areas) if done_areas else "- None reported yet"
    missing_str = "\n".join(f"- {a}" for a in missing_areas) if missing_areas else "- None — great job!"
    priorities_str = "\n".join(f"{i+1}. {p}" for i, p in enumerate(top_priorities))

    return f"""Generate a friendly, encouraging digital readiness report {biz_line}.

Assessment data:
- Digital Readiness Score: {score}/100
- Level: {level}
- Summary: {summary}
- Completed areas: {done_str}
- Missing/incomplete areas: {missing_str}
- Top 3 priorities: {priorities_str}

Respond in: {language}

Write the report in this structure:

## Digital Readiness Assessment

**Your Score: {score}/100 — {level}**

[2–3 sentence encouraging summary based on the level and score]

### ✅ What You've Got Right
[List completed areas with a brief positive note for each]

### 🎯 Areas to Work On
[List missing areas with a brief, practical explanation of why each matters]

### 🚀 Your Top 3 Next Actions
[The 3 priority actions, written as friendly, actionable steps]

### 📈 What This Unlocks
[1–2 sentences on what completing these steps enables: visibility, credit access, etc.]

IMPORTANT:
- Be encouraging and respectful.
- Do NOT guarantee outcomes.
- Frame everything as "completing this typically helps" — not "this will guarantee."
"""


# ---------------------------------------------------------------------------
# General chat prompt (fallback)
# ---------------------------------------------------------------------------
def general_chat_prompt(question: str, context: str) -> str:
    ctx_block = f"\n\nRetrieved context that may help:\n{context}" if context else ""
    return f"""Vendor's message: {question}{ctx_block}

IMPORTANT — Read the vendor's message carefully:
- Understand the ACTUAL business type they describe (e.g. yatra/travel service, food stall,
  tailoring, repair, chai, flowers — not just fruits/vegetables).
- Understand their ACTUAL goal (online customers, promotion, payment setup, scheme info, etc.).
- Reply in the SAME language they used (Hinglish → Hinglish, Hindi → Hindi, English → English).
- Keep the response SHORT and PRACTICAL — 100–150 words max unless more is needed.
- Use numbered steps for actions. Use simple words.

If the vendor needs online customers or promotion, provide:
1. 2–3 practical digital visibility steps (WhatsApp, Google, local groups).
2. A short ready-to-copy promotional message with [placeholders] for missing details.
3. One clear next action.

Do NOT mention fruits/vegetables unless the vendor is a fruit/vegetable seller.
Do NOT guarantee results. Do NOT invent customer numbers or statistics.
If information is unavailable, say so honestly.

## VendorSetu AI Response
"""
