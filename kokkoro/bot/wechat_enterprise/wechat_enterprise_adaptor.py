from wechatpy.messages import BaseMessage

from kokkoro.common_interface import EventInterface
from kokkoro import config

class WechatEpEvent(EventInterface):
    def __init__(self, raw_event: BaseMessage):
        self.raw_event = raw_event

    @overrides(EventInterface)
    def get_id(self):
        return str(self.raw_event.id)
    @overrides(EventInterface)
    def get_author_id(self):
        return str(self.raw_event.source) # Only return name
    @overrides(EventInterface)
    def get_author_name(self):
        return str(self.raw_event.source) # Only return name
    @overrides(EventInterface)
    def get_group_id(self):
        return str(config.bot.wechat_enterprise.CORP_ID)
    @overrides(EventInterface)
    def get_content(self) -> str:
        return str(self.raw_event.content)
    @overrides(EventInterface)
    def get_mentions(self):
        return [] # Not supported in wechat enterprise
    @overrides(EventInterface)
    def get_raw_event(self):
        # coupleness
        return self.raw_event