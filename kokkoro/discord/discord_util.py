from kokkoro import config

MENTION_BOT = f"<@!{config.BOT_ID}>"
def remove_mention_me(raw_message) -> str:
    if (raw_message.startswith(MENTION_BOT)):
        return raw_message.replace(MENTION_BOT, "").strip()
    return raw_message