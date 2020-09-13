import asyncio
from aiogram import types

import kokkoro
from kokkoro.common_interface import EventInterface, UserInterface, BaseParameter
from kokkoro.typing import overrides, List
from kokkoro.util import to_string
from kokkoro.priv import SUPERUSER, ADMIN, NORMAL

class TelegramUser(UserInterface):
    def __init__(self, raw_user, gid):
        self.raw_user = raw_user
        self.gid = gid
    
    @overrides(UserInterface)
    def get_id(self):
        return to_string(self.raw_user.id)
    
    @overrides(UserInterface)
    def get_name(self):
        return to_string(self.raw_user.first_name + self.raw_user.last_name)

    @overrides(UserInterface)
    def get_nick_name(self):
        return self.get_name()

    @overrides(UserInterface)
    def get_priv(self):
        if self.get_id() in kokkoro.config.SUPER_USER:
            return SUPERUSER
        elif self.is_admin():
            return ADMIN
        return NORMAL
    
    @overrides(UserInterface)
    def is_admin(self):
        from . import get_bot
        bot = get_bot()
        chat_member = asyncio.run(bot.raw_bot.get_chat_member(self.gid, self.get_id()))
        if chat_member.is_chat_admin():
            return True
        return False
    
    @overrides(UserInterface)
    def get_raw_user(self) -> types.User:
        return self.raw_user


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
    def get_author(self):
        return TelegramUser(self.raw_event.from_user, self.get_group_id())

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
    
    @overrides(EventInterface)
    def set_content(self, content):
        self.raw_event.text = content
