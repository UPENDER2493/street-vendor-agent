"""Demo query test for the religious trip scenario and other key inputs."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.orchestrator import handle_message
from agent import handlers

PASS = "[PASS]"
FAIL = "[FAIL]"

def chk(label, cond):
    print(f"  {PASS if cond else FAIL} {label}")
    return cond

# ── 1. Religious trip / yatra service scenario ──────────────────────────────
print("\n=== DEMO QUERY: Religious Trip Service ===")
demo_msg = (
    "Mera religious trip provide karane ka kaam hai. "
    "Hum Gurgaon se Khatu Shyam ke liye 2nd Saturday ko gaadi bhejte hain. "
    "Mujhe online client dhundne hain."
)
result = handle_message(
    demo_msg,
    language="Hinglish",
    business_name="Khatu Shyam Yatra Seva",
    location="Gurgaon",
    products="Religious trip Gurgaon to Khatu Shyam Ji, 2nd Saturday every month",
    business_type="Travel / Transport Service",
)
print(f"  Intents: {result['intents']}")
print(f"  Labels:  {result['intent_labels']}")

answer_text = " ".join(s["answer"] for s in result["sections"]).lower()

# Print first section for manual inspection
print("\n  --- Response preview ---")
print(result["sections"][0]["answer"][:600])
print("  ---")

chk("1. Not about fruits/vegetables (no fruit-centric content)",
    "fruit seller" not in answer_text and "sabzi" not in answer_text)
chk("2. Goal understood (online customers/visibility)",
    any(w in answer_text for w in ["online", "customer", "client", "whatsapp", "google", "visibility", "visible"]))
chk("3. No system prompt leakage",
    "core rules" not in answer_text and "anti-hallucination" not in answer_text
    and "vendor details:" not in answer_text and "generate a professional" not in answer_text)
chk("4. No raw RAG context dump",
    "[source:" not in answer_text)
chk("5. No fake statistics invented",
    "1000 customers" not in answer_text and "guaranteed booking" not in answer_text)
chk("6. Has substantive content",
    len(answer_text) > 50)
chk("7. Response is in Hinglish / not English-only corporate tone",
    any(w in answer_text for w in ["karo", "karein", "aapka", "se", "mein", "ke liye",
                                     "demo mode", "online", "whatsapp"]))

# ── 2. Hindi input ──────────────────────────────────────────────────────────
print("\n=== Hindi Input ===")
r2 = handle_message("SVANidhi yojana ke baare mein batao", language="Hindi")
a2 = " ".join(s["answer"] for s in r2["sections"]).lower()
chk("No prompt leakage", "core rules" not in a2 and "anti-hallucination" not in a2)
chk("Has content", len(a2) > 50)
chk("Mentions SVANidhi", "svanidhi" in a2 or "loan" in a2 or "yojana" in a2)

# ── 3. English input ────────────────────────────────────────────────────────
print("\n=== English Input ===")
r3 = handle_message("How do I set up UPI payments at my stall?", language="English")
a3 = " ".join(s["answer"] for s in r3["sections"]).lower()
chk("No prompt leakage", "core rules" not in a3 and "retrieved context" not in a3.replace("grounded in retrieved", ""))
chk("Contains UPI guidance", "upi" in a3 or "payment" in a3 or "phonepe" in a3)
chk("No fake claims", "i have created" not in a3 and "i set up your" not in a3)

# ── 4. Normal fruit vendor ──────────────────────────────────────────────────
print("\n=== Normal Fruit Vendor ===")
r4 = handle_message(
    "Mere paas fruit ki dukaan hai, UPI kaise setup karun?",
    language="Hinglish", business_name="Ram Fruits", products="Apple Mango"
)
a4 = " ".join(s["answer"] for s in r4["sections"]).lower()
chk("No prompt leakage", "core rules" not in a4)
chk("Has UPI content", "upi" in a4 or "payment" in a4)

# ── 5. Unknown scheme (anti-hallucination) ──────────────────────────────────
print("\n=== Anti-Hallucination: Unknown Scheme ===")
a5, _, _ = handlers.scheme_lookup("VendorBharat Gold Scheme 2025 mein free gold milega", "Hinglish")
a5l = a5.lower()
chk("No fake gold scheme confirmation", "free gold approved" not in a5l and "gold milega confirmed" not in a5l)
chk("Has content", len(a5) > 30)
chk("No prompt leakage", "core rules" not in a5l and "critical anti-hallucination" not in a5l)

# ── 6. Government scheme query ──────────────────────────────────────────────
print("\n=== Govt Scheme Query ===")
a6, ctx6, srcs6 = handlers.scheme_lookup("PM SVANidhi kya hai?", "Hinglish")
a6l = a6.lower()
chk("No raw context dump", "[source:" not in a6l)
chk("Has scheme info or verify reminder",
    any(w in a6l for w in ["svanidhi", "loan", "official", "verify", "portal", "confirm"]))
chk("Mentions official portal or verify", "official" in a6l or "verify" in a6l or "portal" in a6l or "confirm" in a6l)

print("\n" + "="*50)
print("Demo query verification complete.")
