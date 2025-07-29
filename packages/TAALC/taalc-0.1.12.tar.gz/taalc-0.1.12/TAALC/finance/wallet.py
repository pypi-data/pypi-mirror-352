from .tokens_bag import TokensBag
from ..tg_environment.t_user import TUser
from .currency import Currency
from .transaction import Transaction

class Wallet(TokensBag):

    user: TUser
    # currency: Currency

    def __init__(self, user: TUser):
        self.user = user
        # self.currency = currency

    def amount(self, currency: Currency) -> float:
        received = Transaction.resource.read(sent_to=self.user.data_id, currency=currency.data_id)
        total_input = sum(tr.amount for tr in received)

        spent = Transaction.resource.read(sent_from=self.user.data_id, currency=currency.data_id)
        total_output = sum(tr.amount for tr in spent)

        res = total_input - total_output
        return res