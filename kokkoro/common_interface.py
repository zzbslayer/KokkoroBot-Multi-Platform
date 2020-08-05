import os
from PIL import Image

import kokkoro
from kokkoro import config
from kokkoro.typing import Union, List
from kokkoro.R import ResImg, RemoteResImg

if config.BOT_TYPE == "discord":
    from kokkoro.discord import discord_util
    
SupportedMessageType = Union[ResImg, RemoteResImg, Image.Image, str]

class BaseParameter:
    def __init__(self, msg:str):
        if config.BOT_TYPE == "discord":
            self.plain_text = discord_util.remove_mention_me(msg)
        else:
            self.plain_text = msg
        self.norm_text = util.normalize_str(self.plain_text)

from kokkoro.msg_handler import handle_message
from kokkoro import config, util

class UserInterface:
    def get_id(self):
        raise NotImplementedError
    def get_name(self):
        raise NotImplementedError
    def get_raw_user(self):
        raise NotImplementedError

class EventInterface:
    def get_id(self):
        raise NotImplementedError
    def get_author_id(self):
        raise NotImplementedError
    def get_group_id(self):
        raise NotImplementedError
    def get_content(self) -> str:
        raise NotImplementedError
    def get_mentions(self) -> List[UserInterface]:
        # coupleness
        raise NotImplementedError

    def get_param(self) -> BaseParameter: 
        # Custom parameter of trigger
        raise NotImplementedError
    def get_raw_event(self):
        # coupleness
        raise NotImplementedError


# In case the name of function is the same as bot sdk client.
class KokkoroBot():
    def kkr_load_modules(self, config):
        for module_name in config.MODULES_ON:
            util.load_modules(
                os.path.join(os.path.dirname(__file__), 'modules', module_name),
                f'kokkoro.modules.{module_name}')

    def kkr_event_adaptor(self, raw_event) -> EventInterface:
        raise NotImplementedError
    
    async def kkr_send(self, ev: EventInterface, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        raise NotImplementedError

    async def kkr_on_message(self, raw_event):
        # don't respond to ourselves
        ev = self.kkr_event_adaptor(raw_event)
        if ev.get_author_id() == self.config.BOT_ID:
            return
        if ev.get_group_id() not in config.ENABLED_GUILD:
            return

        kokkoro.logger.debug(f'Receive message:{ev.get_content()}')

        await handle_message(self, ev)

    def kkr_run(self):
        raise NotImplementedError