import re
import json
import os
from functools import wraps

import kokkoro
from kokkoro.typing import *
from kokkoro import logger, KokkoroBot
from kokkoro import priv, log, typing, trigger
from kokkoro.common_interface import *

# service management
_loaded_services: Dict[str, "Service"] = {}  # {name: service}
_re_illegal_char = re.compile(r'[\\/:*?"<>|\.]')
_service_config_dir = os.path.expanduser('~/.kokkoro/service_config/')
os.makedirs(_service_config_dir, exist_ok=True)

def _load_service_config(service_name):
    config_file = os.path.join(_service_config_dir, f'{service_name}.json')
    if not os.path.exists(config_file):
        return {}  # config file not found, return default config.
    try:
        with open(config_file, encoding='utf8') as f:
            config = json.load(f)
            return config
    except Exception as e:
        logger.exception(e)
        return {}

def _save_service_config(service):
    config_file = os.path.join(_service_config_dir, f'{service.name}.json')
    with open(config_file, 'w', encoding='utf8') as f:
        json.dump(
            {
                "name": service.name,
                "use_priv": service.use_priv,
                "manage_priv": service.manage_priv,
                "enable_on_default": service.enable_on_default,
                "visible": service.visible,
                "enable_group": list(service.enable_group),
                "disable_group": list(service.disable_group)
            },
            f,
            ensure_ascii=False,
            indent=2)

class ServiceFunc:
    def __init__(self, sv: "Service", func: Callable, only_to_me: bool):
        self.sv = sv
        self.func = func
        self.only_to_me = only_to_me
        self.__name__ = func.__name__

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class Service:
    """将一组功能包装为服务, 提供增强的触发条件与分群权限管理.

    支持的触发条件:
    `on_message`,
    `on_prefix`, `on_fullmatch`, `on_suffix`,
    `on_keyword`, `on_rex`,
    `on_command`, `on_natural_language`

    提供接口：
    `scheduled_job`, `broadcast`

    服务的配置文件格式为：
    {
        "name": "ServiceName",
        "use_priv": priv.NORMAL,
        "manage_priv": priv.ADMIN,
        "enable_on_default": true/false,
        "visible": true/false,
        "enable_group": [],
        "disable_group": []
    }

    储存位置：
    `~/.kokkoro/service_config/{ServiceName}.json`
    """
    def __init__(self, name, use_priv=None, manage_priv=None, enable_on_default=None, visible=None,
                 help_=None):
        """
        定义一个服务
        配置的优先级别：配置文件 > 程序指定 > 缺省值
        """
        #assert not _re_illegal_char.search(name), r'Service name cannot contain character in `\/:*?"<>|.`'

        config = _load_service_config(name)
        self.name = name
        self.use_priv = config.get('use_priv') or use_priv or priv.NORMAL
        self.manage_priv = config.get('manage_priv') or manage_priv or priv.ADMIN
        self.enable_on_default = config.get('enable_on_default')
        if self.enable_on_default is None:
            self.enable_on_default = enable_on_default
        if self.enable_on_default is None:
            self.enable_on_default = True
        self.visible = config.get('visible')
        if self.visible is None:
            self.visible = visible
        if self.visible is None:
            self.visible = True
        self.help = help_
        self.enable_group = set(config.get('enable_group', []))
        self.disable_group = set(config.get('disable_group', []))

        self.logger = log.new_logger(name)

        assert self.name not in _loaded_services, f'Service name "{self.name}" already exist!'
        _loaded_services[self.name] = self

    @property
    def bot(self):
        return kokkoro.get_bot()
    
    @staticmethod
    def get_loaded_services() -> Dict[str, "Service"]:
        return _loaded_services
    
    def set_enable(self, group_id):
        self.enable_group.add(group_id)
        self.disable_group.discard(group_id)
        _save_service_config(self)
        self.logger.info(f'Service {self.name} is enabled at group {group_id}')

    def set_disable(self, group_id):
        self.enable_group.discard(group_id)
        self.disable_group.add(group_id)
        _save_service_config(self)
        self.logger.info(
            f'Service {self.name} is disabled at group {group_id}')

    def check_enabled(self, group_id):
        return bool( (group_id in self.enable_group) or (self.enable_on_default and group_id not in self.disable_group))


    def _check_all(self, ev: EventInterface):
        gid = ev.get_group_id()
        return self.check_enabled(gid) and not priv.check_block_group(gid) and priv.check_priv(ev.get_author(), self.use_priv)
    
    def get_enable_groups(self) -> dict:
        """获取所有启用本服务的群
        @return [group_id]
        """
        gl = defaultdict(list)
        gids = set(g.id for g in self.bot.guilds)
        if self.enable_on_default:
            gids = gids - self.disable_group
        else:
            gids = gids & self.enable_group
        return gids

    def on_prefix(self, prefix, only_to_me=False) -> Callable:
        if isinstance(prefix, str):
            prefix = (prefix, )
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me)
            for p in prefix:
                trigger.prefix.add(p, sf)
            return func
        return deco
    
    def on_fullmatch(self, word, only_to_me=False) -> Callable:
        if isinstance(word, str):
            word = (word, )
        def deco(func) -> Callable:
            @wraps(func)
            async def wrapper(bot: KokkoroBot, ev: EventInterface):
                param = ev.get_param()
                if param.remain != '':
                    self.logger.info(f'Message {ev.get_id()} is ignored by fullmatch condition.')
                    return
                return await func(bot, ev)
            sf = ServiceFunc(self, wrapper, only_to_me)
            for w in word:
                trigger.prefix.add(w, sf)
            return func
            # func itself is still func, not wrapper. wrapper is a part of trigger.
            # so that we could use multi-trigger freely, regardless of the order of decorators.
            # ```
            # """the order doesn't matter"""
            # @on_keyword(...)
            # @on_fullmatch(...)
            # async def func(...):
            #   ...
            # ```
        return deco
    
    def on_suffix(self, suffix, only_to_me=False) -> Callable:
        if isinstance(suffix, str):
            suffix = (suffix, )
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me)
            for s in suffix:
                trigger.suffix.add(s, sf)
            return func
        return deco


    def on_keyword(self, keywords, only_to_me=False) -> Callable:
        if isinstance(keywords, str):
            keywords = (keywords, )
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me)
            for kw in keywords:
                trigger.keyword.add(kw, sf)
            return func
        return deco


    def on_rex(self, rex: Union[str, re.Pattern], only_to_me=False) -> Callable:
        if isinstance(rex, str):
            rex = re.compile(rex)
        def deco(func) -> Callable:
            sf = ServiceFunc(self, func, only_to_me)
            trigger.rex.add(rex, sf)
            return func
        return deco

    async def broadcast(self, msgs, TAG='', interval_time=0.5):
        bot = self.bot
        glist = self.get_enable_groups()
        for gid in glist:
            try:
                for msg in msgs:
                    await asyncio.sleep(interval_time)
                    channels = bot.get_guild(gid).channels
                    for channel in channels:
                        if channel.name == "broadcast":
                            await bot.send_message(channel, msg)
                l = len(msgs)
                if l:
                    self.logger.info(f"群{gid} 投递{TAG}成功 共{l}条消息")
            except Exception as e:
                self.logger.error(f"群{gid} 投递{TAG}失败：{type(e)}")
                self.logger.exception(e)