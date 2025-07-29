import os
from .senders.telegram_bot_sender import TelegramSender


def send_with_telegram(
    chat_id: str,
    file: str,
    caption: str | None = None,
    token: str | None = None,
) -> None:
    """Send a file with a caption to a telegram chat

    Args:
        chat_id (str): id of the chat to send the file
        file (str): Path of the file to send to the chat
        caption (str | None, optional): Add a caption to the message. Defaults to None.
        token (str | None, optional): Token of the Telegram bot that will send the message. Defaults to None.
            Also can be loaded from the enviroment variable "TELEGRAM_BOT_TOKEN"

    Raises:
        ValueError: If the file does not exists

    Example:
        >>> from log_sender import send_with_telegram
        >>> send_with_telegram(
                "-3248744778",
                "./hello.py",
                "Im a extra caption!",
                "<telegram_bot_token>",
            )


    """
    if not os.path.isfile(file):
        raise ValueError(f"File '{file}' does not exists")

    TelegramSender(token).send(chat_id, file, caption or "")
