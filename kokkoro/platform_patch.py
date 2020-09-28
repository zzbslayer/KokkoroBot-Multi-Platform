import kokkoro
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

PLATFORM_FIELD = '__kkr_platform__'

def discord(func):
    func.__setattr__(PLATFORM_FIELD, ['discord'])
    return func

def tomon(func):
    func.__setattr__(PLATFORM_FIELD, ['tomon'])
    return func

def telegram(func):
    func.__setattr__(PLATFORM_FIELD, ['telegram'])
    return func

def platform(pl):
    if type(pl) == str:
        pl = [pl]
    def deco(func):
        func.__setattr__(PLATFORM_FIELD, pl)
        return func
    return deco

def is_supported(func):
    try:
        supported_platforms = func.__getattribute__(PLATFORM_FIELD)
    except AttributeError as e:
        #supported_platforms = "*"
        return True
    platform = config.BOT_TYPE
    if platform in supported_platforms:
        return True
    return False

def check_platform(on_deco):
    def wrapper(sv_func):
        if is_supported(sv_func):
            return on_deco(sv_func)
        else:
            kokkoro.logger.warning(f'`{sv_func.__name__}` isn\'t supported in current platform')
            return sv_func
    return wrapper


    