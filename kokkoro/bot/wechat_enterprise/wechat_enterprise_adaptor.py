from wechatpy.messages import BaseMessage

from kokkoro.util import to_string
from kokkoro.common_interface import EventInterface
from kokkoro import config
from kokkoro.typing import overrides

class WechatEpEvent(EventInterface):
    def __init__(self, raw_event: BaseMessage):
        self.raw_event = raw_event

    @overrides(EventInterface)
    def get_id(self):
        return to_string(self.raw_event.id)
    @overrides(EventInterface)
    def get_author_id(self):
        return to_string(self.raw_event.source) # Only return name
    @overrides(EventInterface)
    def get_author_name(self):
        return to_string(self.raw_event.source) # Only return name
    @overrides(EventInterface)
    def get_group_id(self):
        return to_string(config.bot.wechat_enterprise.CORP_ID)
    @overrides(EventInterface)
    def get_content(self) -> str:
        return to_string(self.raw_event.content)
    @overrides(EventInterface)
    def get_mentions(self):
        return [] # Not supported in wechat enterprise
    @overrides(EventInterface)
    def get_raw_event(self):
        # coupleness
        return self.raw_event