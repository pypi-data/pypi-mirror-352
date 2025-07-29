from aiogram import Bot, Dispatcher, types, Router
from .tg_environment.t_user import TUser
from .taalc_bot import TaalcBot
from re import Match
import traceback
from aiogram.types import ChatMemberUpdated

def msg_handler(*args):
    def handler_wrapper(handler):

        async def wrapper(message: types.Message, match: Match):
            # if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
            try:
                user = TUser.user_by_tg_user(message.from_user)                
                result =  await handler(message, user, match)
                
                return result
            except Exception as ex:
                tb = traceback.format_tb(ex.__traceback__)
                tb = "\n".join(tb)
                err_msg = f'{ex}\n {tb}'
                if TaalcBot.error_prefix:
                    err_msg = f'{TaalcBot.error_prefix}: {err_msg}'
                await message.reply(err_msg)                    
                raise ex
        
        for route in args:
            TaalcBot.msg_handlers[route] = wrapper
        return wrapper
    return handler_wrapper


def cmd_handler(*args):
    def handler_wrapper(handler):

        async def wrapper(message: types.Message):
            
            try:
                user = TUser.user_by_tg_user(message.from_user)
                result =  await handler(message, user)
                
                return result
            except Exception as ex:
                tb = traceback.format_tb(ex.__traceback__)
                tb = "\n".join(tb)
                err_msg = f'{ex}\n {tb}'
                if TaalcBot.error_prefix:
                    err_msg = f'{TaalcBot.error_prefix}: {err_msg}'
                await message.reply(err_msg)                    
                raise ex
        
        for route in args:
            TaalcBot.cmd_handlers[route] = wrapper
        return wrapper
    return handler_wrapper

async def _on_member_updated(event: ChatMemberUpdated, handler):
    try:
        user = TUser.user_by_tg_user(event.new_chat_member.user)                
        result =  await handler(event, user)
        
        return result
    except Exception as ex:
        tb = traceback.format_tb(ex.__traceback__)
        tb = "\n".join(tb)
        err_msg = f'{ex}\n {tb}'
        if TaalcBot.error_prefix:
            err_msg = f'{TaalcBot.error_prefix}: {err_msg}'
        await event.answer(err_msg)                    
        raise ex
    

def join_handler(handler):
    async def wrapper(event: ChatMemberUpdated):
        return await _on_member_updated(event, handler)
    TaalcBot.join_handlers.append(wrapper)
        
    return wrapper


def leave_handler(handler):
    async def wrapper(event: ChatMemberUpdated):
        return await _on_member_updated(event, handler)
    TaalcBot.leave_handlers.append(wrapper)
        
    return wrapper


def promoted_handler(handler):
    async def wrapper(event: ChatMemberUpdated):
        return await _on_member_updated(event, handler)
    TaalcBot.promoted_handlers.append(wrapper)
        
    return wrapper

def reaction_handler(handler):
    async def wrapper(reaction: types.MessageReactionUpdated):
        try:
            user = TUser.user_by_tg_user(reaction.user)
            result =  await handler(reaction, user)
            
            return result
        except Exception as ex:
            tb = traceback.format_tb(ex.__traceback__)
            tb = "\n".join(tb)
            err_msg = f'{ex}\n {tb}'
            if TaalcBot.error_prefix:
                err_msg = f'{TaalcBot.error_prefix}: {err_msg}'
             
            await reaction.bot.send_message(reaction.chat.id, err_msg)                    
            raise ex
    TaalcBot.reaction_handlers.append(wrapper)
        
    return wrapper