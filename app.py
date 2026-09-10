"""
VendorSetu AI — Street Vendor Digitalization Agent
Problem Statement #29 (AICTE 2026) | Agentic AI + RAG | IBM watsonx.ai (Granite)

Run:
    pip install -r requirements.txt
    cp .env.example .env
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from agent import handlers
from agent.classifier import INTENT_LABELS, READINESS_AREAS, READINESS_LABELS
from agent.orchestrator import handle_message
from agent.watsonx_client import is_configured

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="VendorSetu AI — Street Vendor Digitalization Agent",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Brand palette ─────────────────────────────────────── */
:root {
    --brand-primary: #E65100;
    --brand-light:   #FFF3E0;
    --brand-dark:    #BF360C;
    --surface:       #FAFAFA;
    --card-bg:       #FFFFFF;
    --border:        #E0E0E0;
    --muted:         #616161;
    --text:          #212121;
    --success:       #2E7D32;
    --info:          #1565C0;
    --warning:       #F57F17;
}

/* ── Hero ──────────────────────────────────────────────── */
.vs-hero {
    background: linear-gradient(135deg, #E65100 0%, #BF360C 100%);
    color: white;
    padding: 1.6rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.vs-hero-icon { font-size: 2.6rem; line-height: 1; flex-shrink: 0; }
.vs-hero h1 {
    font-size: 1.75rem;
    font-weight: 800;
    margin: 0 0 0.15rem;
    color: white !important;
    line-height: 1.15;
}
.vs-hero p {
    font-size: 0.95rem;
    opacity: 0.88;
    margin: 0 0 0.45rem;
    color: white !important;
}
.vs-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    color: white;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    margin-right: 4px;
}

/* ── Status pills ──────────────────────────────────────── */
.status-live    { color: #2E7D32; font-weight: 700; font-size: 0.88rem; }
.status-offline { color: #BF360C; font-weight: 700; font-size: 0.88rem; }

/* ── Source / intent badges ───────────────────────────── */
.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 12px;
    font-size: 0.71rem;
    font-weight: 600;
    margin: 2px 2px 2px 0;
}
.badge-intent { background: #FFF3E0; color: #E65100; border: 1px solid #FFCC80; }
.badge-source { background: #E3F2FD; color: #1565C0; border: 1px solid #90CAF9; }
.badge-ok     { background: #E8F5E9; color: #2E7D32; border: 1px solid #A5D6A7; }

/* ── Tab section headers ──────────────────────────────── */
.tab-title { font-size: 1.3rem; font-weight: 700; color: var(--text); margin-bottom: 0.2rem; }
.tab-desc  { color: var(--muted); font-size: 0.92rem; margin-bottom: 1.1rem; line-height: 1.5; }

/* ── Info card ────────────────────────────────────────── */
.info-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-left: 4px solid var(--brand-primary);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
}

/* ── Readiness score bar ──────────────────────────────── */
.score-wrap  { background: #EEEEEE; border-radius: 8px; height: 18px; overflow: hidden; margin: 0.4rem 0 0.7rem; }
.score-fill  { height: 100%; border-radius: 8px; }

/* ── Grounding note ───────────────────────────────────── */
.grounding-note { color: #1565C0; font-size: 0.8rem; font-style: italic; margin-top: 0.3rem; }

/* ── Sidebar brand ────────────────────────────────────── */
.sb-brand { text-align: center; padding: 0.8rem 0 0.4rem; }
.sb-brand .name  { font-size: 1.25rem; font-weight: 800; color: #E65100; margin: 0; }
.sb-brand .sub   { font-size: 0.76rem; color: #757575; margin: 2px 0 0; }

/* ── Output area ──────────────────────────────────────── */
.output-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-top: 0.5rem;
}

/* ── Profile completeness bar (sidebar) ──────────────── */
.pct-label { font-size: 0.82rem; color: var(--muted); margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
_defaults: dict = {
    "business_name":  "",
    "business_type":  "Fruits & Vegetables",
    "location":       "",
    "products":       "",
    "phone":          "",
    "language":       "Hinglish",
    "chat_history":   [],
    # Readiness assessment answers
    "ra_upi":     False,
    "ra_google":  False,
    "ra_whatsapp":False,
    "ra_online":  False,
    "ra_comms":   False,
    "ra_govt":    False,
    "ra_promo":   False,
    "ra_records": False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

BUSINESS_TYPES = [
    "Fruits & Vegetables",
    "Food / Snacks / Street Food",
    "Tea / Chai / Beverages",
    "Clothing & Textiles",
    "Electronics & Mobile Accessories",
    "Flowers & Puja Items",
    "Books & Stationery",
    "Toys & Games",
    "Repair / Service Provider",
    "General / Kirana Store",
    "Artisan / Craftsperson",
    "Other",
]
LANGUAGES = ["Hinglish", "Hindi", "English"]

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div style="font-size:2.2rem;">🏪</div>
        <p class="name">VendorSetu AI</p>
        <p class="sub">Your Digital Business Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Connection status ──
    if is_configured():
        st.markdown(
            '<div class="status-live">● IBM Granite (watsonx.ai) — Live</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-offline">● Offline Mode — Demo Fallback Active</div>',
            unsafe_allow_html=True,
        )
        st.caption("Connect IBM Granite: add `WATSONX_API_KEY` + `WATSONX_PROJECT_ID` to `.env`")

    st.divider()

    # ── Business profile fields ──
    filled = sum([
        bool(st.session_state.business_name),
        bool(st.session_state.location),
        bool(st.session_state.products),
    ])
    pct = int(filled / 3 * 100)
    st.markdown(f"**Your Business Profile** — {pct}% complete")
    st.progress(pct / 100)
    if pct < 100:
        st.caption("Complete all 3 fields for the best personalised answers.")

    st.session_state.business_name = st.text_input(
        "Business name *",
        value=st.session_state.business_name,
        placeholder="e.g. Sharma Fresh Fruits",
    )
    st.session_state.business_type = st.selectbox(
        "Business type",
        BUSINESS_TYPES,
        index=BUSINESS_TYPES.index(st.session_state.business_type)
        if st.session_state.business_type in BUSINESS_TYPES else 0,
    )
    st.session_state.location = st.text_input(
        "Location / area *",
        value=st.session_state.location,
        placeholder="e.g. Sector 14, Gurugram",
    )
    st.session_state.products = st.text_area(
        "Products / services *",
        value=st.session_state.products,
        placeholder="e.g. Apple, Banana, Mango, seasonal fruits",
        height=76,
    )
    st.session_state.phone = st.text_input(
        "WhatsApp number (optional)",
        value=st.session_state.phone,
        placeholder="e.g. 98765 43210",
    )
    st.session_state.language = st.selectbox(
        "Response language",
        LANGUAGES,
        index=LANGUAGES.index(st.session_state.language),
    )

    st.divider()

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("🎯 Demo: Fruits", use_container_width=True, help="Load a sample fruit vendor profile"):
            st.session_state.business_name  = "Sharma Fresh Fruits"
            st.session_state.business_type  = "Fruits & Vegetables"
            st.session_state.location       = "Sector 14, Gurugram"
            st.session_state.products       = "Fresh seasonal fruits — Apple, Banana, Mango, Orange, Papaya"
            st.session_state.phone          = "98765 43210"
            st.session_state.language       = "Hinglish"
            st.rerun()
    with col_d2:
        if st.button("☕ Demo: Chai", use_container_width=True, help="Load a sample chai stall profile"):
            st.session_state.business_name  = "Raju Chai Wala"
            st.session_state.business_type  = "Tea / Chai / Beverages"
            st.session_state.location       = "Connaught Place, New Delhi"
            st.session_state.products       = "Masala chai, ginger tea, black tea, cold coffee"
            st.session_state.phone          = "91234 56789"
            st.session_state.language       = "Hindi"
            st.rerun()

    st.caption("⚠️ Demo data is for demonstration only.")
    st.divider()
    st.caption(
        "Powered by **IBM watsonx.ai** (Granite-3-8b-instruct) · "
        "RAG over verified govt/MSME documents · "
        "AICTE 2026 PS#29"
    )


# ---------------------------------------------------------------------------
# Hero banner
# ---------------------------------------------------------------------------
st.markdown("""
<div class="vs-hero">
    <div class="vs-hero-icon">🏪</div>
    <div>
        <h1>VendorSetu AI</h1>
        <p>Digital growth assistant for Indian street vendors &amp; micro-entrepreneurs</p>
        <span class="vs-badge">IBM Granite (watsonx.ai)</span>
        <span class="vs-badge">RAG · 6 Verified Docs</span>
        <span class="vs-badge">AICTE 2026 PS#29</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Shared helpers  (no logic changes — only display presentation)
