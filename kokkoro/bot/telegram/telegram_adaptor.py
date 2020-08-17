from aiogram import types
from kokkoro.common_interface import EventInterface, UserInterface, BaseParameter
from kokkoro.typing import overrides, List
from kokkoro.util import to_string

class TelegramEvent(EventInterface):
    def __init__(self, raw_event: types.Message):
        self.raw_event = raw_event

    @overrides(EventInterface)
    def get_id(self):
        return to_string(self.raw_event.message_id)

    @overrides(EventInterface)
    def get_author_id(self):
        return to_string(self.raw_event.from_user.id)
    
    @overrides(EventInterface)
    def get_author_name(self):
        return to_string(self.raw_event.from_user.username)

    @overrides(EventInterface)
    def get_group_id(self):
        return to_string(self.raw_event.chat.id)

    @overrides(EventInterface)
    def get_content(self) -> str:
        return to_string(self.raw_event.text)

    @overrides(EventInterface)
    def get_mentions(self) -> List[UserInterface]:
        # TODO: MessageEntity
        return []

    @overrides(EventInterface)
    def get_raw_event(self) -> types.Message:
        # coupleness
        return self.raw_event
