from aiogram.types import ChatMemberUpdated
from ..decorators import join_handler, leave_handler,\
      cmd_handler, promoted_handler, reaction_handler
from aiogram import Bot, Dispatcher, types, Router
from ..tg_environment.t_user import TUser

@join_handler
async def new_member(event: ChatMemberUpdated, user):
    await event.answer(f'На колени, животное, <b>{user}</b>!\n'+
                        'Прочитай наши правила, и потом не говори, что ты не знал, петух:\n'+
                        '<a href="https://t.me/polysap_rules/2">Правила полисап</a>', parse_mode="HTML")

@leave_handler
async def left_member(event: ChatMemberUpdated, user):
    await event.answer(f'{user} покинул нас, земля пухом')

@promoted_handler
async def promoted_member(event: ChatMemberUpdated, user):
    await event.answer(f'{user} получил новые звёздочки, респект')

@cmd_handler('start', 'stop')
async def process_cmd(message: types.Message, user: TUser): 
    await message.reply('Ты по русски говори')

@reaction_handler
async def process_reaction(reaction: types.MessageReactionUpdated, user):
    chat = reaction.chat
    await reaction.bot.send_message(chat.id, \
                f'{user} отреагировал на <a href="https://t.me/c/{chat.shifted_id}/{reaction.message_id}">сообщение</a>', parse_mode="HTML")