# ---------------------------------------------------------------------------
def _ctx() -> dict:
    return {
        "business_name": st.session_state.business_name,
        "location":      st.session_state.location,
        "products":      st.session_state.products,
        "business_type": st.session_state.business_type,
        "phone":         st.session_state.phone,
        "language":      st.session_state.language,
    }


def _require_profile(require_products: bool = True) -> bool:
    c = _ctx()
    if not c["business_name"]:
        st.warning("👈 Please enter your **business name** in the sidebar to continue.")
        return False
    if require_products and not c["products"]:
        st.warning("👈 Please enter your **products/services** in the sidebar to continue.")
        return False
    return True


def _show_output(text: str) -> None:
    """Render AI output and offer a plain-text copy block."""
    st.markdown(text)
    with st.expander("📋 Copy plain text"):
        st.code(text, language="")


def _show_sources(context: str, sources: list[dict]) -> None:
    """Collapsible RAG source panel."""
    if not context or not context.strip():
        return
    with st.expander("📚 Knowledge base sources (RAG)"):
        if sources:
            for s in sources:
                st.markdown(
                    f'<span class="badge badge-source">📄 {s["source"]}</span>'
                    f'<span style="font-size:0.82rem;color:#555;margin-left:4px;">{s["heading"]}</span>',
                    unsafe_allow_html=True,
                )
            st.divider()
        st.caption("Retrieved context (first 800 chars):")
        st.text(context[:800] + ("…" if len(context) > 800 else ""))


