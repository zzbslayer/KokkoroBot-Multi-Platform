import re
import pygtrie
import discord

import kokkoro
class PrefixHandlerParameter:
    def __init__(self, prefix, remain):
        self.prefix=prefix
        self.remain=remain

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
        param = PrefixHandlerParameter(item.key, remain)

        return item.value, param



prefix = PrefixTrigger()

chain = [
    prefix,
]
