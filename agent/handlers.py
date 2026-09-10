"""
VendorSetu AI — Handlers for structured (form-based) UI tabs.

Each handler corresponds to a specific UI tab/section. They wrap:
  knowledge retrieval → prompt construction → IBM Granite generation

All handlers return (answer, context, sources) unless noted.
"""

from __future__ import annotations

from . import prompts
from .classifier import assess_digital_readiness, ReadinessReport
from .rag import get_kb
from .watsonx_client import generate


def _retrieve(query: str, top_k: int = 3) -> tuple[str, list[dict]]:
    kb = get_kb()
    chunks = kb.retrieve(query, top_k=top_k)
    context = kb.format_context(chunks)
    sources = [{"source": c.source, "heading": c.heading} for c in chunks]
    return context, sources


def _gen(system_extra: str, prompt: str, language: str) -> str:
    system = prompts.BASE_SYSTEM_PROMPT + f"\nRespond in: {language}\n" + system_extra
    return generate(system, prompt)


# ---------------------------------------------------------------------------
# Business Profile
# ---------------------------------------------------------------------------
def build_profile(
    business_name: str, location: str, products: str, language: str,
    business_type: str = "", phone: str = "", extra_notes: str = "",
) -> tuple[str, str, list[dict]]:
    prompt = prompts.profile_builder_prompt(
        business_name, location, products, language,
        business_type=business_type, phone=phone, extra_notes=extra_notes,
    )
    answer = _gen("", prompt, language)
    return answer, "", []


# ---------------------------------------------------------------------------
# Local SEO
# ---------------------------------------------------------------------------
def build_seo(
    business_name: str, location: str, products: str,
    target_customers: str, language: str,
    business_type: str = "", phone: str = "",
) -> tuple[str, str, list[dict]]:
    context, sources = _retrieve(f"local SEO Google Business Profile {products} {business_type}")
    prompt = prompts.seo_prompt(
        business_name, location, products, target_customers, context,
        business_type=business_type, phone=phone,
    )
    answer = _gen("", prompt, language)
    return answer, context, sources


# ---------------------------------------------------------------------------
# Marketing
# ---------------------------------------------------------------------------
def build_marketing(
    business_name: str, product_or_offer: str, location: str,
    tone: str, platform: str, language: str, business_type: str = "",
) -> tuple[str, str, list[dict]]:
    prompt = prompts.marketing_prompt(
        business_name, product_or_offer, location, tone, platform,
        business_type=business_type, language=language,
    )
    answer = _gen("", prompt, language)
    return answer, "", []


# ---------------------------------------------------------------------------
# UPI / Digital Payments
# ---------------------------------------------------------------------------
def upi_lookup(question: str, language: str) -> tuple[str, str, list[dict]]:
    context, sources = _retrieve(question + " UPI setup digital payment QR code")
    prompt = prompts.upi_guidance_prompt(question, context)
    answer = _gen("", prompt, language)
    return answer, context, sources


# ---------------------------------------------------------------------------
# Government / MSME Schemes
# ---------------------------------------------------------------------------
def scheme_lookup(question: str, language: str) -> tuple[str, str, list[dict]]:
    context, sources = _retrieve(
        question + " government scheme MSME SVANidhi loan Mudra Vishwakarma e-Shram",
        top_k=4,
    )
    prompt = prompts.scheme_guidance_prompt(question, context)
    answer = _gen("", prompt, language)
    return answer, context, sources


# ---------------------------------------------------------------------------
# Customer Engagement
# ---------------------------------------------------------------------------
def engagement_lookup(
    question: str, language: str,
    business_name: str = "", products: str = "",
) -> tuple[str, str, list[dict]]:
    context, sources = _retrieve(question + " customer engagement repeat customers loyalty WhatsApp")
    prompt = prompts.engagement_prompt(question, context, business_name=business_name, products=products)
    answer = _gen("", prompt, language)
    return answer, context, sources


# ---------------------------------------------------------------------------
# Pricing Strategy
# ---------------------------------------------------------------------------
def pricing_lookup(
    question: str, language: str,
    business_name: str = "", products: str = "",
) -> tuple[str, str, list[dict]]:
    context, sources = _retrieve(question + " pricing display strategy bundle offer mandi")
    prompt = prompts.pricing_prompt(question, context, business_name=business_name, products=products)
    answer = _gen("", prompt, language)
    return answer, context, sources


# ---------------------------------------------------------------------------
# Business Growth
# ---------------------------------------------------------------------------
def business_growth_lookup(
    question: str, language: str,
    business_name: str = "", location: str = "",
    products: str = "", business_type: str = "",
) -> tuple[str, str, list[dict]]:
    context, sources = _retrieve(
        question + " business growth digital visibility hyperlocal economy online listing ONDC",
        top_k=4,
    )
    prompt = prompts.business_growth_prompt(
        question, context,
        business_name=business_name, location=location,
        products=products, business_type=business_type,
    )
    answer = _gen("", prompt, language)
    return answer, context, sources


# ---------------------------------------------------------------------------
# Digital Onboarding (free-text question)
# ---------------------------------------------------------------------------
def onboarding_lookup(
    question: str, language: str,
    business_name: str = "", location: str = "", business_type: str = "",
) -> tuple[str, str, list[dict]]:
    context, sources = _retrieve(
        question + " digital onboarding WhatsApp Business Google Business e-Shram registration UPI"
    )
    prompt = prompts.digital_onboarding_prompt(
        question, context,
        business_name=business_name, location=location, business_type=business_type,
    )
    answer = _gen("", prompt, language)
    return answer, context, sources


# ---------------------------------------------------------------------------
# Digital Onboarding Checklist (structured)
# ---------------------------------------------------------------------------
def onboarding_checklist(
    business_name: str, location: str, business_type: str,
    products: str, language: str,
) -> tuple[str, str, list[dict]]:
    prompt = prompts.onboarding_checklist_prompt(
        business_name, location, business_type, products, language,
    )
    answer = _gen("", prompt, language)
    return answer, "", []


# ---------------------------------------------------------------------------
# Digital Readiness Assessment
# ---------------------------------------------------------------------------
def digital_readiness_assessment(
    has_upi: bool, has_google_profile: bool, has_whatsapp_business: bool,
    has_online_presence: bool, has_customer_comms: bool, has_govt_registration: bool,
    has_promotions: bool, has_financial_records: bool,
    language: str,
    business_name: str = "", business_type: str = "",
) -> tuple[ReadinessReport, str]:
    """
    Score the vendor's digital readiness, then generate a narrative report via Granite.
    Returns (ReadinessReport, narrative_answer).
    """
    report = assess_digital_readiness(
        has_upi=has_upi,
        has_google_profile=has_google_profile,
        has_whatsapp_business=has_whatsapp_business,
        has_online_presence=has_online_presence,
        has_customer_comms=has_customer_comms,
        has_govt_registration=has_govt_registration,
        has_promotions=has_promotions,
        has_financial_records=has_financial_records,
    )

    done_areas = [a.label for a in report.areas if a.status == "done"]
    missing_areas = [a.label for a in report.areas if a.status == "missing"]

    prompt = prompts.digital_readiness_narrative_prompt(
        score=report.score,
        level=report.level,
        done_areas=done_areas,
        missing_areas=missing_areas,
        top_priorities=report.top_priorities,
        summary=report.summary,
        language=language,
        business_name=business_name,
        business_type=business_type,
    )
    narrative = _gen("", prompt, language)
    return report, narrative
