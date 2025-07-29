from ..finance.taalc_nft import TaalcNft
from .t_user import TUser
from .t_chat import TChat
from ..bidding.t_offer import TOffer
from epure import epure

@epure()
class TMessage():
    owner: TUser
    creator: TUser
    taalc_offer: TOffer
    taalc_nft: TaalcNft
    taalc_chat: TChat
    tg_id: int