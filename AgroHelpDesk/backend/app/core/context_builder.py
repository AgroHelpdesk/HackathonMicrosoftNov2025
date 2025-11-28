from app.services.session_store import get_session
from app.utils.logger import get_logger

logger = get_logger("context_builder")

async def build_context(session_id: str | None = None, extras: dict | None = None):
    ctx = {}
    if session_id:
        s = await get_session(session_id)
        if s:
            ctx["thread_id"] = s["thread_id"]
            ctx["history"] = s["messages"]
    if extras:
        ctx.update(extras)
    # TODO: fetch IoT telemetry, farm metadata, operator data
    return ctx
