from pydantic import BaseModel
from enum import Enum


class ChatMessage(BaseModel):
    session_id: str
    customer_email: str
    message: str


class Intent(str, Enum):
    ORDER_STATUS = "ORDER_STATUS"  # "where is my order #1001"
    FAQ = "FAQ"  # "what's your return policy"
    REFUND_REQUEST = "REFUND_REQUEST"  # "I want a refund"        → escalate
    HUMAN_HANDOFF = "HUMAN_HANDOFF"  # "talk to a human"        → escalate
    UNKNOWN = "UNKNOWN"  # gibberish                → escalate
