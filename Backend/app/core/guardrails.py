"""Input and output guardrails for the AI receptionist.

These run as fast Python checks — no extra LLM calls — so they
add negligible latency to each request.
"""

import re

# ──────────────────────────────────────────────
#  Input guardrails
# ──────────────────────────────────────────────

# Patterns that indicate someone trying to override the system prompt.
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?previous (instructions|prompts)",
    r"forget (your|all|the previous) (instructions|rules|prompt)",
    r"you are (now|no longer) (a |an )?",
    r"act as (if you are|a |an )",
    r"pretend (you are|to be) (a |an )?",
    r"reveal (your|the) (system )?prompt",
    r"show (me )?(your|the) (system )?(prompt|instructions)",
    r"override (your|the|all) (instructions|rules)",
    r"jailbreak",
    r"do not follow (your|the) (instructions|rules)",
    r"disregard (your|the|all) (previous|prior) (instructions|prompt)",
]

# Keywords that signal the user wants medical advice — not allowed.
MEDICAL_ADVICE_PATTERNS = [
    r"should i take\b",
    r"what (medicine|medication|drug|pill)s?\b",
    r"can you (prescribe|recommend) (me )?(medicine|medication|drug)",
    r"diagnose (me|my)",
    r"what'?s wrong with (me|my) (tooth|teeth|gum)",
    r"how (do|should) i treat\b",
    r"is (this|my) (condition|symptom) (serious|dangerous)",
    r"what dosage\b",
    r"can i take\b .*\bwith\b",
    r"will (this|these) antibiotics\b",
    r"do i need (a )?(root canal|extraction|antibiotic)",
]

# Keywords that signal a possible medical emergency.
EMERGENCY_KEYWORDS = [
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "chest pain",
    "uncontrolled bleeding",
    "won't stop bleeding",
    "lost consciousness",
    "fainted",
    "seizure",
    "heart attack",
    "stroke",
    "swelling that is closing the airway",
    "severe facial trauma",
    "jaw broken",
    "can't stop bleeding",
    "anaphylaxis",
    "choking",
]

# Basic profanity filter (expandable).
PROFANITY_PATTERNS = [
    r"\b(fuck|shit|bitch|asshole|bastard|dick|cunt|wanker|prick)\b",
]

# Topics completely outside the clinic's scope.
OFF_TOPIC_HINTS = [
    "write me a poem",
    "write me a song",
    "write code",
    "write a python",
    "write a javascript",
    "what is the capital of",
    "who is the president",
    "what is your favorite",
    "tell me a joke",
    "write an essay",
    "translate this",
    "what is the meaning of life",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    lowered = text.lower()
    return any(re.search(p, lowered) for p in patterns)


def check_input(message: str) -> tuple[bool, str, str]:
    """Inspect the user's message before it reaches the agent.

    Returns:
        (blocked, reason, response)
        - blocked = True  → the agent is NOT called; return response to user
        - blocked = False → the message is safe, let it through
    """
    # 1. Prompt injection
    if _matches_any(message, PROMPT_INJECTION_PATTERNS):
        return (
            True,
            "prompt_injection",
            "I'm sorry, I can only help with clinic-related requests such as "
            "booking appointments, answering FAQs, or providing clinic information.",
        )

    # 2. Emergency — don't block, but return immediate guidance
    lowered = message.lower()
    if any(keyword in lowered for keyword in EMERGENCY_KEYWORDS):
        return (
            True,
            "emergency",
            "This sounds like it could be a medical emergency. Please call your "
            "local emergency number (e.g. 911 in the US, 112 in India) or go to "
            "the nearest emergency room immediately. Do not wait for an appointment. "
            "Would you like me to help you book a non-emergency appointment as well?",
        )

    # 3. Medical advice request
    if _matches_any(message, MEDICAL_ADVICE_PATTERNS):
        return (
            True,
            "medical_advice_request",
            "I'm not able to provide medical advice, diagnoses, or medication "
            "recommendations. Please consult with a dentist or doctor for that. "
            "I can help you book an appointment with our clinic if you'd like.",
        )

    # 4. Profanity
    if _matches_any(message, PROFANITY_PATTERNS):
        return (
            True,
            "profanity",
            "Let's keep our conversation professional. How can I help you "
            "with your dental clinic needs today?",
        )

    # 5. Off-topic
    if any(hint in lowered for hint in OFF_TOPIC_HINTS):
        return (
            True,
            "off_topic",
            "I'm the AI receptionist for Sunshine Dental Clinic. I can help you "
            "with booking appointments, clinic hours, services, and FAQs. "
            "Is there something clinic-related I can help you with?",
        )

    return (False, "", "")


# ──────────────────────────────────────────────
#  Output guardrails
# ──────────────────────────────────────────────

# Patterns that suggest the agent is giving medical advice.
OUTPUT_MEDICAL_ADVICE = [
    r"you (should|need to) take\b",
    r"take \d+\s?mg\b",
    r"you (have|may have)\b .*\b(cavity|infection|abscess|gingivitis|periodontitis)",
    r"this (is|looks like|appears to be) (a |an )?\w+ (infection|cavity|abscess)",
    r"i (recommend|prescribe|suggest)\b .*\b(medication|antibiotic|painkiller|ibuprofen|paracetamol|amoxicillin)",
]

# Patterns that look like raw PII that shouldn't be echoed back.
PII_PATTERNS = [
    # Credit card numbers (16 digits, optional spaces/dashes)
    r"\b(?:\d[ -]*?){13,16}\b",
    # Email addresses
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
]


def check_output(reply: str) -> tuple[bool, str, str]:
    """Inspect the agent's reply before returning it to the user.

    Returns:
        (blocked, reason, sanitized_reply)
        - blocked = True  → replace with safe fallback message
        - blocked = False → return reply as-is (or sanitized version)
    """
    # 1. Medical advice in output
    if _matches_any(reply, OUTPUT_MEDICAL_ADVICE):
        return (
            True,
            "medical_advice_output",
            "I'm not able to provide medical advice or medication recommendations. "
            "Please consult with our dentist for a proper assessment. "
            "Would you like me to help you book an appointment?",
        )

    # 2. PII leakage — sanitize instead of blocking
    sanitized = reply
    for pattern in PII_PATTERNS:
        if re.search(pattern, reply):
            sanitized = re.sub(pattern, "[REDACTED]", sanitized)

    if sanitized != reply:
        return (False, "pii_sanitized", sanitized)

    return (False, "", reply)
