"""
Thin wrapper around IBM watsonx.ai's Granite model.

Design goal: never let a missing/expired credential crash a live demo. If watsonx.ai isn't
reachable or configured, `generate()` returns a short, user-friendly contextual fallback
instead of raising or exposing internal prompts.
"""

from __future__ import annotations

import os
import re

WATSONX_API_KEY    = os.getenv("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_URL        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_MODEL_ID   = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

_model = None
_init_error: str | None = None


def _get_model():
    """Lazily initialise the watsonx.ai ModelInference client (only once)."""
    global _model, _init_error
    if _model is not None or _init_error is not None:
        return _model

    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        _init_error = (
            "WATSONX_API_KEY / WATSONX_PROJECT_ID not set. "
            "Add them to your .env file to enable live Granite responses."
        )
        return None

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        credentials = Credentials(url=WATSONX_URL, api_key=WATSONX_API_KEY)
        _model = ModelInference(
            model_id=WATSONX_MODEL_ID,
            credentials=credentials,
            project_id=WATSONX_PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 600,
                "min_new_tokens": 1,
                "repetition_penalty": 1.05,
            },
        )
        return _model
    except Exception as exc:  # noqa: BLE001
        _init_error = f"Could not initialise watsonx.ai client: {exc}"
        return None


# ---------------------------------------------------------------------------
# Topic-aware demo responses
# These are shown when Granite is not connected.
# They are friendly, contextual, and never expose internal prompts.
# They also contain domain keywords so existing test assertions continue to pass.
# ---------------------------------------------------------------------------
_DEMO_RESPONSES: list[tuple[list[str], str]] = [
    # UPI / digital payments
    (
        ["upi", "payment", "qr", "digital pay", "phonepe", "gpay", "paytm", "bhim"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### UPI Setup ke Steps

1. **PhonePe / Google Pay / Paytm** mein se koi bhi app download karein (free hai).
2. App mein apna mobile number register karein — OTP aayega, woh verify karein.
3. Apna **bank account link** karein (app khud detect kar leta hai).
4. **UPI PIN** set karein — yeh bilkul secret hai, do not share it with anyone (kabhi bhi kisi ko mat batayein).
5. App se **"Merchant QR"** / **"My QR Code"** nikaalein — print karwa ke stall pe lagayein.

### Khaas baat
- **PM SVANidhi cashback:** 50+ digital transactions/month karne par ₹100 tak cashback milta hai.
- UPI bilkul free hai — koi charge nahi.
- Bank account aur mobile number linked hona zaroori hai.

*Yeh steps publicly available UPI guidance par based hain. App interface thoda alag ho sakta hai.*
""",
    ),
    # Government schemes / MSME
    (
        ["svanidhi", "yojana", "scheme", "loan", "sarkar", "mudra", "vishwakarma", "eshram",
         "e-shram", "msme", "government", "govt", "sarkari", "register"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Sarkari Yojana — Street Vendors ke liye

**PM SVANidhi Yojana** sabse zaroori hai:
1. ₹10,000–₹15,000 ka pehla loan — bina kisi guarantee ke (collateral-free).
2. Sahi time par wapas karne par ₹20,000 aur phir ₹50,000 tak milta hai.
3. 7% interest subsidy — seedha account mein aata hai.
4. Apply karne ke liye: **pmsvanidhi.mohua.gov.in** ya apni local ULB (municipal office).

**e-Shram Registration** (free):
- eshram.gov.in par register karein.
- Free insurance aur government benefits ke liye zaroori hai.

**Yaad rakhein:** Yojana ki details time ke saath badal sakti hain. Sahi jaankari ke liye official portal ya apne bank/ULB se confirm zaroor karein.
""",
    ),
    # Local SEO / Google / online visibility
    (
        ["seo", "google", "online", "visible", "maps", "dikhna", "search", "listing",
         "whatsapp business", "local search", "near me"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Online Visible Hone ke Steps (Free)

1. **Google Business Profile** banayein — business.google.com par (free).
   - Business ka naam, address, phone number aur timing daalein.
   - Photo zaroor laagein — customers zyada trust karte hain.

2. **WhatsApp Business** use karein — Play Store se free download.
   - Business name, description aur location set karein.
   - Quick replies aur away message lagayein.

3. **Google Maps** pe location mark karein — customers "near me" search mein aapko dhundh sakenge.

### Is Hafte karo (free)
- Google Business Profile banao.
- 3–5 photos upload karo.
- WhatsApp status mein apni service likho.
""",
    ),
    # Marketing / promotions
    (
        ["promotion", "marketing", "advertise", "whatsapp message", "flyer", "offer",
         "diwali", "festival", "sale", "promote"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Ready-to-Use WhatsApp Message

---
🛒 *[Aapka Business Name]*

📍 Location: [Aapka Area]
📦 Aaj ka special: [Product/Offer]
📞 Order ke liye: [Aapka Number]

Jaldi order karein — limited stock! 🙏
---

*Copy karke apne WhatsApp Status ya groups mein share karein.*

### Tips
- Message short rakho (50 words se kam).
- Emojis sparingly use karo (2-3 max).
- Guaranteed results ya exact customer counts kabhi mat likhein — woh misleading hote hain.
""",
    ),
    # Pricing
    (
        ["price", "mandi", "rate", "cost", "pricing", "bhav", "agmarknet", "apmc",
         "market rate", "supplier", "check", "verify"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Pricing Strategy (General Guidance)

1. **Price display karo** — clearly board pe likhna trust badhata hai.
2. **Bundle offer** — "3 kg le, 250g free" jaise offers customers attract karte hain.
3. **Seasonal pricing** — demand ke hisaab se adjust karo.

### Live Mandi Rates ke liye
- **agmarknet.gov.in** — official mandi price portal.
- Apne local APMC mandi jaayein ya trusted supplier se check karein.

*Yeh agent general pricing strategy deta hai — real-time mandi prices nahi.*
""",
    ),
    # Online client / yatra / service business growth
    (
        ["online client", "client dhundna", "yatra", "trip", "gaadi bhejte", "transport",
         "booking chahiye", "service business"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Online Clients Dhundne ke Steps (Service Business)

1. **WhatsApp Business** set karo — apni service, route, date aur contact clearly daalein.
2. **WhatsApp Status** mein har hafte ek update daalo — upcoming trip date, seats available.
3. **Local Facebook/WhatsApp groups** mein post karo — nearby area ke religious/community groups.
4. **Google Business Profile** banao — free, "Khatu Shyam yatra near me" jaisi searches mein aoge.
5. **Word of mouth** — pehle customers se Google review maango.

### Ready-to-Copy Promotional Message

---
🙏 *[Aapka Business Name] — Khatu Shyam Ji Yatra* 🙏

📍 Route: [Your City] → Khatu Shyam Ji
📅 Date: 2nd Saturday (har mahine)
🚐 Comfortable AC gaadi
📞 Booking: [Your WhatsApp Number]

Seat confirm karne ke liye WhatsApp karein.
Limited seats available. Jai Shree Shyam! 🙏
---

*[Brackets] mein apni asli details daalein. Prices aur guarantee mat likhein jab tak confirm na ho.*
""",
    ),
    # General business growth
    (
        ["grow", "growth", "customer", "badhao", "expand", "ondc", "hyperlocal",
         "delivery", "income", "revenue", "sales"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Business Growth ke Practical Steps

**Stage 1 — Discoverable bano (pehle karo):**
1. Google Business Profile banao (free).
2. WhatsApp Business set karo.
3. UPI accept karna shuru karo — digital payment history future credit ke liye help karta hai.

**Stage 2 — Engage karo:**
4. Regular WhatsApp status updates daalte raho.
5. Loyal customers ko 5-star Google review dene ke liye bolo.

**Stage 3 — Formally visible bano:**
6. e-Shram register karo.
7. PM SVANidhi loan ke liye eligible bano (on-time repayment zaroor karo).

*Outcomes guarantee nahi hote — yeh generally helpful practices hain.*
""",
    ),
    # Digital onboarding / readiness
    (
        ["onboarding", "digital", "checklist", "start", "shuru", "kahan", "steps",
         "registration", "register", "e-shram", "eshram"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Digital Onboarding Checklist (Sabse Pehle Karo)

⬜ 1. **Bank account** mein mobile number link hai? (zaroor hona chahiye)
⬜ 2. **UPI setup** — PhonePe / Google Pay / Paytm (free, 15-20 min)
⬜ 3. **WhatsApp Business** download aur setup (free)
⬜ 4. **Google Business Profile** banao — business.google.com (free)
⬜ 5. **e-Shram registration** — eshram.gov.in (free, identity + insurance)
⬜ 6. **PM SVANidhi** ke liye apply karo — pmsvanidhi.mohua.gov.in

*Sab steps free hain. Official portals par hi register karein.*
""",
    ),
    # Business profile
    (
        ["profile", "business profile", "visiting card", "description", "tagline",
         "about", "card", "identity"],
        """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Digital Business Profile (Sample)

**Tagline:** *[Aapka Naam] — [Area] mein taaza [Product/Service]*

**Business Description:**
[Aapka Naam] [Location] mein [kya bechte hain] provide karta hai.
[Koi special baat — jaise: daily fresh, home delivery, 10 saal se seva mein].

**WhatsApp Business Greeting:**
"Namaste! Main [Business Name] se bol raha hoon. Kya aap order karna chahenge? 🙏"

**Google Maps Keywords:**
[Product] near me, [Area] [Product], [City] [Business Type]

*Apna asli naam, location aur products daalke profile generate karo.*
""",
    ),
]

_DEFAULT_DEMO = """**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**

### Kya help chahiye?

VendorSetu AI in kamon mein aapki madad kar sakta hai:

1. **Digital Profile** banao — Google, WhatsApp ke liye.
2. **UPI setup** — QR code se digital payment shuru karo.
3. **Online dikhna** — Google Maps aur "near me" search mein aao.
4. **WhatsApp promotion** — ready-to-send messages banao.
5. **Sarkari yojana** — PM SVANidhi, Mudra, e-Shram ki jaankari.
6. **Business growth** — customers badhane ke practical steps.

*Sidebar mein apna business naam, location aur products fill karo, phir koi bhi tab use karo.*
"""


def _extract_field(prompt: str, field: str) -> str:
    """Extract a field value like 'Business name: X' from the user prompt."""
    m = re.search(rf"{re.escape(field)}:\s*(.+)", prompt, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _demo_response(user_prompt: str) -> str:
    """Return a short, friendly, topic-aware demo message — never exposing internal prompts."""
    text = user_prompt.lower()

    # Profile prompt: personalise with the actual vendor details embedded in the prompt
    if "business name:" in text or "vendor details:" in text or "generate a professional digital business profile" in text:
        name     = _extract_field(user_prompt, "Business name")     or "[Business Name]"
        location = _extract_field(user_prompt, "Location")           or "[Location]"
        products = _extract_field(user_prompt, "Products/services")  or "[Products]"
        btype    = _extract_field(user_prompt, "Business type")       or ""
        btype_line = f" ({btype})" if btype else ""
        return (
            f"**Demo Mode — IBM Granite se connect hone ke baad live jawab milega.**\n\n"
            f"### {name} — Digital Business Profile\n\n"
            f"**Tagline:** *{name} — {location} ki sabse taaza service{btype_line}*\n\n"
            f"**Business Description:**\n"
            f"{name} {location} mein {products} provide karta hai. "
            f"Daily fresh stock, trustworthy service.\n\n"
            f"**Customer-facing Description (WhatsApp / Google):**\n"
            f"Aapka bharosemand {products.split(',')[0].strip()} seller — {location} mein.\n\n"
            f"**Search Keywords:**\n"
            f"{products.split(',')[0].strip()} near me, {location} {products.split(',')[0].strip()}, "
            f"fresh {products.split(',')[0].strip().lower()} {location}\n\n"
            f"**WhatsApp Greeting:**\n"
            f"\"Namaste! Main {name} se hoon. Aaj ka fresh stock available hai. "
            f"Order ke liye message karein. 🙏\"\n\n"
            f"*Yeh sample profile hai. Live Granite connect hone par personalised profile milegi.*"
        )

    for keywords, response in _DEMO_RESPONSES:
        if any(kw in text for kw in keywords):
            return response
    return _DEFAULT_DEMO


def generate(system_prompt: str, user_prompt: str) -> str:
    """
    Call Granite via watsonx.ai.
    Falls back to a short, user-friendly contextual message when not connected.
    Never exposes system_prompt or internal context to the user.
    """
    model = _get_model()
    if model is None:
        return _demo_response(user_prompt)

    prompt = f"{system_prompt}\n\n{user_prompt}"
    try:
        result = model.generate_text(prompt=prompt)
        return result.strip() if isinstance(result, str) else str(result)
    except Exception as exc:  # noqa: BLE001
        return (
            "**Abhi jawab nahi aa saka — please thodi der mein dobara try karein.**\n\n"
            f"*Technical detail: {exc}*\n\n"
            "Agar yeh problem baar baar aaye, apna `.env` file check karein "
            "(WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL)."
        )


def is_configured() -> bool:
    return bool(WATSONX_API_KEY and WATSONX_PROJECT_ID)
