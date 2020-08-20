from .weibo import WeiboSpider
import kokkoro
from kokkoro.service import Service, BroadcastTag
from kokkoro.common_interface import KokkoroBot, EventInterface
from kokkoro import priv
from kokkoro import R, util
from .exception import *

lmt = util.FreqLimiter(5)
sv = Service('weibo-poller', manage_priv=priv.SUPERUSER, visible=False)

def _load_config(services_config):
    for sv_config in services_config:
        sv.logger.debug(sv_config)
        service_name = sv_config["service_name"]
        enable_on_default = sv_config.get("enable_on_default", False)
        broadcast_tag = sv_config.get("broadcast_tag", None)

        users_config = sv_config["users"]

        sv_spider_list = []
        for user_config in users_config:
            wb_spider = WeiboSpider(user_config)
            sv_spider_list.append(wb_spider)
            alias_list = user_config.get("alias", [])
            for alias in alias_list:
                if alias in alias_dic:
                    raise DuplicateError(f"Alias {alias} is duplicate")
                alias_dic[alias] = {
                    "service_name":service_name, 
                    "user_id":wb_spider.get_user_id()
                    }
        
        subService = Service(service_name, enable_on_default=enable_on_default)
        subr_dic[service_name] = {"service": subService, "spiders": sv_spider_list, "broadcast_tag":BroadcastTag.parse(broadcast_tag)}
  
services_config = kokkoro.config.modules.weibo.weibos
subr_dic = {}
alias_dic = {}
_load_config(services_config)

def wb_to_message(wb):
    msg = f'@{wb["screen_name"]}'
    if "retweet" in wb:
        msg = f'{msg} 转发:\n{wb["text"]}\n======================'
        wb = wb["retweet"]
    else:
        msg = f'{msg}:'

    msg = f'{msg}\n{wb["text"]}'

    imgs = []
    if kokkoro.config.ENABLE_IMAGE and len(wb["pics"]) > 0:
        images_url = wb["pics"]
        msg = f'{msg}\n'
        imgs = [R.remote_img(url) for url in images_url]
    if len(wb["video_url"]) > 0:
        videos = wb["video_url"]
        res_videos = ';'.join(videos)
        msg = f'{msg}\n视频链接：{res_videos}'

    return msg, imgs

weibo_url_prefix = "https://weibo.com/u"
@sv.on_fullmatch(('weibo-config', '查看微博服务', '微博服务', '微博配置', '查看微博配置'))
async def weibo_config(bot, ev):
    msg = '微博推送配置：服务名，别名，微博链接, 推送标签'
    index = 1
    for service_config in services_config:
        service_name = service_config['service_name']
        bc_tag = service_config['broadcast_tag']
        users_config = service_config['users']
        for user_config in users_config:
            weibo_id =  user_config['user_id']
            alias = user_config['alias']
            weibo_url = f'{weibo_url_prefix}/{weibo_id}'
            msg = f'{msg}\n{index}. {service_name}, {alias}, {weibo_url}, {bc_tag}'
            index+=1
    await bot.kkr_send(ev, msg)


# @bot 看微博 alias
@sv.on_prefix('看微博')
async def get_last_5_weibo(bot: KokkoroBot, ev: EventInterface):
    uid = ev.get_author_id()
    if not lmt.check(uid):
        await bot.kkr_send(ev, '您查询得过于频繁，请稍等片刻', at_sender=True)
        return

    lmt.start_cd(uid)

    params = ev.get_param().remain.split(' ')
    if len(params) == 0 or params[0] == '':
        await bot.kkr_send(ev, f'使用方法：看微博 <微博别称> <1-5的数字>\n仅支持主动查看最新5条微博~')
        return
    alias = params[0]
    if len(params) == 1:
        amount = 5
    else:
        try:
            amount = int(params[1])
        except Exception as e:
            await bot.kkr_send(ev, f'使用方法：看微博  {alias} <1-5的数字>\n仅支持主动查看最新5条微博~')
            return
        if amount >= 5 or amount <= 0:
            amount = 5

    if alias not in alias_dic:
        await bot.kkr_send(ev, f"未找到微博: {alias}")
        return

    service_name = alias_dic[alias]["service_name"]
    user_id = alias_dic[alias]["user_id"]

    spiders = subr_dic[service_name]["spiders"]
    for spider in spiders:
        if spider.get_user_id() == user_id:
            last_5_weibos = spider.get_last_5_weibos()
            weibos = last_5_weibos[-amount:]
            formatted_weibos = [wb_to_message(wb) for wb in weibos]
            for wb in formatted_weibos:
                await bot.kkr_send(ev, wb[0]) # send text
                imgs = wb[1]
                for img in imgs:
                    await bot.kkr_send(ev, img) # send img
                await bot.kkr_send(ev, "===================================")
            await bot.kkr_send(ev, f"以上为 {alias} 的最新 {len(formatted_weibos)} 条微博")
            return
    await bot.kkr_send(ev, f"未找到微博: {alias}")

@sv.scheduled_job('cron', minute='*/20', jitter=20)
async def weibo_poller():
    for sv_name, serviceObj in subr_dic.items():
        weibos = []
        ssv = serviceObj["service"]
        spiders = serviceObj["spiders"]
        bc_tag = serviceObj["broadcast_tag"]
        for spider in spiders:
            latest_weibos = await spider.get_latest_weibos()
            formatted_weibos = [wb_to_message(wb) for wb in latest_weibos]

            if l := len(formatted_weibos):
                sv.logger.info(f"成功获取@{spider.get_username()}的新微博{l}条")
            else:
                sv.logger.info(f"未检测到@{spider.get_username()}的新微博")

            weibos.extend(formatted_weibos)
        for wb in weibos:
            await ssv.broadcast(wb[0], bc_tag)
            imgs = wb[1]
            for img in imgs:
                await ssv.broadcast(img, bc_tag)

@sv.scheduled_job('cron', second='0', minute='0', hour='5')
async def clear_spider_buffer():
    sv.logger.info("Cleaning weibo spider buffer...")
    for sv_name, serviceObj in subr_dic.items():
        spiders = serviceObj["spiders"]
        for spider in spiders:
            spider.clear_buffer()