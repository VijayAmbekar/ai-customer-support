from fastapi import APIRouter
import logging
from ai_customer_support.helpers.guardrails import sanitize_input
from ai_customer_support.models.chat_model import ChatMessage, Intent
from ai_customer_support.helpers.intent_classifier import classify_intent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/chat")
async def handle_chat(msg: ChatMessage):
    logger.info("Received the message")

    status, reply_msg = sanitize_input(msg)

    if status == "INVALID":
        return {"reply": reply_msg}

    # Input sanitized - Procced
    intent = classify_intent(message=msg.message)
    logger.info(f"Identified intent as {intent}")

    # This is where all your logic will live
    return {"reply": "placeholder"}
