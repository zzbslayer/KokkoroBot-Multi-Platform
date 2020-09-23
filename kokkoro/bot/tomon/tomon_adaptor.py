import asyncio
from kokkoro import config
from kokkoro.priv import SUPERUSER, ADMIN, NORMAL, OWNER
from kokkoro.typing import List, overrides
from kokkoro.common_interface import EventInterface, UserInterface, GroupInterface, SupportedMessageType
from kokkoro.util import to_string

from . import get_bot
from .tomon_util import has_permission_for, calculate_permission

class TomonPriv:
    ADMINISTRATOR = 1 << 3

'''
Raw User (dict)
https://developer.tomon.co/docs/guild#群组成员guild-member
'''
class TomonUser(UserInterface):
    def __init__(self, user, member={}):
        self.raw_user = user
        self.raw_member = member
        # lazy loaded var
        self.group = None
        self.roles = None

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
        res = self.raw_user.get('name', self.raw_user.get('username')) # 优先获取昵称，若无则获取用户名
        return to_string(res)
    
    @overrides(UserInterface)
    def get_raw_user(self):
        return self.raw_user
    
    @overrides(UserInterface)
    def get_nick_name(self):
        return to_string(self.raw_member.get('nick')) or self.get_name()

    @overrides(UserInterface)
    def get_priv(self):
        if self.get_id() in config.SUPER_USER:
            return SUPERUSER
        elif self.is_owner():
            return OWNER
        elif self.is_admin():
            return ADMIN
        return NORMAL

    def get_roles(self):
        if self.roles == None:
            my_roles_id = self.raw_member.get('roles') # only role id in this list
            bot = get_bot()
            all_roles = bot.get_roles_by_group(self.raw_member.get('guild_id'))

            my_roles = []
            for role in all_roles:
                for rid in my_roles_id:
                    if role["id"] == rid:
                        my_roles.append(role)
            self.roles = my_roles
        return self.roles
    
    @overrides(UserInterface)
    def is_admin(self):
        permission = calculate_permission(self.get_roles())
        return has_permission_for(permission, TomonPriv.ADMINISTRATOR)
    
    def is_owner(self):
        if self.group == None:
            guild_id = self.raw_member.get('guild_id')
            if guild_id == None:
                return False
            bot = get_bot()
            self.group = bot.get_group_by_id(guild_id)
        if self.group.get_owner_id() == self.get_id():
            return True
        return False

class TomonGroup(GroupInterface):
    def __init__(self, raw_group):
        self.raw_group = raw_group
        self.members = None

    @staticmethod
    def from_raw_groups(raw_groups):
        return [ TomonGroup(rg) for rg in raw_groups]

    @overrides(GroupInterface)
    def get_id(self):
        return self.raw_group.get('id')
    
    @overrides(GroupInterface)
    def get_name(self):
        return self.raw_group.get('name')
    
    @overrides(GroupInterface)
    def get_members(self) -> List[TomonUser]:
        _bot = get_bot().get_raw_bot()
        if self.members == None:
            self.members = asyncio.run(_bot.api().route(f'/guilds/{self.get_id()}/members').get())
        return TomonUser.from_raw_members(self.members)
    
    @overrides(GroupInterface)
    def get_owner_id(self):
        return to_string(self.raw_group.get("owner_id"))

'''
Raw Event (dict)
https://developer.tomon.co/docs/channel#消息message
'''
class TomonEvent(EventInterface):
    def __init__(self, raw_event):
        self.members_in_group = None
        self.group = None

        self._raw_event=raw_event

        # 这是不完整的 Member 信息。不包含 guild_id 等信息
        # 'member': {'nick': 'zzbslayer', 'roles': ['161137464197890048']}
        member = self._raw_event.get('member') 
        member = {} if member == None else member
        member['guild_id'] = self._raw_event.get('guild_id')
        self.author = TomonUser(self._raw_event.get('author'), member=member)

    @overrides(EventInterface)
    def get_id(self):
        return to_string(self._raw_event.get('id'))

    @overrides(EventInterface)
    def get_content(self) -> str:
        return to_string(self._raw_event.get('content'))

    @overrides(EventInterface)
    def set_content(self, msg):
        self._raw_event['content']=msg
    
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
        kkr_bot = get_bot()
        if self.members_in_group == None:
            members_in_group = kkr_bot.get_members_in_group(self.get_group_id()) # 这是完整的 Member 信息
            self.members_in_group = members_in_group
        
        return self.members_in_group

    @overrides(EventInterface)
    def get_group_id(self):
        return to_string(self._raw_event.get('guild_id'))
    
    @overrides(EventInterface)
    def get_group(self) -> GroupInterface:
        _bot = get_bot().get_raw_bot()
        if self.group == None:
            self.group = TomonGroup(asyncio.run(_bot.api().route(f'/guilds/{self.get_group_id()}').get()))
        
        return self.group

    @overrides(EventInterface)
    def get_mentions(self) -> List[TomonUser]:
        return TomonUser.from_raw_users(self._raw_event.get('mentions'))

    @overrides(EventInterface)
    def get_raw_event(self):
        return self._raw_event

    def get_channel_id(self):
        return self._raw_event.get('channel_id')
