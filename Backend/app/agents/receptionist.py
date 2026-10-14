import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from app.services.mcp_client import get_clinic_tools

load_dotenv()

_receptionist = None


async def build_receptionist():
    """Create the AI receptionist agent using MCP clinic tools."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to Backend/.env."
        )

    tools = await get_clinic_tools()

    if not tools:
        raise RuntimeError(
            "No tools were loaded from the clinic MCP server."
        )

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=api_key,
    )

    return create_react_agent(
        model=llm,
        tools=tools,
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


async def get_receptionist():
    global _receptionist

    if _receptionist is None:
        _receptionist = await build_receptionist()

    return _receptionist
