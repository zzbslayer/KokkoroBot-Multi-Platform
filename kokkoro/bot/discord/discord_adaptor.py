import discord
from discord import User, Message
from discord.permissions import Permissions
import os
from PIL import Image
from typing import Union

import kokkoro
from kokkoro import config
from kokkoro.util import to_string
from kokkoro.priv import SUPERUSER, ADMIN, NORMAL
from kokkoro.common_interface import EventInterface, UserInterface, GroupInterface
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.typing import overrides, List

'''
Modules should depend on Interface instead of Discord specific concept.
Then it would be easy to migrate to other platform.
'''

class DiscordUser(UserInterface):
    def __init__(self, user: User):
        self.raw_user = user

    @staticmethod
    def from_raw_users(users: List[User]):
        return [ DiscordUser(user) for user in users]

    @overrides(UserInterface)
    def get_id(self):
        return to_string(self.raw_user.id)

    @overrides(UserInterface)
    def get_name(self):
        return to_string(self.raw_user.name)
    
    @overrides(UserInterface)
    def get_raw_user(self) -> User:
        return self.raw_user
    
    @overrides(UserInterface)
    def get_nick_name(self):
        return to_string(self.raw_user.nick)
    
    @overrides(UserInterface)
    def get_priv(self):
        if self.get_id() in config.SUPER_USER:
            return SUPERUSER
        elif self.is_admin():
            return ADMIN
        return NORMAL

    @overrides(UserInterface)
    def is_admin(self):
        return self.raw_user.guild_permissions == Permissions.all()

class DiscordGroup(GroupInterface):
    def __init__(self, raw_group):
        self.raw_group=raw_group

    @staticmethod
    def from_raw_groups(rgs):
        return [DiscordGroup(rg) for rg in rgs]

    @overrides(GroupInterface)
    def get_id(self):
        return to_string(self.raw_group.id)

    @overrides(GroupInterface)
    def get_name(self):
        return to_string(self.raw_group.name)

    @overrides(GroupInterface)
    def get_members(self):
        return DiscordUser.from_raw_users(self.raw_group.members)



class DiscordEvent(EventInterface):
    def __init__(self, msg: Message):
        self._raw_event = msg
        self.author = DiscordUser(self._raw_event.author)

    @overrides(EventInterface)
    def get_id(self):
        return to_string(self._raw_event.id)

    @overrides(EventInterface)
    def get_author_id(self):
        return to_string(self._raw_event.author.id)
    
    @overrides(EventInterface)
    def get_author_name(self):
        return to_string(self._raw_event.author.name)
    
    @overrides(EventInterface)
    def get_author(self):
        return self.author

    @overrides(EventInterface)
    def get_members_in_group(self) -> List[DiscordUser]:
        return DiscordUser.from_raw_users(self._raw_event.guild.members)

    @overrides(EventInterface)
    def get_group_id(self):
        return to_string(self._raw_event.guild.id)
    
    @overrides(EventInterface)
    def get_group(self) -> GroupInterface:
        return DiscordGroup(self._raw_event.guild)

    @overrides(EventInterface)
    def get_content(self) -> str:
        return to_string(self._raw_event.content)

    @overrides(EventInterface)
    def get_mentions(self) -> List[DiscordUser]:
        return DiscordUser.from_raw_users(self._raw_event.mentions)

    @overrides(EventInterface)
    def get_raw_event(self) -> Message:
        return self._raw_event
    
    def get_channel(self):
        return self._raw_event.channel