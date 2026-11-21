"""
Mock Shopify data + lookup helpers.

Swap the ORDERS dict and helper functions for real Shopify Admin API
calls later without touching the rest of the app. Every function here
mirrors a query the AI workflow will need.
"""

from __future__ import annotations

import re
import urllib.parse
from datetime import UTC, datetime, timedelta
from typing import Any
import logging

_NOW = datetime.now(UTC)

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock order data (shaped like Shopify's /admin/api/.../orders.json)
# ---------------------------------------------------------------------------
ORDERS: dict[str, dict[str, Any]] = {
    "#1001": {
        "id": 1001,
        "name": "#1001",
        "email": "alice@example.com",
        "created_at": (_NOW - timedelta(days=5)).isoformat(),
        "financial_status": "paid",
        "fulfillment_status": "fulfilled",
        "line_items": [
            {"title": "Wireless Headphones", "quantity": 1, "price": "89.00"},
            {"title": "USB-C Cable", "quantity": 2, "price": "12.00"},
        ],
        "tracking_company": "FedEx",
        "tracking_number": "FX123456789",
        "tracking_url": "https://track.example.com/FX123456789",
        "estimated_delivery": (_NOW - timedelta(days=1)).date().isoformat(),
        "shipping_address": {"city": "Austin", "country": "US"},
        "total_price": "113.00",
    },
    "#1002": {
        "id": 1002,
        "name": "#1002",
        "email": "bob@example.com",
        "created_at": (_NOW - timedelta(days=2)).isoformat(),
        "financial_status": "paid",
        "fulfillment_status": "unfulfilled",
        "line_items": [
            {"title": "Mechanical Keyboard", "quantity": 1, "price": "149.00"}
        ],
        "tracking_company": None,
        "tracking_number": None,
        "tracking_url": None,
        "estimated_delivery": (_NOW + timedelta(days=4)).date().isoformat(),
        "shipping_address": {"city": "Denver", "country": "US"},
        "total_price": "149.00",
    },
    "#1003": {
        "id": 1003,
        "name": "#1003",
        "email": "alice@example.com",
        "created_at": (_NOW - timedelta(days=3)).isoformat(),
        "financial_status": "paid",
        "fulfillment_status": "fulfilled",
        "line_items": [{"title": "Desk Lamp", "quantity": 1, "price": "45.00"}],
        "tracking_company": "UPS",
        "tracking_number": "1Z999AA10123456784",
        "tracking_url": "https://track.example.com/1Z999AA10123456784",
        "estimated_delivery": _NOW.date().isoformat(),
        "shipping_address": {"city": "Austin", "country": "US"},
        "total_price": "45.00",
    },
    "#1004": {
        "id": 1004,
        "name": "#1004",
        "email": "carol@example.com",
        "created_at": (_NOW - timedelta(days=10)).isoformat(),
        "financial_status": "refunded",
        "fulfillment_status": "fulfilled",
        "line_items": [{"title": "Bluetooth Speaker", "quantity": 1, "price": "79.00"}],
        "tracking_company": "FedEx",
        "tracking_number": "FX987654321",
        "tracking_url": "https://track.example.com/FX987654321",
        "estimated_delivery": (_NOW - timedelta(days=5)).date().isoformat(),
        "shipping_address": {"city": "Seattle", "country": "US"},
        "total_price": "79.00",
    },
    "#1005": {
        "id": 1005,
        "name": "#1005",
        "email": "bob@example.com",
        "created_at": (_NOW - timedelta(hours=6)).isoformat(),
        "financial_status": "pending",
        "fulfillment_status": "unfulfilled",
        "line_items": [{"title": "Webcam HD", "quantity": 1, "price": "59.00"}],
        "tracking_company": None,
        "tracking_number": None,
        "tracking_url": None,
        "estimated_delivery": None,
        "shipping_address": {"city": "Denver", "country": "US"},
        "total_price": "59.00",
    },
}

# ---------------------------------------------------------------------------
# FAQ data (pre-approved, verbatim answers — no LLM rewriting)
# ---------------------------------------------------------------------------
FAQS: dict[str, str] = {
    "return_policy": (
        "You can return any item within 30 days of delivery for a full refund, "
        "provided it's unused and in original packaging. Start a return at "
        "https://example.com/returns."
    ),
    "shipping_times": (
        "Standard shipping takes 3–5 business days within the US. Express "
        "shipping (1–2 business days) is available at checkout."
    ),
    "payment_methods": (
        "We accept Visa, Mastercard, Amex, PayPal, Apple Pay, and Google Pay."
    ),
    "international_shipping": (
        "We currently ship to the US, Canada, UK, and EU. International orders "
        "typically arrive in 7–14 business days."
    ),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_ORDER_RE = re.compile(r"(?:#|ord[-\s]?)?\s*(\d{4,})", re.IGNORECASE)


def _normalize_order_number(order_number: str) -> str:
    """'1001' -> '#1001', '#1001' -> '#1001', 'ORD-1001' -> '#1001'."""
    if not order_number:
        return ""
    digits = re.sub(r"\D", "", order_number)
    return f"#{digits}" if digits else ""


def extract_order_number(text: str) -> str | None:
    """Pull an order number out of a free-text customer message."""
    match = _ORDER_RE.search(text or "")
    return f"#{match.group(1)}" if match else None


def _humanize_status(order: dict[str, Any]) -> str:
    fin, ful = order["financial_status"], order["fulfillment_status"]
    if fin == "refunded":
        return "Refunded."
    if fin == "pending":
        return "Payment pending — order not yet confirmed."
    if ful == "fulfilled":
        carrier = order.get("tracking_company") or "the carrier"
        return f"Shipped via {carrier}."
    if ful == "partial":
        return "Partially shipped — some items are on the way."
    return "Paid and processing — not shipped yet."


# ---------------------------------------------------------------------------
# Public lookups (the "tools" your AI workflow will call)
# ---------------------------------------------------------------------------
def get_order(order_number: str) -> dict[str, Any] | None:
    """Look up a single order by number ('#1001', '1001', 'ORD-1001')."""
    return ORDERS.get(_normalize_order_number(order_number))


def get_order_status(order_number: str) -> dict[str, Any] | None:
    """Compact status summary suitable for an LLM prompt."""
    order = get_order(order_number)
    if not order:
        return None
    return {
        "order_number": order["name"],
        "financial_status": order["financial_status"],
        "fulfillment_status": order["fulfillment_status"],
        "human_readable": _humanize_status(order),
        "estimated_delivery": order.get("estimated_delivery"),
    }


def track_shipment(order_number: str) -> dict[str, Any] | None:
    """Return tracking info, or a clear 'not shipped yet' response."""
    order = get_order(order_number)
    if not order:
        return None
    if not order.get("tracking_number"):
        return {
            "order_number": order["name"],
            "tracking_available": False,
            "message": "This order hasn't shipped yet.",
        }
    return {
        "order_number": order["name"],
        "tracking_available": True,
        "carrier": order["tracking_company"],
        "tracking_number": order["tracking_number"],
        "tracking_url": order["tracking_url"],
        "estimated_delivery": order.get("estimated_delivery"),
    }


def sanitize_query(q: str | None) -> str:
    """
    Normalize free-text input from HTTP callers.

    - None / empty -> ""
    - Trims whitespace
    - URL-decodes once more (idempotent for normal text; fixes double-encoded input)
    - Collapses internal whitespace
    """
    if not q:
        return ""
    try:
        q = urllib.parse.unquote(q)
    except Exception:
        pass
    return " ".join(q.split()).strip()


def _order_haystack(order: dict[str, Any]) -> str:
    """Everything about an order, lowercased, for substring matching."""
    fields = [
        order["name"].lstrip("#"),
        order.get("customer_name", ""),
        order["email"],
        order["email"].split("@")[0],  # local part: "alice"
        *[item["title"] for item in order["line_items"]],
    ]
    return " ".join(str(f) for f in fields).lower()


def list_orders(
    email: str | None = None,
    name: str | None = None,
    q: str | None = None,
) -> list[dict[str, Any]]:
    """
    List orders with optional filters. All filters are:
      - case-insensitive
      - partial-match (substring)
      - ANDed together when multiple are supplied
    """
    orders = list(ORDERS.values())

    email_n = sanitize_query(email).lower()
    if email_n:
        orders = [o for o in orders if email_n in o["email"].lower()]

    name_n = sanitize_query(name).lower()
    if name_n:
        orders = [o for o in orders if name_n in o.get("customer_name", "").lower()]

    q_n = sanitize_query(q)
    if q_n:
        terms = [t.lstrip("#").lower() for t in q_n.split() if t.lstrip("#")]
        orders = [o for o in orders if all(t in _order_haystack(o) for t in terms)]

    return orders


def search_orders(query: str) -> list[dict[str, Any]]:
    """
    Free-text search across order number, customer name, email,
    email local-part, and line-item titles.

    Callers never need to type '#' — '1001', '#1001', and '%231001'
    all behave identically. Multiple terms use AND logic.
    """
    q = sanitize_query(query)

    if not q:
        return []

    terms = [t.lstrip("#").lower() for t in q.split() if t.lstrip("#")]
    if not terms:
        return []

    return [o for o in ORDERS.values() if all(t in _order_haystack(o) for t in terms)]


def order_stats() -> dict[str, Any]:
    """Aggregate counts — handy for a dashboard or an 'ops' endpoint."""
    by_fulfillment: dict[str, int] = {}
    by_financial: dict[str, int] = {}
    for o in ORDERS.values():
        by_fulfillment[o["fulfillment_status"]] = (
            by_fulfillment.get(o["fulfillment_status"], 0) + 1
        )
        by_financial[o["financial_status"]] = (
            by_financial.get(o["financial_status"], 0) + 1
        )
    return {
        "total_orders": len(ORDERS),
        "by_fulfillment_status": by_fulfillment,
        "by_financial_status": by_financial,
    }


def get_faq(topic: str) -> dict[str, Any] | None:
    """Look up a pre-approved FAQ answer by topic key."""
    key = (topic or "").lower().strip().replace(" ", "_")
    answer = FAQS.get(key)
    if not answer:
        return None
    return {"topic": key, "answer": answer}
