from ai_customer_support.models.chat_model import ChatMessage


def sanitize_input(msg: ChatMessage) -> tuple:
    """
    1. If human handoff is already done, do not reply anything. - #TODO
    2. Ensure enough message content before pushing things further - DONE
    3. Verify no prompt injection - #TODO
    """

    if msg.message and msg.message.strip().__len__() <= 2:
        return {"INVALID", "Need more info"}

    return {"VALID", "Good to proceed"}
