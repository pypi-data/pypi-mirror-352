from __future__ import annotations
from typing import List

class TaalcToken():
    name: str
    aliases: List[str]

    def __init__(self, name, aliases = None):
        self.name = name
        if aliases:
            self.aliases = aliases

    @classmethod
    def get_by_alias(cls, alias: str) -> TaalcToken:
        pass