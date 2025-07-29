import os
import niquests
from .exceptions import ImproperConfigurationError, BadResponseFromTelegramAPI


class TelegramSender:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ImproperConfigurationError(
                "Missing token parameter in function call and missing 'TELEGRAM_BOT_TOKEN' in env vars."
                "You must set at least one"
            )

    def send(self, chat_id: str, file_path: str, caption: str) -> None:
        res = niquests.post(
            f"https://api.telegram.org/bot{self.token}/sendDocument",
            files={"document": open(file_path, "rb")},
            data={"caption": caption, "chat_id": chat_id},
            stream=True,
        )

        if res.status_code != 200:
            raise BadResponseFromTelegramAPI(res.text)
