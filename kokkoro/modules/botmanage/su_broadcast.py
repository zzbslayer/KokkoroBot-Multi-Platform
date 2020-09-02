from kokkoro.service import BroadcastService, BroadcastTag
from kokkoro import priv
from kokkoro.common_interface import KokkoroBot, EventInterface

sv = BroadcastService('su-broadcast', broadcast_tag=BroadcastTag.default, use_priv=priv.SUPERUSER, manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)

@sv.on_prefix(('广播', 'bc', 'broadcast'))
async def broadcast(bot: KokkoroBot, ev: EventInterface):
    msg = ev.get_param().remain
    await sv.broadcast(msg)