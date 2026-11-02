"""Twilio voice call endpoints for the AI dental receptionist.

Flow:
  1. Patient calls the Twilio number
  2. Twilio POSTs to /voice/incoming
     → We greet and start listening (<Gather input="speech">)
  3. Patient speaks → Twilio transcribes → POSTs to /voice/process
     → We send transcript to the AI agent
     → Agent returns text reply
     → We wrap in <Say> + <Gather> to speak and keep listening
  4. Loop continues until the patient says goodbye or hangs up
"""

import os
import logging
from uuid import uuid4

from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.agents.receptionist import receptionist
from app.core.limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice"])

# Twilio's Polly voice — sounds natural and professional
VOICE = "Polly.Joanna"
LANGUAGE = "en-US"

# How long Twilio waits after the caller stops speaking (seconds)
SPEECH_TIMEOUT = "auto"

# In-memory session store: call_sid → thread_id
# This lets the AI agent remember context across turns of the same call.
_call_sessions: dict[str, str] = {}


def _get_or_create_thread(call_sid: str) -> str:
    """Return the agent thread ID for this call, creating one if needed."""
    if call_sid not in _call_sessions:
        _call_sessions[call_sid] = str(uuid4())
    return _call_sessions[call_sid]


def _build_gather(action: str) -> Gather:
    """Return a <Gather> that listens for speech and posts to `action`."""
    return Gather(
        input="speech",
        action=action,
        method="POST",
        speech_timeout=SPEECH_TIMEOUT,
        language=LANGUAGE,
    )


def _twiml_response(text: str, gather_action: str, hangup: bool = False) -> Response:
    """Build a TwiML response that speaks `text` then listens again (or hangs up)."""
    vr = VoiceResponse()

    if hangup:
        vr.say(text, voice=VOICE)
        vr.hangup()
    else:
        gather = _build_gather(gather_action)
        gather.say(text, voice=VOICE)
        vr.append(gather)

        # Fallback if the caller says nothing
        vr.say(
            "I didn't catch that. Please call us back if you need help. Goodbye!",
            voice=VOICE,
        )
        vr.hangup()

    return Response(content=str(vr), media_type="application/xml")


# ── Endpoint 1: incoming call ──────────────────────────────────────────────

@router.post("/incoming")
@limiter.limit("30/minute")
async def incoming_call(
    request: Request,
    CallSid: str = Form(default=""),
):
    """Twilio calls this when a patient dials the clinic number.

    Creates a session for this call and greets the patient.
    """
    logger.info("Incoming call: CallSid=%s", CallSid)

    # Pre-create the thread so the first turn has a session
    if CallSid:
        _get_or_create_thread(CallSid)

    greeting = (
        "Hello! Thank you for calling Sunshine Dental Clinic. "
        "I'm Sunny, your AI receptionist. "
        "I can help you with our working hours, services, or booking an appointment. "
        "How can I help you today?"
    )

    return _twiml_response(greeting, gather_action="/voice/process")


# ── Endpoint 2: process speech ─────────────────────────────────────────────

@router.post("/process")
@limiter.limit("30/minute")
async def process_speech(
    request: Request,
    CallSid: str = Form(default=""),
    SpeechResult: str = Form(default=""),
    Confidence: str = Form(default="0"),
):
    """Twilio calls this with the transcribed speech after each patient turn.

    Sends the transcript to the AI agent and speaks the reply back.
    """
    logger.info(
        "Speech received: CallSid=%s confidence=%s text=%r",
        CallSid, Confidence, SpeechResult,
    )

    # If Twilio got nothing (silence or timeout), prompt again
    if not SpeechResult.strip():
        return _twiml_response(
            "I'm sorry, I didn't catch that. Could you please repeat?",
            gather_action="/voice/process",
        )

    thread_id = _get_or_create_thread(CallSid)

    # --- Send to agent ---
    try:
        result = await receptionist.ainvoke(
            {"messages": [{"role": "user", "content": SpeechResult}]},
            config={"configurable": {"thread_id": thread_id}},
        )
        reply = result["messages"][-1].content
        if not isinstance(reply, str):
            reply = str(reply)
    except Exception as exc:
        logger.error("Agent error during voice call: %s", exc)
        reply = (
            "I'm sorry, I'm having trouble processing your request right now. "
            "Please hold or call back in a moment."
        )

    # --- Detect goodbye to hang up cleanly ---
    goodbye_words = ["goodbye", "bye", "thank you bye", "that's all", "no thanks", "nothing else"]
    should_hangup = any(word in SpeechResult.lower() for word in goodbye_words)

    if should_hangup:
        reply_with_close = reply + " Thank you for calling Sunshine Dental Clinic. Have a great day!"
        return _twiml_response(reply_with_close, gather_action="/voice/process", hangup=True)

    return _twiml_response(reply, gather_action="/voice/process")
