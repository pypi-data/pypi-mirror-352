from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from epure import epure, proto
from .t_member import TMember
from aiogram.types.user import User
from ..finance.currency import Currency
if TYPE_CHECKING:
    from ..finance.transaction import Transaction
from aiogram.types import Message
# from epure.generics import Check

@epure()
class TUser(TMember):    
    first_name: str
    last_name: str
    username: str
    _wallet = None

    @property
    def wallet(self):
        if not self._wallet:
            from ..finance.wallet import Wallet
            self._wallet = Wallet(self)
        return self._wallet

    @classmethod
    def users(cls):
        res = TUser.resource.read()
        return res

    @classmethod
    def user_by_tg_user(cls, tg_user: User) -> TUser:
        res: TUser = None
        if not cls.tg_user_is_saved(tg_user):
            res = cls.save_user(tg_user)
        else:            
            res = cls.resource.read(telegram_id = tg_user.id)
            res = res[0]
        return res


    def __init__(self, user: User=None):
        # super().__init__()
        if user:
            self.telegram_id = user.id
            self.first_name = user.first_name
            self.last_name = user.last_name
            self.username = user.username

    @classmethod
    def tg_user_is_saved(cls, user: User) -> bool:
        users = cls.users()
        filtered = list(filter(lambda u: u.telegram_id == user.id, users))
        res = len(filtered) > 0
        return res
    
    @classmethod
    def save_user(cls, user: User):
        res = cls(user).save()
        return res
    
    
    def send_currency(self, to_user: TUser, currency: Currency, amount: float) -> Transaction:
        from ..finance.transaction import Transaction
        res = Transaction(self, to_user, currency, amount)
        res = res.save()

        return res
    
    def __str__(self):
        res = 'noname user'
        first_name = self.first_name if self.first_name else ''
        last_name = self.last_name if self.last_name else ''
        if self.username:
            res = f'@{self.username}'
        elif self.first_name or self.last_name:
            res = f'{first_name} {last_name}'
        return res