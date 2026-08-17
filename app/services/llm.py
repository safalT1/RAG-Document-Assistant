import json
import logging
from typing import List, Dict, Optional

from openai import OpenAI
from app.core.config import GROQ_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)

# ── Initialize OpenAI client (pointing to Groq) ─────────────────────────────
_client: Optional[OpenAI] = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
) if GROQ_API_KEY else None


def generate_answer(
    context: str,
    query: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Generate an answer from context + query + optional chat history.

    This is a **custom RAG** implementation — no RetrievalQAChain.
    """
    if _client is None:
        return (
            f"[MOCK ANSWER — no Groq key configured]\n"
            f"Context: {context[:300]}\n"
            f"Question: {query}"
        )

    system_prompt = (
        "You are a helpful document assistant. "
        "Answer the user's question using ONLY the provided context. "
        "If the context does not contain enough information, say so clearly. "
        "If the user wants to book an interview, collect their name, email, "
        "preferred date (YYYY-MM-DD) and time (HH:MM), then confirm the booking."
    )

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    # Inject previous conversation turns for multi-turn support
    if chat_history:
        messages.extend(chat_history)

    # Current turn with retrieved context
    user_message = (
        f"Context:\n{context}\n\n"
        f"Question:\n{query}"
    )
    messages.append({"role": "user", "content": user_message})

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content


def detect_booking_intent(query: str, answer: str) -> Optional[Dict]:
    """
    Ask the LLM whether the latest exchange contains a complete booking request.

    Returns a dict with {name, email, date, time} if detected, else None.
    """
    if _client is None:
        return None

    extraction_prompt = (
        "Analyze the following conversation exchange and determine if the user "
        "is requesting to book an interview AND has provided ALL of these details:\n"
        "- name\n- email\n- date (YYYY-MM-DD)\n- time (HH:MM)\n\n"
        f"User message: {query}\n"
        f"Assistant response: {answer}\n\n"
        "If ALL four fields are present, respond with ONLY valid JSON:\n"
        '{"name": "...", "email": "...", "date": "YYYY-MM-DD", "time": "HH:MM"}\n\n'
        "If any field is missing or this is not a booking request, respond with: null"
    )

    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.0,
        )
        raw = response.choices[0].message.content.strip()

        if raw.lower() == "null" or raw.lower() == "none":
            return None

        return json.loads(raw)
    except (json.JSONDecodeError, Exception) as exc:
        logger.debug("Booking detection returned non-JSON: %s", exc)
        return None