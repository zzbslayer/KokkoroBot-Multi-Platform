import re

from kokkoro import config

def at(uid):
    return f"<@{uid}>"

MENTION_BOT = at(config.BOT_ID)

def remove_mention_me(raw_message) -> str:
    if (raw_message.startswith(MENTION_BOT)):
        return raw_message.replace(MENTION_BOT, "").strip()
    return raw_message

tomon_at_pattern = r'<@[a-z0-9A-Z]+>'
def normalize_message(raw_message: str) -> str:
    """
    规范化 at 信息，"<@123> waht<@312>a12" => "@123 waht @312 a12"
    """
    raw_ats = re.findall(dc_at_pattern, raw_message)
    for rat in raw_ats:
        raw_message = raw_message.replace(rat, normalize_at(rat))
    return raw_message.strip()

def normalize_at(raw_at):
    """
    规范化 at 信息，"<@123>" => " @123 "
    """
    return f' @{raw_at[2:-1]} '