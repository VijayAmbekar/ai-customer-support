# main.py
import logging

from fastapi import FastAPI
from pydantic import BaseModel

from src.routes import orders

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(orders.router)


class ChatMessage(BaseModel):
    session_id: str
    customer_email: str
    message: str


@app.post("/chat")
async def handle_chat(msg: ChatMessage):
    logger.info("Received the message")
    # This is where all your logic will live
    return {"reply": "placeholder"}
