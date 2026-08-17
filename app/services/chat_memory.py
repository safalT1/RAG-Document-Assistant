import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

_redis_client = None
_fallback_store: Dict[str, List[Dict[str, str]]] = {}

try:
    import redis
    from app.core.config import REDIS_URL
    _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    _redis_client.ping()
    logger.info("Connected to Redis at %s", REDIS_URL)
except Exception as exc:
    logger.warning("Redis unavailable (%s) -- using in-memory chat memory.", exc)
    _redis_client = None

SESSION_TTL: int = 86400
MAX_HISTORY: int = 20


def _key(session_id: str) -> str:
    return f"chat:{session_id}"


def get_history(session_id: str) -> List[Dict[str, str]]:
    """Return conversation history for a session."""
    if _redis_client is not None:
        raw = _redis_client.get(_key(session_id))
        if raw:
            return json.loads(raw)
        return []
    return list(_fallback_store.get(session_id, []))


def add_message(session_id: str, role: str, content: str) -> None:
   
    history = get_history(session_id)
    history.append({"role": role, "content": content})
    history = history[-MAX_HISTORY:]

    if _redis_client is not None:
        _redis_client.set(_key(session_id), json.dumps(history), ex=SESSION_TTL)
    else:
        _fallback_store[session_id] = history


def clear_history(session_id: str) -> None:
    
    if _redis_client is not None:
        _redis_client.delete(_key(session_id))
    else:
        _fallback_store.pop(session_id, None)
