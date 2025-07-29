
#default_handler.py
from pathlib import Path
from typing import Dict, List

from .config import cfg
from .tools_and_personas import DigitalPersona
from .handler import ConvoProcesser

CHAT_CACHE_LENGTH = int(cfg.get("CHAT_CACHE_LENGTH"))
CHAT_CACHE_PATH = Path(cfg.get("CHAT_CACHE_PATH"))


class DefaultHandler(ConvoProcesser):
    def __init__(self, role: DigitalPersona, markdown: bool) -> None:
        super().__init__(role, markdown)
        self.role = role

    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        messages = [
            {"role": "system", "content": self.role.definition},
            {"role": "user", "content": prompt},
        ]
        return messages