def _grounding_note() -> None:
    st.markdown(
        '<p class="grounding-note">📚 Response grounded in retrieved knowledge base sources.</p>',
        unsafe_allow_html=True,
    )


def _tab_header(icon_title: str, desc: str) -> None:
    st.markdown(f'<div class="tab-title">{icon_title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tab-desc">{desc}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Tabs  — 11 tabs grouped by function
# ---------------------------------------------------------------------------
(
    tab_chat,
    tab_profile, tab_upi, tab_scheme, tab_onboarding,
    tab_seo, tab_marketing, tab_engagement,
    tab_pricing, tab_growth, tab_readiness,
) = st.tabs([
    "💬 AI Chat",
    "🪪 Business Profile",
    "💳 UPI Payments",
    "🏛️ Govt Schemes",
    "🚀 Get Online",
    "📍 Local SEO",
    "📣 Marketing",
    "🤝 Customers",
    "💰 Pricing",
    "📈 Growth",
    "🔍 Readiness",
])


# ============================================================
# Tab 1 — AI Agent Chat
# ============================================================
with tab_chat:
    _tab_header(
        "💬 AI Agent Chat",
        "Ask anything in Hindi, Hinglish, or English. The agent automatically detects "
        "what help you need, retrieves trusted information, and answers in your language.",
    )

    # Quick-start example prompts
    with st.expander("💡 Example questions — click to expand"):
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("""
**Hindi / Hinglish:**
- *"Meri fruit ki dukaan hai, UPI kaise setup karun?"*
- *"SVANidhi loan kaise milega? Kya main eligible hoon?"*
- *"Customer kaise badhau aur online visible kaise banu?"*
- *"WhatsApp pe mango ka promotion message likhdo"*
""")
        with col_e2:
            st.markdown("""
**English:**
- *"I sell fruits in Gurgaon, how do I get online?"*
- *"What government schemes are available for street vendors?"*
- *"How do I set up UPI payments at my stall?"*
- *"Create a WhatsApp promotion for fresh mangoes."*
""")

    if not st.session_state.business_name:
        st.info("💡 **Tip:** Fill in your business details in the sidebar for personalised answers.")

    # Chat history display
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_msg = st.chat_input("Ask in Hindi, Hinglish, or English…")
    if user_msg:
        st.session_state.chat_history.append(("user", user_msg))
        with st.chat_message("user"):
            st.markdown(user_msg)

        with st.chat_message("assistant"):
            with st.spinner("Analysing your question and retrieving trusted information…"):
                c = _ctx()
                result = handle_message(
                    user_msg,
                    language=c["language"],
                    business_name=c["business_name"],
                    location=c["location"],
                    products=c["products"],
                    business_type=c["business_type"],
                    phone=c["phone"],
                )

            # Intent pills
            if result["intent_labels"]:
                pills_html = "".join(
                    f'<span class="badge badge-intent">🎯 {lbl}</span>'
                    for lbl in result["intent_labels"]
                )
                st.markdown(pills_html + "<br>", unsafe_allow_html=True)

            # Answer sections
            combined = ""
            for section in result["sections"]:
                if len(result["sections"]) > 1:
                    st.markdown(f"---\n### {section['label']}")
                st.markdown(section["answer"])
                combined += f"### {section['label']}\n\n{section['answer']}\n\n"

            # Grounding + collapsible RAG context
            if result["is_grounded"]:
                _grounding_note()
            if any(result["context_used"].values()):
                with st.expander("📚 Retrieved knowledge-base context (RAG)"):
                    for lbl_key, ctx_text in result["context_used"].items():
                        if ctx_text:
                            srcs = result["sources"].get(lbl_key, [])
                            if srcs:
                                st.markdown(f"**{lbl_key}**")
                                for s in srcs:
                                    st.markdown(
                                        f'<span class="badge badge-source">📄 {s["source"]}</span> '
                                        f'<span style="font-size:0.81rem;color:#555;">{s["heading"]}</span>',
                                        unsafe_allow_html=True,
                                    )
                            st.text(ctx_text[:800] + ("…" if len(ctx_text) > 800 else ""))

        st.session_state.chat_history.append(("assistant", combined.strip()))

    if st.session_state.chat_history:
        if st.button("🗑️ Clear chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ============================================================
# Tab 2 — Business Profile Builder
# ============================================================
with tab_profile:
    _tab_header(
        "🪪 Digital Business Profile Builder",
        "Generate a professional digital profile for Google Business, WhatsApp Business, "
        "or a printed visiting card. Uses your sidebar details.",
    )

    extra = st.text_input(
        "Anything special about your business? (optional)",
        placeholder="e.g. fresh daily, home delivery available, 10 years in this area, open 7 days",
        key="profile_extra",
    )

    if st.button("Generate Business Profile", type="primary", key="btn_profile"):
        if _require_profile():
            c = _ctx()
            with st.spinner("Crafting your digital business profile…"):
                answer, _, _ = handlers.build_profile(
                    c["business_name"], c["location"], c["products"], c["language"],
                    business_type=c["business_type"], phone=c["phone"], extra_notes=extra,
                )
            st.success("Profile generated!")
            _show_output(answer)


# ============================================================
# Tab 3 — UPI & Digital Payments
# ============================================================
with tab_upi:
    _tab_header(
        "💳 UPI & Digital Payment Guidance",
        "Step-by-step guidance for setting up UPI payments, printing QR codes, "
        "and accessing PM SVANidhi cashback benefits.",
    )

    st.info(
        "🔒 **Security:** VendorSetu AI will never ask for your UPI PIN, OTP, "
        "bank password, or card details. Never share these with anyone."
    )

    q_upi = st.text_input(
        "Your question about digital payments",
        value="UPI kaise setup karun apni dukaan ke liye?",
        key="upi_q",
    )

    if st.button("Get UPI Guidance", type="primary", key="btn_upi"):
        c = _ctx()
        with st.spinner("Retrieving official UPI guidance…"):
            answer, context, sources = handlers.upi_lookup(q_upi, c["language"])
        st.success("Guidance retrieved!")
        _grounding_note()
        _show_output(answer)
        _show_sources(context, sources)


# ============================================================
# Tab 4 — Government & MSME Schemes
# ============================================================
with tab_scheme:
    _tab_header(
        "🏛️ Government & MSME Scheme Finder",
        "Grounded answers from verified scheme documents — PM SVANidhi, Mudra, "
        "Vishwakarma, e-Shram, and more. Only verified information is shown.",
    )

    st.warning(
        "⚠️ **Important:** Scheme details change over time. Always verify current amounts, "
        "eligibility, and deadlines at the official portal or your nearest ULB / bank / CSC."
    )

    q_scheme = st.text_input(
        "Your question about government schemes",
        value="Street vendors ke liye kaunsi sarkari yojana hai?",
        key="scheme_q",
    )

    if st.button("Look Up Schemes", type="primary", key="btn_scheme"):
        c = _ctx()
        with st.spinner("Retrieving scheme information from verified knowledge base…"):
            answer, context, sources = handlers.scheme_lookup(q_scheme, c["language"])
        st.success("Information retrieved!")
        _grounding_note()
        _show_output(answer)
        _show_sources(context, sources)


# ============================================================
# Tab 5 — Digital Onboarding (Get Online)
# ============================================================
with tab_onboarding:
    _tab_header(
        "🚀 Get Your Business Online",
        "Free tools to go digital: WhatsApp Business, Google Business Profile, "
        "e-Shram registration, and UPI setup — all free, step by step.",
    )

    st.info("💡 Every tool in this guide is **100% free**. No paid subscriptions needed.")

    mode = st.radio(
        "What do you need?",
        ["📋 Generate my personalised checklist", "❓ Ask a specific question"],
        key="onboard_mode",
        horizontal=True,
    )

    if mode == "📋 Generate my personalised checklist":
        st.caption(
            "Fill in your business details in the sidebar, then click below for "
            "a personalised step-by-step digital onboarding checklist."
        )
        if st.button("Generate My Checklist", type="primary", key="btn_checklist"):
            if not st.session_state.business_name:
                st.warning("👈 Please enter your business name in the sidebar.")
            else:
                c = _ctx()
                with st.spinner("Creating your personalised digital onboarding checklist…"):
                    answer, _, _ = handlers.onboarding_checklist(
                        c["business_name"],
                        c["location"] or "your area",
                        c["business_type"],
                        c["products"] or "your products",
                        c["language"],
                    )
                st.success("Checklist generated!")
                _show_output(answer)
    else:
        q_onboard = st.text_input(
            "Your question about going digital",
            value="WhatsApp Business kaise setup karun aur Google pe dukaan kaise dikhau?",
            key="onboard_q",
        )
        if st.button("Get Onboarding Guidance", type="primary", key="btn_onboard"):
            c = _ctx()
            with st.spinner("Retrieving digital onboarding guidance…"):
                answer, context, sources = handlers.onboarding_lookup(
                    q_onboard, c["language"],
                    business_name=c["business_name"],
                    location=c["location"],
                    business_type=c["business_type"],
                )
            st.success("Guidance ready!")
            _grounding_note()
            _show_output(answer)
            _show_sources(context, sources)


# ============================================================
# Tab 6 — Local SEO
# ============================================================
with tab_seo:
    _tab_header(
        "📍 Local SEO & Online Visibility",
        "Get a ready-to-use Google Business Profile description, hyperlocal keywords, "
        "and quick action steps to appear in 'near me' searches — all free.",
    )

    target = st.text_input(
        "Who are your target customers?",
        placeholder="e.g. nearby office-goers, local families, college students",
        key="seo_target",
    )

    if st.button("Generate Local SEO Plan", type="primary", key="btn_seo"):
        if _require_profile():
            c = _ctx()
            with st.spinner("Retrieving SEO best practices and generating your plan…"):
                answer, context, sources = handlers.build_seo(
                    c["business_name"], c["location"], c["products"],
                    target or "local residents", c["language"],
                    business_type=c["business_type"], phone=c["phone"],
                )
            st.success("SEO plan generated!")
            _show_output(answer)
            _show_sources(context, sources)


# ============================================================
# Tab 7 — Marketing & Promotional Content
# ============================================================
with tab_marketing:
    _tab_header(
        "📣 Marketing & Promotional Content",
        "Generate ready-to-send promotional messages for WhatsApp, Instagram, SMS, "
        "or printed flyers — in your language, your tone.",
    )

    offer = st.text_input(
        "What do you want to promote?",
        placeholder="e.g. fresh mangoes arrived, 10% off today, Diwali special offer",
        key="mkt_offer",
    )

    col_p, col_t = st.columns(2)
    with col_p:
        platform = st.selectbox(
            "Platform",
            ["WhatsApp", "Instagram caption", "Facebook post", "Printed flyer", "SMS"],
            key="mkt_platform",
        )
    with col_t:
        tone = st.selectbox(
            "Tone",
            [
                "Friendly and enthusiastic",
                "Simple and informative",
                "Festive / celebratory",
                "Urgent (limited stock / offer)",
                "Warm and community-focused",
            ],
            key="mkt_tone",
        )

    if st.button("Generate Promotional Content", type="primary", key="btn_marketing"):
        if not st.session_state.business_name:
            st.warning("👈 Please enter your business name in the sidebar.")
        elif not offer:
            st.warning("Please describe what you want to promote.")
        else:
            c = _ctx()
            with st.spinner("Writing your promotional content…"):
                answer, _, _ = handlers.build_marketing(
                    c["business_name"], offer, c["location"], tone, platform,
                    c["language"], business_type=c["business_type"],
                )
            st.success("Content ready to copy-paste!")
            _show_output(answer)


# ============================================================
# Tab 8 — Customer Engagement
# ============================================================
with tab_engagement:
    _tab_header(
        "🤝 Customer Engagement & Loyalty",
        "Practical, free or low-cost ideas to attract more customers, "
        "build loyalty, and grow your regular customer base.",
    )

    q_eng = st.text_input(
        "What would you like help with?",
        value="Regular customers kaise badhau aur naye customers attract karun?",
        key="eng_q",
    )

    if st.button("Get Engagement Ideas", type="primary", key="btn_engagement"):
        c = _ctx()
        with st.spinner("Generating customer engagement strategies…"):
            answer, context, sources = handlers.engagement_lookup(
                q_eng, c["language"],
                business_name=c["business_name"], products=c["products"],
            )
        st.success("Ideas generated!")
        _show_output(answer)
        _show_sources(context, sources)


# ============================================================
# Tab 9 — Pricing Strategy
# ============================================================
with tab_pricing:
    _tab_header(
        "💰 Pricing Strategy Advisor",
        "Advice on pricing display, bundle strategies, and customer perception. "
        "General strategy only — not live mandi or market prices.",
    )

    st.info(
        "ℹ️ For live mandi prices, check **agmarknet.gov.in** or your local APMC mandi."
    )

    q_price = st.text_input(
        "Your pricing question",
        value="Apne products ke price kaise display karun jisse zyada bikri ho?",
        key="price_q",
    )

    if st.button("Get Pricing Advice", type="primary", key="btn_pricing"):
        c = _ctx()
        with st.spinner("Retrieving pricing strategy guidance…"):
            answer, context, sources = handlers.pricing_lookup(
                q_price, c["language"],
                business_name=c["business_name"], products=c["products"],
            )
        st.success("Pricing strategy ready!")
        _show_output(answer)
        _show_sources(context, sources)


# ============================================================
# Tab 10 — Business Growth
# ============================================================
with tab_growth:
    _tab_header(
        "📈 Business Growth Advisor",
        "Discover the hyperlocal digital growth path — from being discoverable online "
        "to building financial credibility for future credit access.",
    )

    q_growth = st.text_input(
        "Your growth question",
        value="Mera business kaise badhaun aur zyada customers kaise laun?",
        key="growth_q",
    )

    if st.button("Get Growth Guidance", type="primary", key="btn_growth"):
        c = _ctx()
        with st.spinner("Generating personalised business growth guidance…"):
            answer, context, sources = handlers.business_growth_lookup(
                q_growth, c["language"],
                business_name=c["business_name"], location=c["location"],
                products=c["products"], business_type=c["business_type"],
            )
        st.success("Growth plan ready!")
        _show_output(answer)
        _show_sources(context, sources)


# ============================================================
# Tab 11 — Digital Readiness Assessment
# ============================================================
with tab_readiness:
    _tab_header(
        "🔍 Digital Readiness Assessment",
        "Find out where you stand digitally and get a personalised action plan "
        "with the most impactful next steps for your business.",
    )

    st.markdown("#### Your current digital setup")
    st.caption("Check every item that is already in place:")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.session_state.ra_upi = st.checkbox(
            "I accept UPI / digital payments",
            value=st.session_state.ra_upi, key="cb_upi",
        )
        st.session_state.ra_google = st.checkbox(
            "I have a Google Business Profile",
            value=st.session_state.ra_google, key="cb_google",
        )
        st.session_state.ra_whatsapp = st.checkbox(
            "I use WhatsApp Business",
            value=st.session_state.ra_whatsapp, key="cb_wa",
        )
        st.session_state.ra_online = st.checkbox(
            "I have some online presence",
            value=st.session_state.ra_online, key="cb_online",
        )
    with col_r2:
        st.session_state.ra_comms = st.checkbox(
            "I communicate digitally with customers",
            value=st.session_state.ra_comms, key="cb_comms",
        )
        st.session_state.ra_govt = st.checkbox(
            "I am registered (e-Shram / ULB / CoV)",
            value=st.session_state.ra_govt, key="cb_govt",
        )
        st.session_state.ra_promo = st.checkbox(
            "I run digital promotions",
            value=st.session_state.ra_promo, key="cb_promo",
        )
        st.session_state.ra_records = st.checkbox(
            "I track my digital transactions",
            value=st.session_state.ra_records, key="cb_records",
        )

    # Live score preview
    done_count = sum([
        st.session_state.ra_upi, st.session_state.ra_google,
        st.session_state.ra_whatsapp, st.session_state.ra_online,
        st.session_state.ra_comms, st.session_state.ra_govt,
        st.session_state.ra_promo, st.session_state.ra_records,
    ])
    score_preview = int(done_count / 8 * 100)
    level_preview = (
        "Beginner" if score_preview <= 25
        else ("Growing" if score_preview <= 62 else "Established")
    )
    bar_color = (
        "#E65100" if score_preview <= 25
        else ("#F9A825" if score_preview <= 62 else "#2E7D32")
    )

    st.markdown(f"**Current Score: {score_preview}/100 — {level_preview}**")
    st.markdown(
        f'<div class="score-wrap">'
        f'<div class="score-fill" style="width:{score_preview}%;background:{bar_color};"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.button("Generate Full Readiness Report", type="primary", key="btn_readiness"):
        c = _ctx()
        with st.spinner("Analysing your digital readiness and generating personalised report…"):
            report, narrative = handlers.digital_readiness_assessment(
                has_upi=st.session_state.ra_upi,
                has_google_profile=st.session_state.ra_google,
                has_whatsapp_business=st.session_state.ra_whatsapp,
                has_online_presence=st.session_state.ra_online,
                has_customer_comms=st.session_state.ra_comms,
                has_govt_registration=st.session_state.ra_govt,
                has_promotions=st.session_state.ra_promo,
                has_financial_records=st.session_state.ra_records,
                language=c["language"],
                business_name=c["business_name"],
                business_type=c["business_type"],
            )
        st.success(f"Assessment complete — Score: {report.score}/100 ({report.level})")
        _show_output(narrative)


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.markdown(
    '<p style="text-align:center;font-size:0.78rem;color:#9E9E9E;">'
    'VendorSetu AI &nbsp;·&nbsp; IBM watsonx.ai (Granite-3-8b-instruct) + RAG &nbsp;·&nbsp; '
    'AICTE 2026 Problem Statement #29 &nbsp;·&nbsp; '
    'For guidance only — always verify government scheme details at official portals.'
    '</p>',
    unsafe_allow_html=True,
)
