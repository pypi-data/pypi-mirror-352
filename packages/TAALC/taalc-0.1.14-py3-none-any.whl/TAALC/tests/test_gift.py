from pytest import fixture, mark
from ..teest.tester import Tester
from epure.files import IniFile
from .. import __main__ as main
from ..taalc_bot import TaalcBot

@fixture
async def user1():
    config = IniFile("./pyt/pyconfig.ini")
    tested_bot = main.get_bot(config)
    # tested_bot = None
    tested_bot.start()
    res = Tester(config.test_user1_token, tested_bot, config.test_chat_id)
    return res

@mark.asyncio
async def test_process_message(user1):
    user1 = await user1
    TaalcBot.testers = [user1]
    res = await user1.msg('hellow world')
    assert res.is_responded == False

    res = await user1.msg('марат')
    assert res.response and 'шлюха' in res.response.text.lower()

    res = await user1.msg('привет, марат')
    assert res.response and 'шлюха' in res.response.text.lower()
    user1.tested_bot.stop()