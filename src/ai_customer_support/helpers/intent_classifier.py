"""
Intent classification for customer support messages.

Strategy:
  1. If OPENAI_API_KEY is set, use the LLM (temperature=0, strict label).
  2. On any LLM error (or no key), fall back to regex rules.
  3. Always return one of the fixed Intent values — never free text.
"""

import logging
import os
import re

from ai_customer_support.models.chat_model import Intent

logger = logging.getLogger(__name__)

_INTENT_RULES: list[tuple[Intent, list[str]]] = [
    (
        Intent.HUMAN_HANDOFF,
        [
            r"\b(human|agent|person|representative|manager)\b",
            r"\bspeak (to|with)\b",
            r"\btalk to (someone|a real)\b",
        ],
    ),
    (
        Intent.REFUND_REQUEST,
        [
            r"\brefund\b",
            r"\bmoney back\b",
            r"\bcancel (my )?order\b",
        ],
    ),
    (
        Intent.ORDER_STATUS,
        [
            r"\b(order|package|parcel|shipment)\b",
            r"\b(track|tracking|status|delivery|deliver|shipped|arrive)\b",
            r"#?\d{4,}\b",  # any 4+ digit number, with or without '#'
        ],
    ),
    (
        Intent.FAQ,
        [
            r"\b(return policy|refund policy)\b",
            r"\b(shipping (time|times|cost|fee))\b",
            r"\b(payment|pay|card|paypal|apple pay|google pay)\b",
            r"\b(international|ship to|ship overseas)\b",
            r"\b(faq|policy|policies)\b",
        ],
    ),
]


def classify_intent(message: str) -> str:
    logger.info("Classifiying intent")
    if os.getenv("OPENAI_API_KEY"):
        # LLM based classification - #TODO
        pass

    return classify_with_rules(message=message)


def classify_with_rules(message: str) -> str:
    logger.info("Classifiying intent using rules ...")

    for intent, patterns in _INTENT_RULES:
        for p in patterns:
            if re.search(p, message):
                return intent

    return Intent.UNKNOWN
