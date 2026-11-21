from fastapi import APIRouter

from mock_data.mock_shopify import (
    get_faq,
    get_order,
    get_order_status,
    list_orders,
    order_stats,
    search_orders,
    track_shipment,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/stats")
def orders_stats():
    return order_stats()


@router.get("/faq")
def get_faqs(topic: str):
    return get_faq(topic=topic)


@router.get("")
def list_of_orders(email: str, name: str):
    return list_orders(email=email, name=name)


@router.get("/{order_number}/status")
def get_orders_status(order_number: str):
    return get_order_status(order_number=order_number)


@router.get("/{order_number}")
def get_order_detail(order_number: str):
    return get_order(order_number=order_number)


@router.get("/{order_number}/tracking")
def track_order(order_number: str):
    return track_shipment(order_number=order_number)


@router.get("/search/{query}")
def search_order(query: str):
    return search_orders(query=query)
