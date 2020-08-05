import discord
import os
from PIL import Image
from typing import Union

import kokkoro
from kokkoro.common_interface import EventInterface, UserInterface, BaseParameter
from kokkoro.R import ResImg, RemoteResImg
from kokkoro.typing import overrides, List

'''
Adaptor to convert ResImg to DiscordImage.
Modules should depend on the ResImg or Adaptor
'''
class DiscordImage:
    LOCAL_IMAGE = 1
    REMOTE_IMAGE = 2
    PIL_IMAGE = 3

    def __init__(self, img_type, img, filename="image.png"):
        self.type = img_type
        self.img = img # path or url or pil image
        self.filename = filename

def _local_image(path:str) -> DiscordImage:
    return DiscordImage(DiscordImage.LOCAL_IMAGE, path)

def _remote_image(url:str, filename="image.png") -> DiscordImage:
    return DiscordImage(DiscordImage.REMOTE_IMAGE, url, filename=filename)

def _pil_image(img: Image, filename="image.png") -> DiscordImage:
    return DiscordImage(DiscordImage.PIL_IMAGE, img, filename=filename)

def message_adaptor(res: Union[ResImg, RemoteResImg, Image.Image, str], filename="image.png") -> DiscordImage:
    if isinstance(res, ResImg):
        if kokkoro.config.RES_PROTOCOL == 'http':
            return _remote_image(res.url, filename=filename)
        elif kokkoro.config.RES_PROTOCOL == 'file':
            return _local_image(os.path.abspath(res.path))
    elif isinstance(res, RemoteResImg):
        return _remote_image(res.url, filename=filename)
    elif isinstance(res, Image.Image):
        return _pil_image(res, filename=filename)
    elif isinstance(res, str):
        return res

    raise NotImplementedError

'''
Modules should depend on Interface instead of Discord specific concept.
Then it would be easy to migrate to other platform.
'''
class DiscordUser(UserInterface):
    def __init__(self, user: discord.User):
        self.raw_user = user

    @staticmethod
    def from_raw_users(users: List[discord.User]):
        return [ DiscordUser(user) for user in users]

    @overrides(UserInterface)
    def get_id(self):
        return self.raw_user.id

    @overrides(UserInterface)
    def get_name(self):
        return self.raw_user.name
    
    @overrides(UserInterface)
    def get_raw_user(self):
        return self.raw_user

class DiscordEvent(EventInterface):
    def __init__(self, msg: discord.Message):
        self._raw_event = msg
        self.param:BaseParameter = None

    @overrides(EventInterface)
    def get_id(self):
        return self._raw_event.id

    @overrides(EventInterface)
    def get_author_id(self):
        return self._raw_event.author.id

    @overrides(EventInterface)
    def get_group_id(self):
        return self._raw_event.guild.id

    @overrides(EventInterface)
    def get_content(self) -> str:
        return self._raw_event.content

    @overrides(EventInterface)
    def get_mentions(self) -> List[DiscordUser]:
        return DiscordUser.from_raw_users(self._raw_event.mentions)

    @overrides(EventInterface)
    def get_param(self): 
        return self.param

    @overrides(EventInterface)
    def get_raw_event(self) -> discord.Message:
        return self._raw_event
    
    def get_channel(self):
        return self._raw_event.channel