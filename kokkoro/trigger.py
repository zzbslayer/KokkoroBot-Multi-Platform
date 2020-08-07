import re
import pygtrie
from typing import List

import kokkoro
from kokkoro import util, config
from kokkoro.common_interface import BaseParameter

if config.BOT_TYPE == "discord":
    from kokkoro.discord import discord_util

class PrefixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, prefix, remain):
        super().__init__(msg)
        self.prefix=prefix
        self.remain=remain.strip()

class SuffixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, suffix, remain):
        super().__init__(msg)
        self.suffix=suffix
        self.remain=remain.strip()

class KeywordHandlerParameter(BaseParameter):
    def __init__(self, msg:str):
        super().__init__(msg)

class RegexHandlerParameter:
    def __init__(self, msg:str, match):
        super().__init__(msg)
        self.match=match

class BaseTrigger:
    
    def add(self, x, sf):
        raise NotImplementedErrorev

    def find_handler(self, ev):
        raise NotImplementedError


class PrefixTrigger(BaseTrigger):
    
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()


    def add(self, prefix: str, sf):
        if prefix in self.trie:
            other = self.trie[prefix]
            kokkoro.logger.warning(f'Failed to add prefix trigger `{prefix}`: Conflicts between {sf.__name__} and {other.__name__}')
            return
        self.trie[prefix] = sf
        kokkoro.logger.debug(f'Succeed to add prefix trigger `{prefix}`')


    def find_handler(self, ev):
        if config.BOT_TYPE=="discord":
            first_text = discord_util.remove_mention_me(ev.get_content())
        else:
            first_text = ev.get_content()

        kokkoro.logger.debug(f'Searching for Prefix Handler for {first_text}...')
        item = self.trie.longest_prefix(first_text)
        if not item:
            return None
        prefix = item.key
        kokkoro.logger.debug(f'Prefix `{prefix}` triggered')

        remain = first_text[len(prefix):].lstrip()
        ev.set_param(PrefixHandlerParameter(ev.get_content(), item.key, remain))

        return item.value

class SuffixTrigger(BaseTrigger):
    
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()


    def add(self, suffix: str, sf):
        suffix_r = suffix[::-1]
        if suffix_r in self.trie:
            other = self.trie[suffix_r]
            kokkoro.logger.warning(f'Failed to add suffix trigger `{suffix}`: Conflicts between {sf.__name__} and {other.__name__}')
            return
        self.trie[suffix_r] = sf
        kokkoro.logger.debug(f'Succeed to add suffix trigger `{suffix}`')


    def find_handler(self, ev):
        if config.BOT_TYPE=="discord":
            last_text = discord_util.remove_mention_me(ev.get_content())
        else:
            last_text = ev.get_content()
        item = self.trie.longest_prefix(last_text[::-1])
        if not item:
            return None
        
        suffix = item.key[::-1]
        remain = last_text[:-len(item.key)].rstrip()
        ev.set_param(SuffixHandlerParameter(ev.get_content(), suffix, remain))

        return item.value

class KeywordTrigger(BaseTrigger):
    
    def __init__(self):
        super().__init__()
        self.allkw = {}

    def add(self, keyword: str, sf):
        keyword = util.normalize_str(keyword)
        if keyword in self.allkw:
            other = self.allkw[keyword]
            kokkoro.logger.warning(f'Failed to add keyword trigger `{keyword}`: Conflicts between {sf.__name__} and {other.__name__}')
            return
        self.allkw[keyword] = sf
        kokkoro.logger.debug(f'Succeed to add keyword trigger `{keyword}`')


    def find_handler(self, ev):
        if config.BOT_TYPE=="discord":
            text = discord_util.remove_mention_me(ev.get_content())
        else:
            text = ev.get_content()
        for kw in self.allkw:
            if kw in text:
                ev.set_param(KeywordHandlerParameter(ev.get_content()))
                return self.allkw[kw]
        return None

class RexTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allrex = {}
    
    
    def add(self, rex: re.Pattern, sf):
        self.allrex[rex] = sf
        kokkoro.logger.debug(f'Succeed to add rex trigger `{rex.pattern}`')

    def find_handler(self, ev):
        if config.BOT_TYPE=="discord":
            text = discord_util.remove_mention_me(ev.get_content())
        else:
            text = ev.get_content()
        for rex in self.allrex:
            match = rex.search(text)
            if match:
                ev.set_param(RegexHandlerParameter(ev.get_content(), match))
                return self.allrex[rex]
        return None



prefix = PrefixTrigger()
suffix = SuffixTrigger()
keyword = KeywordTrigger()
rex = RexTrigger()

chain: List[BaseTrigger] = [
    prefix,
    suffix,
    keyword,
    rex,
]
