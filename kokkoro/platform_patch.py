from kokkoro import config

def preprocess_message(ev):
    if config.BOT_TYPE == "discord":
        from kokkoro.bot.discord.discord_util import remove_mention_me, normalize_message
        dc_msg = ev.get_raw_event()
        new_content = dc_msg.content
        new_content = remove_mention_me(new_content)
        new_content = normalize_message(new_content)
        dc_msg.content = new_content
