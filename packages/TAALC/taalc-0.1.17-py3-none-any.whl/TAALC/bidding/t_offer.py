from epure import epure
from ..tg_environment.t_user import TUser
from ..finance.currency import Currency
from ..tg_environment.t_message import TMessage
from .offer_state import OfferState
from .offer_type import OfferType
from uuid import UUID
from datetime import datetime

@epure()
class TOffer:
    from_user: TUser
    to_user: TUser
    offer_type: OfferType
    state: OfferState
    subject: TMessage
    currency: Currency
    price: float
    time: datetime
    duration: int
    message: TMessage
    bidding_id: UUID