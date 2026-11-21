# main.py
import logging

from fastapi import FastAPI
from pydantic import BaseModel

from ai_customer_support.routes import orders
from ai_customer_support.routes import chat

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info("Hello there")

app = FastAPI()
app.include_router(orders.router)
app.include_router(chat.router)
