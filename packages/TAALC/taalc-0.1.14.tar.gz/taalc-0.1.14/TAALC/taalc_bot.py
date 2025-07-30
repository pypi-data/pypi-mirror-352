from .worker import Worker
from aiogram import Bot, Dispatcher, types, Router, filters, F
from aiogram.filters.command import Command, CommandStart
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION, PROMOTED_TRANSITION
from epure.resource.db.db import Db
import asyncio
from collections import OrderedDict
from typing import List
# from .teest.tester import Tester


class TaalcBot(Worker):
    bot_token:str
    bot:Bot
    dsp:Dispatcher
    config:object
    testers: list = []

    msg_handlers = OrderedDict()
    cmd_handlers = OrderedDict()

    join_handlers = []
    leave_handlers = []
    promoted_handlers = []
    reaction_handlers = []

    error_prefix = ''

    db: Db = None

    

    def __init__(self, bot_token: str, db:Db=None, config:object=None, error_prefix = ''):        

        self.bot_token = bot_token
        self.config = config
        self.db = db
        self.__class__.error_prefix = error_prefix


        self.bot = Bot(self.bot_token)        
        self.dsp = Dispatcher()
        
        for route, handler in reversed(self.msg_handlers.items()):
            self.dsp.message(F.text.regexp(route).as_("match"))(handler)

        for route, handler in self.cmd_handlers.items():
            self.dsp.message(Command(route))(handler)

        for handler in self.join_handlers:
            self.dsp.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))(handler)

        for handler in self.leave_handlers:
            self.dsp.chat_member(ChatMemberUpdatedFilter(LEAVE_TRANSITION))(handler)

        for handler in self.promoted_handlers:
            self.dsp.chat_member(ChatMemberUpdatedFilter(PROMOTED_TRANSITION))(handler)

        for handler in self.reaction_handlers:
            self.dsp.message_reaction()(handler)
   
 
    def start(self):
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._start())
        except RuntimeError as ex:
            asyncio.run(self._start())
        
    async def _start(self):
        await self.dsp.start_polling(self.bot, skip_updates=True)

    async def stop(self):
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._stop())
        except RuntimeError as ex:
            asyncio.run(self._stop())

    async def _stop(self):
        await self.dsp.stop_polling()

    # def create_parser() -> ArgumentParser:
    #     parser = ArgumentParser()
    #     parser.add_argument("--token", help="Telegram Bot API Token")
    #     parser.add_argument("--chat-id", type=int, help="Target chat id")
    #     parser.add_argument("--message", "-m", help="Message text to sent", default="Hello, World!")

    #     return parser
