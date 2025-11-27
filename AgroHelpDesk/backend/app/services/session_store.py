from typing import Optional
from app.utils.logger import get_logger
logger = get_logger("session_store")

# Simple in-memory store
_SESSIONS: dict = {}

async def create_session(session_id: str, thread_id: str, initial_metadata: dict | None = None):
    _SESSIONS[session_id] = {
        "thread_id": thread_id,
        "metadata": initial_metadata or {},
        "messages": []  # store {role, text, ts}
    }
    logger.info("Session created: %s -> thread %s", session_id, thread_id)
    return _SESSIONS[session_id]

async def get_session(session_id: str):
    return _SESSIONS.get(session_id)

async def add_message(session_id: str, role: str, text: str, extra: dict | None = None):
    s = _SESSIONS.get(session_id)
    if not s:
        return None
    s["messages"].append({"role": role, "text": text, "extra": extra or {}})
    return s

async def list_history(session_id: str):
    s = _SESSIONS.get(session_id)
    return s["messages"] if s else []
