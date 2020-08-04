import re
import pygtrie
import discord

import kokkoro
from kokkoro import util

class BaseParameter:
    def __init__(self, msg:str):
        self.plain_text = msg.strip()
        self.norm_text = util.normalize_str(self.plain_text)

class PrefixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, prefix, remain):
        super().__init__(msg)
        self.prefix=prefix
        self.remain=remain

class SuffixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, suffix, remain):
        super().__init__(msg)
        self.suffix=prefix
        self.remain=suffix

class KeywordHandlerParameter(BaseParameter):
    def __init__(self, msg:str):
        super().__init__(msg)

class RegexHandlerParameter:
    def __init__(self, msg:str, match):
        super().__init__(msg)
        self.match=match

class BaseTrigger:
    
    def add(self, x, sf: "ServiceFunc"):
        raise NotImplementedError

    def find_handler(self, msg: discord.Message) -> "ServiceFunc":
        raise NotImplementedError


class PrefixTrigger(BaseTrigger):
    
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()


    def add(self, prefix: str, sf: "ServiceFunc"):
        if prefix in self.trie:
            other = self.trie[prefix]
            kokkoro.logger.warning(f'Failed to add prefix trigger `{prefix}`: Conflicts between {sf.__name__} and {other.__name__}')
            return
        self.trie[prefix] = sf
        kokkoro.logger.debug(f'Succeed to add prefix trigger `{prefix}`')


    def find_handler(self, msg: discord.Message):
        first_text = msg.content
        kokkoro.logger.debug(f'Searching for Prefix Handler for {first_text}...')
        item = self.trie.longest_prefix(first_text)
        if not item:
            return None, None
        prefix = item.key
        kokkoro.logger.debug(f'Prefix `{prefix}` triggered')

        remain = first_text[len(prefix):].lstrip()
        param = PrefixHandlerParameter(msg.content, item.key, remain)

        return item.value, param

class SuffixTrigger(BaseTrigger):
    
    def __init__(self):
        super().__init__()
        self.trie = pygtrie.CharTrie()


    def add(self, suffix: str, sf: "ServiceFunc"):
        suffix_r = suffix[::-1]
        if suffix_r in self.trie:
            other = self.trie[suffix_r]
            kokkoro.logger.warning(f'Failed to add suffix trigger `{suffix}`: Conflicts between {sf.__name__} and {other.__name__}')
            return
        self.trie[suffix_r] = sf
        kokkoro.logger.debug(f'Succeed to add suffix trigger `{suffix}`')


    def find_handler(self, msg: discord.Message):
        last_text = msg.content
        item = self.trie.longest_prefix(last_text[::-1])
        if not item:
            return None, None
        
        suffix = item.key[::-1]
        remain = last_text[:-len(item.key)].rstrip()
        param = SuffixHandlerParameter(msg.content, suffix, remain)

        return item.value, param

class KeywordTrigger(BaseTrigger):
    
    def __init__(self):
        super().__init__()
        self.allkw = {}

    def add(self, keyword: str, sf: "ServiceFunc"):
        keyword = util.normalize_str(keyword)
        if keyword in self.allkw:
            other = self.allkw[keyword]
            kokkoro.logger.warning(f'Failed to add keyword trigger `{keyword}`: Conflicts between {sf.__name__} and {other.__name__}')
            return
        self.allkw[keyword] = sf
        kokkoro.logger.debug(f'Succeed to add keyword trigger `{keyword}`')


    def find_handler(self, msg: discord.Message) -> "ServiceFunc":
        text = msg.content
        for kw in self.allkw:
            if kw in text:
                param = KeywordHandlerParameter(msg.content)
                return self.allkw[kw], param
        return None, None

class RexTrigger(BaseTrigger):
    def __init__(self):
        super().__init__()
        self.allrex = {}
    
    
    def add(self, rex: re.Pattern, sf: "ServiceFunc"):
        self.allrex[rex] = sf
        kokkoro.logger.debug(f'Succeed to add rex trigger `{rex.pattern}`')

    def find_handler(self, msg: discord.Message) -> "ServiceFunc":
        text = msg.content
        for rex in self.allrex:
            match = rex.search(text)
            if match:
                param = RegexHandlerParameter(msg.content, match)
                return self.allrex[rex], param
        return None, None



prefix = PrefixTrigger()
suffix = SuffixTrigger()
keyword = KeywordTrigger()
rex = RexTrigger()

chain = [
    prefix,
    suffix,
    keyword,
    rex,
]
