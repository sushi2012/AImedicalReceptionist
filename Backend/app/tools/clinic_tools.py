
from app.services.clinic_data import CLINIC_INFO


def get_clinic_information() -> dict:
    """Return verified clinic details, services, hours, and FAQs."""
    return {
        "name": CLINIC_INFO["name"],
        "address": CLINIC_INFO["address"],
        "phone": CLINIC_INFO["phone"],
        "working_hours": CLINIC_INFO["working_hours"],
        "services": CLINIC_INFO["services"],
        "faqs": CLINIC_INFO["faqs"],
    }


def search_clinic_faq(question: str) -> dict:
    """Find a relevant FAQ using keywords and common paraphrases."""

    question = question.strip().lower()

    if not question:
        return {
            "found": False,
            "message": "Please provide a question.",
        }

    # Common expressions patients may use for the same topic.
    topic_keywords = {
        "teeth cleaning": [
            "clean", "cleaning", "plaque", "scaling",
            "tartar", "oral hygiene",
        ],
        "walk-ins": [
            "walk in", "walk-in", "without appointment",
            "drop in", "direct visit",
        ],
        "appointments": [
            "appointment", "book", "booking",
            "schedule", "reserve",
        ],
    }

    faqs = CLINIC_INFO["faqs"]

    # Try exact question matching first.
    for faq_question, answer in faqs.items():
        if question == faq_question.lower():
            return {
                "found": True,
                "question": faq_question,
                "answer": answer,
            }

    # Then try matching common topic keywords.
    for topic, keywords in topic_keywords.items():
        if any(keyword in question for keyword in keywords):
            for faq_question, answer in faqs.items():
                faq_lower = faq_question.lower()

                if topic == "teeth cleaning" and (
                    "teeth cleaning" in faq_lower
                ):
                    return {
                        "found": True,
                        "question": faq_question,
                        "answer": answer,
                    }

                if topic == "walk-ins" and "walk-ins" in faq_lower:
                    return {
                        "found": True,
                        "question": faq_question,
                        "answer": answer,
                    }

                if topic == "appointments" and (
                    "appointment" in faq_lower
                ):
                    return {
                        "found": True,
                        "question": faq_question,
                        "answer": answer,
                    }

    return {
        "found": False,
        "message": (
            "No matching FAQ was found. "
            "Do not guess; ask clinic staff to confirm."
        ),
    }
