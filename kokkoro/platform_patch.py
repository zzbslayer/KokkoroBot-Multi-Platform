from kokkoro import config

def process_mention_me(raw_msg:str):
    to_me1 = False
    processed_msg = raw_msg
    for nick in config.NICK_NAME:
        if processed_msg.startswith(nick):
            processed_msg = processed_msg[len(nick):] # remove nick
            to_me1 = True
            break
    #to_me2 = False
    if config.BOT_TYPE == "discord":
        from kokkoro.bot.discord.discord_util import remove_mention_me, normalize_message
        processed_msg, to_me2 = remove_mention_me(processed_msg)
        processed_msg = normalize_message(processed_msg)
    elif config.BOT_TYPE == "tomon":
        from kokkoro.bot.tomon.tomon_util import remove_mention_me, normalize_message
        processed_msg, to_me2 = remove_mention_me(processed_msg)
        processed_msg = normalize_message(processed_msg)
    return processed_msg, to_me1 or to_me2

def preprocess_message(ev) -> bool:
    raw_msg = ev.get_content()
    processed_msg, to_me = process_mention_me(raw_msg)
    ev.set_content(processed_msg)
    return to_me



    