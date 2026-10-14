from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.receptionist import receptionist

router = APIRouter(prefix="/receptionist", tags=["AI Receptionist"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = receptionist.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request.message,
                    }
                ]
            }
        )

        reply = result["messages"][-1].content

        if not isinstance(reply, str):
            reply = str(reply)

        return ChatResponse(reply=reply)

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="The AI receptionist could not process your message.",
        )
