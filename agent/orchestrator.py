"""
VendorSetu AI — Orchestrator (Agentic layer)

Workflow per PS#29:
  User Input → Intent Classification → Business Context Extraction
  → RAG Retrieval → Grounded Prompt Construction → IBM Granite Generation
  → Anti-hallucination wrapped response

Multi-intent: a single message touching multiple domains (e.g. "UPI setup AND customer growth")
triggers parallel intent processing, each with its own RAG retrieval and prompt.

Returns a structured result dict with intents, grounded sections, retrieved context,
and source metadata for display in the UI.
"""

from __future__ import annotations

from .classifier import (
    detect_intents,
    INTENT_BUSINESS_PROFILE,
    INTENT_DIGITAL_PAYMENT,
    INTENT_LOCAL_SEO,
    INTENT_MARKETING,
    INTENT_MSME_SCHEME,
    INTENT_BUSINESS_GROWTH,
    INTENT_DIGITAL_READINESS,
    INTENT_GENERAL_VENDOR_HELP,
    INTENT_LABELS,
)
from . import prompts
from .rag import get_kb
from .watsonx_client import generate


def _retrieve(query: str, top_k: int = 3) -> tuple[str, list[dict]]:
    """
    Retrieve from knowledge base. Returns (formatted_context, source_metadata_list).
    Source metadata includes title, source file, and heading for display.
    """
    kb = get_kb()
    chunks = kb.retrieve(query, top_k=top_k)
    context = kb.format_context(chunks)
    sources = [
        {"source": c.source, "heading": c.heading}
        for c in chunks
    ]
    return context, sources


def handle_message(
    message: str,
    language: str = "Hinglish",
    business_name: str = "",
    location: str = "",
    products: str = "",
    business_type: str = "",
    phone: str = "",
) -> dict:
    """
    Main agentic entrypoint.

    Returns:
        {
            "intents": list of intent codes,
            "intent_labels": list of human-readable intent labels,
            "sections": list of {intent, label, answer},
            "context_used": dict of {label: context_text},
            "sources": dict of {label: list of source dicts},
            "is_grounded": bool,
        }
    """
    intents = detect_intents(message)
    sections = []
    context_used: dict[str, str] = {}
    all_sources: dict[str, list[dict]] = {}

    for intent in intents:
        ctx = ""
        sources: list[dict] = []
        label = INTENT_LABELS[intent]

        if intent == INTENT_DIGITAL_PAYMENT:
            ctx, sources = _retrieve(message + " UPI digital payment QR code setup")
            context_used[label] = ctx
            all_sources[label] = sources
            prompt = prompts.upi_guidance_prompt(message, ctx)

        elif intent == INTENT_MSME_SCHEME:
            ctx, sources = _retrieve(message + " government scheme MSME SVANidhi loan Mudra Vishwakarma", top_k=4)
            context_used[label] = ctx
            all_sources[label] = sources
            prompt = prompts.scheme_guidance_prompt(message, ctx)

        elif intent == INTENT_LOCAL_SEO:
            ctx, sources = _retrieve(message + " local SEO Google Business Profile WhatsApp online discovery")
            context_used[label] = ctx
            all_sources[label] = sources
            prompt = prompts.seo_prompt(
                business_name or "your business", location, products,
                "local residents and nearby customers", ctx,
                business_type=business_type, phone=phone,
            )

        elif intent == INTENT_MARKETING:
            prompt = prompts.marketing_prompt(
                business_name=business_name or "your business",
                product_or_offer=message,
                location=location or "your area",
                tone="friendly and enthusiastic",
                platform="WhatsApp",
                business_type=business_type,
                language=language,
            )

        elif intent == INTENT_BUSINESS_PROFILE:
            ctx, sources = _retrieve(message + " business profile Google WhatsApp digital presence")
            context_used[label] = ctx
            all_sources[label] = sources
            prompt = prompts.profile_builder_prompt(
                business_name=business_name or "your business",
                location=location,
                products=products or message,
                language=language,
                business_type=business_type,
                phone=phone,
            )

        elif intent == INTENT_BUSINESS_GROWTH:
            ctx, sources = _retrieve(
                message + " business growth digital visibility hyperlocal economy online listing",
                top_k=4,
            )
            context_used[label] = ctx
            all_sources[label] = sources
            prompt = prompts.business_growth_prompt(
                message, ctx,
                business_name=business_name, location=location,
                products=products, business_type=business_type,
            )

        elif intent == INTENT_DIGITAL_READINESS:
            ctx, sources = _retrieve(
                message + " digital onboarding checklist UPI WhatsApp Google Business e-Shram"
            )
            context_used[label] = ctx
            all_sources[label] = sources
            prompt = prompts.digital_onboarding_prompt(
                message, ctx,
                business_name=business_name, location=location, business_type=business_type,
            )

        else:  # GENERAL_VENDOR_HELP
            ctx, sources = _retrieve(message, top_k=3)
            context_used[label] = ctx
            all_sources[label] = sources
            prompt = prompts.general_chat_prompt(message, ctx)

        system_prompt = prompts.BASE_SYSTEM_PROMPT + f"\nRespond in: {language}\n"
        answer = generate(system_prompt, prompt)
        sections.append({"intent": intent, "label": label, "answer": answer})

    return {
        "intents": intents,
        "intent_labels": [INTENT_LABELS[i] for i in intents],
        "sections": sections,
        "context_used": context_used,
        "sources": all_sources,
        "is_grounded": bool(context_used),
    }
