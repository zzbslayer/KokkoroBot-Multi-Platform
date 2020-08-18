import asyncio
from kokkoro import config
from kokkoro.priv import SUPERUSER, ADMIN, NORMAL

from kokkoro.bot.tomon import get_bot
from kokkoro.typing import List, overrides
from kokkoro.common_interface import EventInterface, UserInterface, SupportedMessageType
from kokkoro.util import to_string

'''
Raw User (dict)
https://developer.tomon.co/docs/guild#群组成员guild-member
'''
class TomonUser(UserInterface):
    def __init__(self, user, member={}):
        self.raw_user = user
        self.raw_member = member

    @staticmethod
    def from_raw_member(member):
        return TomonUser(member.get('user'), member)
    
    @staticmethod
    def from_raw_members(members):
        return [ TomonUser.from_raw_member(member) for member in members]

    @staticmethod
    def from_raw_users(users: List):
        return [ TomonUser(user) for user in users]

    @overrides(UserInterface)
    def get_id(self):
        return to_string(self.raw_user.get('id'))

    @overrides(UserInterface)
    def get_name(self):
        return to_string(self.raw_user.get('username'))
    
    @overrides(UserInterface)
    def get_raw_user(self):
        return self.raw_user
    
    @overrides(UserInterface)
    def get_nick_name(self):
        return to_string(self.raw_member.get('nick'))

    def get_roles(self):
        return self.raw_member.get('roles')
    
    @overrides(UserInterface)
    def get_priv(self):
        if self.get_id() in config.SUPER_USER:
            return SUPERUSER
        elif self.is_admin():
            return ADMIN
        return NORMAL

    @overrides(UserInterface)
    def is_admin(self):
        return False #self.raw_user.roles
'''
Raw Event (dict)
https://developer.tomon.co/docs/channel#消息message
'''
class TomonEvent(EventInterface):
    def __init__(self, raw_event):
        self.members_in_group = None
        self._raw_event=raw_event
        member = self._raw_event.get('member') 
        member = {} if member == None else member
        self.author = TomonUser(self._raw_event.get('author'), member=member)

    @overrides(EventInterface)
    def get_id(self):
        return to_string(self._raw_event.get('id'))

    @overrides(EventInterface)
    def get_content(self) -> str:
        return to_string(self._raw_event.get('content'))
    
    @overrides(EventInterface)
    def get_author(self):
        return self.author

    @overrides(EventInterface)
    def get_author_id(self):
        return to_string(self._raw_event.get('author').get('id'))
    
    @overrides(EventInterface)
    def get_author_name(self):
        return to_string(self._raw_event.get('author').get('username'))
   
    @overrides(EventInterface)
    def get_members_in_group(self) -> List[TomonUser]:
        _bot = get_bot().get_raw_bot()
        if self.members_in_group == None:
            self.members_in_group = asyncio.run(_bot.api().route(f'/guilds/{self.get_group_id()}/members').get())
        
        return TomonUser.from_raw_members(self.members_in_group)

    @overrides(EventInterface)
    def get_group_id(self):
        return to_string(self._raw_event.get('guild_id'))

    @overrides(EventInterface)
    def get_mentions(self) -> List[TomonUser]:
        return TomonUser.from_raw_users(self._raw_event.get('mentions'))

    @overrides(EventInterface)
    def get_raw_event(self):
        return self._raw_event

    def get_channel_id(self):
        return self._raw_event.get('channel_id')
