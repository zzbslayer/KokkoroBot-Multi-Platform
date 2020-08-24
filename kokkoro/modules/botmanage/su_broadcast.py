from kokkoro.service import Service, BroadcastTag
from kokkoro import priv
from kokkoro.common_interface import KokkoroBot, EventInterface

sv = Service('su-broadcast', use_priv=priv.SUPERUSER, manage_priv=priv.SUPERUSER, enable_on_default=True, visible=False)

@sv.on_prefix(('广播', 'bc', 'broadcast'))
async def broadcast(bot: KokkoroBot, ev: EventInterface):
    msg = ev.get_param().remain
    await sv.broadcast(msg, BroadcastTag.default)