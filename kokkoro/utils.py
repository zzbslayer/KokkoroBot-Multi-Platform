import discord
from kokkoro import config

def only_to_me(msg: discord.Message) -> bool:
    members = msg.mentions
    if len(members) != 1:
        return False
    if str(members[0]) == config.BOT_NAME:
        return True
    return False