from aiogram.types import Message

class BotResponse:
    response: Message = None
    orig: Message = None
    is_responded: bool = False

    def __init__(self, request):
        self.orig = request