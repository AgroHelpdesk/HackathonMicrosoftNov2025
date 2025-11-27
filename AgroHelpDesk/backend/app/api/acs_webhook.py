from fastapi import APIRouter, Request, HTTPException
from app.core.orchestrator import Orchestrator
from app.services.acs_messages import send_message_to_thread
from app.services.session_store import list_history, get_session, add_message
from app.services.session_store import _SESSIONS  # internal access for lookup by thread id in MVP
from app.utils.logger import get_logger

logger = get_logger("acs_webhook")
router = APIRouter()
orch = Orchestrator()

def find_session_by_thread(thread_id: str):
    # simple linear search in in-memory store (fine for MVP)
    for sid, data in _SESSIONS.items():
        if data.get("thread_id") == thread_id:
            return sid, data
    return None, None

@router.post("/events")
async def events(request: Request):
    body = await request.json()
    events = body.get("events", [])
    for ev in events:
        etype = ev.get("eventType")
        if etype == "chatMessageReceived" or etype == "messageReceived":
            thread_id = ev.get("threadId") or ev.get("resource", {}).get("threadId")
            content = None
            # try several payload styles
            if ev.get("content") and isinstance(ev["content"], dict):
                content = ev["content"].get("message") or ev["content"].get("text")
            if not content:
                # legacy shape
                content = ev.get("message", {}).get("content") or ev.get("content", {}).get("message")
            sender = ev.get("senderCommunicationIdentifier", {}).get("rawId") or ev.get("from")
            if not thread_id or not content:
                logger.warning("Event missing thread or content: %s", ev)
                continue
            # find session
            sid, sdata = find_session_by_thread(thread_id)
            # store incoming
            if sid:
                await add_message(sid, role="user", text=content, extra={"sender": sender})
            # call orchestrator
            result = await orch.process(content, session_id=sid)
            reply = result.get("response") or result.get("explicacao") or "Recebi, obrigado."
            # post reply back to ACS thread
            await send_message_to_thread(thread_id, reply)
            # if we have session store, store bot reply
            if sid:
                await add_message(sid, role="bot", text=reply)
    return {"status": "ok"}
