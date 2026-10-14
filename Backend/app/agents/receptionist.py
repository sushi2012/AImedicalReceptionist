import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from app.tools.clinic_tools import (
    get_clinic_information as get_clinic_information_data,
    search_clinic_faq as search_clinic_faq_data,
)

load_dotenv()


@tool
def get_clinic_information() -> dict:
    """Get clinic name, address, phone, working hours, services, and FAQs."""
    return get_clinic_information_data()


@tool
def search_clinic_faq(question: str) -> dict:
    """Search clinic FAQs for a patient question, including paraphrases.

    Use this for questions about walk-ins, appointments, cleaning,
    services, or similar topics even when wording differs from the FAQs.
    """
    return search_clinic_faq_data(question)


def build_receptionist():
    """Create the AI receptionist agent."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to Backend/.env."
        )

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

    return create_react_agent(
        model=llm,
        tools=[get_clinic_information, search_clinic_faq],
        prompt=(
            "You are a polite AI receptionist for Sunshine Dental Clinic. "
            "Always use your tools before answering. "
            "Call search_clinic_faq for FAQ-style questions, including "
            "paraphrases. Call get_clinic_information for hours, address, "
            "phone, and the list of services. "
            "Only state facts returned by the tools. "
            "If a tool says nothing was found, or the data does not include "
            "the requested detail such as prices, say you cannot confirm it "
            "and offer to arrange a callback. Do not guess prices, wait times, "
            "or medical advice. Do not diagnose or prescribe treatment. "
            "For possible emergencies, such as difficulty breathing or "
            "uncontrolled bleeding, advise seeking emergency medical care. "
            "Do not claim to book appointments because booking is not "
            "implemented yet. Be concise, friendly, and professional."
        ),
    )


receptionist = build_receptionist()
