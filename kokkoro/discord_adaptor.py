import discord
from PIL import Image
from kokkoro.msg_handler import EventInterface
from kokkoro.trigger import BaseParameter

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

def local_image(path:str) -> DiscordImage:
    return DiscordImage(DiscordImage.LOCAL_IMAGE, path)

def remote_image(url:str, filename="image.png") -> DiscordImage:
    return DiscordImage(DiscordImage.REMOTE_IMAGE, url, filename=filename)

def pil_image(img: Image, filename="image.png") -> DiscordImage:
    return DiscordImage(DiscordImage.PIL_IMAGE, img, filename=filename)

'''
Modules should depend on EventInterface instead of Discord specific concept.
Then it would be easy to migrate to other platform.
'''
class DiscordEvent(EventInterface):
    def __init__(self, msg: discord.Message):
        self._raw_event = msg
        self.param:BaseParameter = None

    def get_id(self):
        return self._raw_event.id

    def get_author_id(self):
        return self._raw_event.author.id

    def get_group_id(self):
        return self._raw_event.guild.id

    def get_content(self) -> str:
        return self._raw_event.content

    def get_mentions(self) -> str:
        return self._raw_event.mentions

    def get_param(self): 
        return self.param

    def get_channel(self):
        return self._raw_event.channel

    def get_raw_event(self) -> discord.Message:
        return self._raw_event