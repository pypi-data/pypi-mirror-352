from aiogram import Bot, Dispatcher, types, Router
from ..tg_environment.t_user import TUser
from ..decorators import msg_handler
from ..finance.currency import Currency

# def gift(message: types.Message, user: User, msg_text: str):
#     pass

@msg_handler(r'(?i).*марат.*')
async def process_message(message: types.Message, user: TUser, match):
    msg_text = message.text.lower()
    if message.reply_to_message and \
        ('марат передай' in msg_text or 'марат, передай' in msg_text):

        msg_split = msg_text.split()
        cur_alias = msg_split[-1]
        currency = Currency.get_by_alias(cur_alias)
        amount = float(msg_split[-2])
        wallet_amount = user.wallet.amount(currency)
        if amount <= 0 or wallet_amount <= 0:
            return await message.reply('А нахуй сходить не хочешь?')
            
        
        if amount > wallet_amount:
            res = f"У тебя нет столько {currency.aliases[1]}, кого ты пытаешься наебать? "+\
                f"У тебя всего лишь {wallet_amount} грамм, иди поработай жопой, нищук."
            return await message.reply(res)
            

        # to_user = User.resource.read(telegram_id = message.reply_to_message.from_user.id)[0]
        to_user = TUser.user_by_msg(message.reply_to_message)
        transaction = user.send_currency(to_user, currency, amount)

        return await message.reply_to_message.reply(f"{to_user}, {user} передал тебе {currency.aliases[1]}, "+ \
                            f"{amount} грамм, запрвляй баян")
    elif message.reply_to_message and \
        ('марат, петух' in msg_text or 'марат петух' in msg_text):
        res = "А твоя мамка дешевая подзаборная шлюха, и что? " +\
            "Ну давай посмотрим сколько этот петушок заработал своим очком: \n"
        
        checked_user = TUser.user_by_msg(message.reply_to_message)            
        total = 0
        for cr in Currency.currencies():
            amt = checked_user.wallet.amount(cr)
            total += amt
            res += f'{cr.aliases[0]}: {amt} грамм \n'
        if total <= 300:
            res += f'Петушок {checked_user} похож на нищука, скоро пойдёт нахуй отсюда!'
        else:
            res += f'Похоже петушок {checked_user} неплохо работает жопой!'

        return await message.reply(res)

    elif msg_text in ('марат, я петух', 'марат я петух'): 
        pass
    elif 'пиво' in message.text.lower():
        return await message.reply(f"где сходка?")
    else:
        return await message.reply(f"{message.from_user.first_name} - шлюха")