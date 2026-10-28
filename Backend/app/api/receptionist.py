from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.requests import Request
from uuid import uuid4

from app.agents.receptionist import receptionist
from app.core.limiter import limiter
from app.core.guardrails import check_input, check_output


router = APIRouter(prefix="/receptionist", tags=["AI Receptionist"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(default_factory=lambda: str(uuid4()))


class ChatResponse(BaseModel):
    reply: str
    blocked: bool = False
    reason: str = ""


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    message = chat_request.message

    # ── Input guardrails ──
    blocked, reason, response = check_input(message)
    if blocked:
        print(f"Input guardrail triggered: {reason}")
        return ChatResponse(reply=response, blocked=True, reason=reason)

    # ── Agent ──
    try:
        result = await receptionist.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            },
            config={"configurable": {"thread_id": chat_request.session_id}},
        )

        reply = result["messages"][-1].content

        if not isinstance(reply, str):
            reply = str(reply)

    except Exception as e:
        print(f"Agent error: {e}")
        raise HTTPException(
            status_code=502,
            detail="The AI receptionist could not process your message.",
        )

    # ── Output guardrails ──
    blocked, reason, reply = check_output(reply)
    if blocked:
        print(f"Output guardrail triggered: {reason}")

    return ChatResponse(reply=reply, blocked=blocked, reason=reason)
