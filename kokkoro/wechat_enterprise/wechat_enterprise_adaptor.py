from wechatpy.messages import BaseMessage

from kokkoro.common_interface import EventInterface
from kokkoro import config

class WechatEpEvent(EventInterface):
    def __init__(self, raw_event: BaseMessage):
        self.raw_event = raw_event

    def get_id(self):
        return self.raw_event.id
    def get_author_id(self):
        return self.raw_event.source # Only return name
    def get_group_id(self):
        return config.bot.wechat_enterprise.CORP_ID
    def get_content(self) -> str:
        return self.raw_event.content
    def get_mentions(self):
        return [] # Not supported in wechat enterprise
    def get_raw_event(self):
        # coupleness
        return self.raw_event