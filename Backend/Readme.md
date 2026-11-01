Advantage	Your implementation	Normal FAQ chatbot
Intelligent response generation	LLM using Groq	Often predefined responses
Tool calling	LangGraph ReAct agent	Usually fixed response flows
Dynamic information retrieval	Calls clinic information tools	Often relies on predefined messages
Different question formulations	FAQ keyword and paraphrase matching	Often requires exact keywords
Controlled responses	Instructions to use verified clinic data	Depends on chatbot configuration
Medical safety	Instructions against diagnosis and prescriptions	Depends on configured rules
Extensibility	Can add specialized tools and workflows	Often limited to configured flows
Backend integration	FastAPI + Python services	Depends on platform



Purple path — user message flows through CORS → rate limiter → input guardrail → LLM → tools → output guardrail → back to user
Teal nodes — the 5 agent tools (clinic info tools hit static data, appointment tools hit MongoDB via a transaction)
Amber nodes — guardrails (input blocks prompt injection, medical advice, emergencies, profanity, off-topic; output blocks medical advice in replies and sanitizes PII)
Red nodes — blocked responses that return a safe message without calling the agent
Indigo nodes — MongoDB Atlas (atomic transaction for booking to prevent double bookings)
MCP path — separate path for external clients like Kiro/Claude Desktop, only exposes clinic info tools, completely independent of the agent