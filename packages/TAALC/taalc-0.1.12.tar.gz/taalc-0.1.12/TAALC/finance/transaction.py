# from __future__ import annotations
# from typing import Optional, TYPE_CHECKING
from epure import epure
from .transaction_batch import TransactionBatch
from .currency import Currency
from ..tg_environment.t_member import TMember
# if TYPE_CHECKING:
from ..tg_environment.t_user import TUser
from datetime import datetime

@epure()
class Transaction():
    transaction_batch: TransactionBatch
    sent_from: TUser
    sent_to: TUser
    currency: Currency
    amount: float
    transaction_time: datetime

    def __init__(self, sent_from, sent_to, currency, amount):

        self.sent_from = sent_from
        self.sent_to = sent_to
        self.currency = currency
        self.amount = amount
        self.transaction_time = datetime.now()