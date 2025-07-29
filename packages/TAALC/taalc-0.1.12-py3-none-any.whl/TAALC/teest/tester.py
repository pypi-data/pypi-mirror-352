from aiogram import Bot, Dispatcher
from aiogram.types import Message
from ..taalc_bot import TaalcBot
import asyncio
from .bot_response import BotResponse

class Tester:
    bot: Bot
    test_chat_id: int
    dsp: Dispatcher
    tested_bot: TaalcBot
    responce: BotResponse
    msg_event: asyncio.Event

    
    async def handler(self, message: Message):
        msg_user = message.from_user
        if msg_user.is_bot and message.chat.id == self.test_chat_id and \
              msg_user.id == self.tested_bot.bot.id and not self.msg_event.is_set():
                
            self.responce.msg = message
            self.responce.is_responded = True
            self.msg_event.set()

    async def msg(self, msg_text: str, parse_mode: str=None) -> BotResponse:
        await self.bot.send_message(self.test_chat_id, msg_text, parse_mode=parse_mode)
        responce = BotResponse()
        self.msg_event = asyncio.Event()
        # stop_event = asyncio.Event()
        
        
        # async def waiter():
        #     await asyncio.sleep(3)
        #     stop_event.set()

        asyncio.create_task(self.dsp.start_polling(self.bot, skip_updates=True))
        # asyncio.gather(self.dsp.start_polling(self.bot, skip_updates=True), self.tested_bot._start())

        # asyncio.create_task(waiter())
        # await stop_event.wait()
        await asyncio.sleep(3)
        await self.dsp.stop_polling()

        return responce
        

    def __init__(self, tester_bot_token: str, tested_bot: TaalcBot, test_chat_id: int):
        
        self.bot = Bot(tester_bot_token)
        self.test_chat_id = test_chat_id
        self.dsp = Dispatcher()
        self.tested_bot = tested_bot

        self.dsp.message()(self.handler)