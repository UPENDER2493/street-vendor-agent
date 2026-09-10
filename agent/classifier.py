"""
Intent classifier and digital readiness scorer for VendorSetu AI.

The classifier maps vendor messages to one or more of 8 defined intent types.
The readiness scorer evaluates a vendor profile and returns a structured assessment.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Intent taxonomy (maps to PS#29 capabilities)
# ---------------------------------------------------------------------------
INTENT_BUSINESS_PROFILE = "BUSINESS_PROFILE"
INTENT_DIGITAL_PAYMENT = "DIGITAL_PAYMENT"
INTENT_LOCAL_SEO = "LOCAL_SEO"
INTENT_MARKETING = "MARKETING"
INTENT_MSME_SCHEME = "MSME_SCHEME"
INTENT_BUSINESS_GROWTH = "BUSINESS_GROWTH"
INTENT_DIGITAL_READINESS = "DIGITAL_READINESS"
INTENT_GENERAL_VENDOR_HELP = "GENERAL_VENDOR_HELP"

ALL_INTENTS = [
    INTENT_BUSINESS_PROFILE,
    INTENT_DIGITAL_PAYMENT,
    INTENT_LOCAL_SEO,
    INTENT_MARKETING,
    INTENT_MSME_SCHEME,
    INTENT_BUSINESS_GROWTH,
    INTENT_DIGITAL_READINESS,
    INTENT_GENERAL_VENDOR_HELP,
]

INTENT_LABELS = {
    INTENT_BUSINESS_PROFILE: "Business Profile",
    INTENT_DIGITAL_PAYMENT: "Digital Payments / UPI",
    INTENT_LOCAL_SEO: "Local SEO & Online Visibility",
    INTENT_MARKETING: "Marketing & Promotions",
    INTENT_MSME_SCHEME: "Government / MSME Schemes",
    INTENT_BUSINESS_GROWTH: "Business Growth Advice",
    INTENT_DIGITAL_READINESS: "Digital Readiness Assessment",
    INTENT_GENERAL_VENDOR_HELP: "General Vendor Assistance",
}

# ---------------------------------------------------------------------------
# Keyword maps — extensive Hindi/Hinglish/English coverage
# ---------------------------------------------------------------------------
_KEYWORD_MAP: dict[str, list[str]] = {
    INTENT_BUSINESS_PROFILE: [
        "profile", "business profile", "digital profile", "business card", "visiting card",
        "about my business", "describe my business", "dukaan ki jankari", "dukaan profile",
        "business description", "shop info", "business info", "business name", "my stall",
        "create profile", "profile banao", "shop description", "mera business",
    ],
    INTENT_DIGITAL_PAYMENT: [
        "upi", "payment", "digital payment", "qr", "qr code", "bhim", "phonepe", "paytm",
        "gpay", "google pay", "online payment", "paise", "transaction", "collect money",
        "paise lena", "digital paise", "mobile payment", "upi id", "upi pin", "upi setup",
        "paytm setup", "phonepe setup", "qr code setup", "payment setup", "collect payment",
        "digital transaction", "online payment karna",
    ],
    INTENT_LOCAL_SEO: [
        "seo", "google", "search", "online dikhna", "discover", "maps", "visible", "visibility",
        "online presence", "google maps", "dhundhna", "online milna", "find me online",
        "google listing", "google pe", "maps pe", "online jaana", "internet pe dikhna",
        "online search", "near me", "nearby", "local search", "google business",
    ],
    INTENT_MARKETING: [
        "promotion", "promo", "advertise", "whatsapp message", "flyer", "poster", "banner",
        "offer banao", "message likho", "advertisement", "social media", "instagram",
        "facebook", "promotional", "announce", "marketing", "promote", "offer", "discount",
        "festival offer", "diwali offer", "sale", "brand", "advertisement banao",
        "message banana", "whatsapp status", "caption", "promo banao",
    ],
    INTENT_MSME_SCHEME: [
        "scheme", "yojana", "svanidhi", "loan", "sarkar", "government", "govt", "subsidy",
        "mudra", "credit", "karza", "karj", "vishwakarma", "eshram", "e-shram",
        "sarkari", "mudra loan", "stand-up india", "msme", "grant", "help from govt",
        "government help", "sarkari madad", "financial help", "loan kaise milega",
        "sarkari loan", "business loan", "working capital", "pm svanidhi",
        "pm vishwakarma", "pm mudra", "ayushman", "insurance",
    ],
    INTENT_BUSINESS_GROWTH: [
        "grow", "growth", "zyada customers", "more customers", "increase sales",
        "bikri badhao", "business badhao", "expand", "customer badhana", "sales",
        "revenue", "earn more", "business tips", "business advice", "improve business",
        "online visibility", "hyperlocal", "ondc", "listing platforms", "jiomart",
        "amazon local", "delivery", "home delivery", "order", "business strategy",
        "business development", "scale", "competition",
        "badhana", "badhao", "badhaun", "aage badhao", "grow karna",
        "business grow", "apna business", "mera business", "dukaan badhao",
        # customer engagement is a growth sub-topic
        "customer engagement", "engagement", "loyalty", "repeat customer", "grahak badhao",
        "customer retention", "regular customers", "naye customers",
        # online client acquisition / service business growth
        "online client", "client dhundna", "online booking", "booking chahiye",
        "yatra service", "trip service", "transport service", "service business",
        "new client", "naye clients", "online customers dhundna",
    ],
    INTENT_DIGITAL_READINESS: [
        "digital readiness", "how digital am i", "kitna digital", "assess", "assessment",
        "check my digital", "digital score", "how ready", "digital status", "evaluate",
        "digital checklist", "am i ready", "digital kya karna hai", "next steps",
        "what should i do", "where to start", "kahan se shuru", "digital journey",
        "digital progress",
    ],
    INTENT_GENERAL_VENDOR_HELP: [
        "help", "guide", "madad", "bataao", "samjhao", "kaise", "how", "what",
        "vendor", "street vendor", "hawker", "dukaan", "stall", "sell", "bechna",
        "fruit", "vegetable", "sabzi", "chai", "food", "clothes", "kapde",
        "business", "informal business", "micro business", "small business",
    ],
}


def detect_intents(message: str) -> list[str]:
    """
    Classify a vendor message into one or more intent codes.
    Returns a list of matched intents in priority order.
    Falls back to GENERAL_VENDOR_HELP if nothing specific is matched.
    """
    text = message.lower().strip()
    found: list[str] = []

    # Check in priority order (more specific intents first)
    priority_order = [
        INTENT_DIGITAL_READINESS,
        INTENT_MSME_SCHEME,
        INTENT_DIGITAL_PAYMENT,
        INTENT_LOCAL_SEO,
        INTENT_MARKETING,
        INTENT_BUSINESS_PROFILE,
        INTENT_BUSINESS_GROWTH,
        INTENT_GENERAL_VENDOR_HELP,
    ]
    for intent in priority_order:
        if any(kw in text for kw in _KEYWORD_MAP[intent]):
            found.append(intent)

    # Remove GENERAL_VENDOR_HELP if other specific intents were found
    if len(found) > 1 and INTENT_GENERAL_VENDOR_HELP in found:
        found.remove(INTENT_GENERAL_VENDOR_HELP)

    return found if found else [INTENT_GENERAL_VENDOR_HELP]


# ---------------------------------------------------------------------------
# Digital Readiness Scorer
# ---------------------------------------------------------------------------
READINESS_AREAS = [
    "digital_payments",
    "google_business_profile",
    "whatsapp_business",
    "online_presence",
    "customer_communication",
    "government_registration",
    "promotion_activity",
    "financial_records",
]

READINESS_LABELS = {
    "digital_payments": "Digital Payments (UPI/QR)",
    "google_business_profile": "Google Business Profile",
    "whatsapp_business": "WhatsApp Business",
    "online_presence": "Online Presence",
    "customer_communication": "Customer Communication",
    "government_registration": "Government Registration (e-Shram/ULB)",
    "promotion_activity": "Digital Promotions",
    "financial_records": "Digital Financial Records",
}

READINESS_NEXT_ACTIONS = {
    "digital_payments": "Set up UPI on PhonePe, Google Pay, or Paytm (free, 15–20 min).",
    "google_business_profile": "Create a free Google Business Profile at business.google.com.",
    "whatsapp_business": "Download WhatsApp Business (free) and set up your business profile.",
    "online_presence": "Add your business to Google Maps and share your location on WhatsApp.",
    "customer_communication": "Use WhatsApp Business quick replies and broadcast lists for customers.",
    "government_registration": "Register on e-Shram (eshram.gov.in) for official identity and free insurance.",
    "promotion_activity": "Share weekly WhatsApp updates and post offers on Google Business Profile.",
    "financial_records": "Track daily UPI collections — useful for PM SVANidhi tranche 2/3 eligibility.",
}


@dataclass
class ReadinessArea:
    key: str
    label: str
    status: str  # "done" | "partial" | "missing"
    note: str
    next_action: str


@dataclass
class ReadinessReport:
    score: int  # 0–100
    level: str  # "Beginner" | "Growing" | "Established"
    areas: list[ReadinessArea] = field(default_factory=list)
    top_priorities: list[str] = field(default_factory=list)
    summary: str = ""


def assess_digital_readiness(
    has_upi: bool = False,
    has_google_profile: bool = False,
    has_whatsapp_business: bool = False,
    has_online_presence: bool = False,
    has_customer_comms: bool = False,
    has_govt_registration: bool = False,
    has_promotions: bool = False,
    has_financial_records: bool = False,
) -> ReadinessReport:
    """
    Score a vendor's digital readiness based on self-reported status.
    Returns a ReadinessReport with score, level, and prioritised next actions.
    """
    status_map = {
        "digital_payments": has_upi,
        "google_business_profile": has_google_profile,
        "whatsapp_business": has_whatsapp_business,
        "online_presence": has_online_presence,
        "customer_communication": has_customer_comms,
        "government_registration": has_govt_registration,
        "promotion_activity": has_promotions,
        "financial_records": has_financial_records,
    }

    notes_done = {
        "digital_payments": "You accept UPI payments — great foundation for digital credibility.",
        "google_business_profile": "You have a Google Business Profile — customers can find you online.",
        "whatsapp_business": "WhatsApp Business is set up — professional customer communication ready.",
        "online_presence": "You have an online presence — customers can discover you digitally.",
        "customer_communication": "You communicate digitally with customers — strong engagement tool.",
        "government_registration": "You are registered — access to government benefits is easier.",
        "promotion_activity": "You run digital promotions — this builds brand visibility.",
        "financial_records": "You track digital transactions — useful for future credit applications.",
    }
    notes_missing = {
        "digital_payments": "No digital payment setup detected — cash-only limits customer convenience.",
        "google_business_profile": "No Google Business Profile — missing free local discovery.",
        "whatsapp_business": "No WhatsApp Business — missing direct customer communication channel.",
        "online_presence": "No visible online presence — hard for new customers to discover you.",
        "customer_communication": "No digital customer communication — relying only on physical footfall.",
        "government_registration": "No e-Shram/ULB registration — missing free insurance and scheme access.",
        "promotion_activity": "No digital promotions — missing opportunity to reach new customers.",
        "financial_records": "No digital financial records — harder to qualify for future credit.",
    }

    areas: list[ReadinessArea] = []
    done_count = 0
    missing_keys: list[str] = []

    for key in READINESS_AREAS:
        is_done = status_map[key]
        if is_done:
            done_count += 1
            areas.append(ReadinessArea(
                key=key, label=READINESS_LABELS[key], status="done",
                note=notes_done[key], next_action="",
            ))
        else:
            missing_keys.append(key)
            areas.append(ReadinessArea(
                key=key, label=READINESS_LABELS[key], status="missing",
                note=notes_missing[key], next_action=READINESS_NEXT_ACTIONS[key],
            ))

    score = int((done_count / len(READINESS_AREAS)) * 100)

    if score <= 25:
        level = "Beginner"
    elif score <= 62:
        level = "Growing"
    else:
        level = "Established"

    top_priorities = [READINESS_NEXT_ACTIONS[k] for k in missing_keys[:3]]

    summary_map = {
        "Beginner": (
            "Your business is just beginning its digital journey. The good news: all the "
            "highest-impact steps are free and can be completed in a few hours."
        ),
        "Growing": (
            "You have made a good start with digital tools. Completing the missing areas "
            "will significantly improve your visibility and access to credit opportunities."
        ),
        "Established": (
            "You have a strong digital foundation. Focus on consistency — regular posts, "
            "prompt responses, and UPI usage will continue to build your credibility."
        ),
    }

    return ReadinessReport(
        score=score, level=level, areas=areas,
        top_priorities=top_priorities, summary=summary_map[level],
    )
