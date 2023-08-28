from typing import Any


def is_user_recipient(user_id: str | int, message: dict[str, Any]) -> bool:
    return user_id == message.get("recipient_id")
