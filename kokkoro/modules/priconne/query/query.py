import itertools, re
from kokkoro import util, R
from kokkoro.common_interface import EventInterface
from . import sv

tw_1 = R.img('priconne/quick/r17-4-1-tw.png')
tw_2 = R.img('priconne/quick/r17-4-2-tw.png')
jp_1 = R.img('priconne/quick/r18-3-1-jp.png')
jp_2 = R.img('priconne/quick/r18-3-2-jp.png')
jp_3 = R.img('priconne/quick/r18-3-3-jp.png')
cn_1 = R.img('priconne/quick/r10-4-1-cn.jpg')
cn_2 = R.img('priconne/quick/r10-4-2-cn.jpg')
cn_3 = R.img('priconne/quick/r10-4-3-cn.jpg')


@sv.on_rex(r'^(\*?([日台国陆b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$')
async def rank_sheet(bot, ev:EventInterface):
    match = ev.get_param().match
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) and match.group(2) in '国陆b'
    if not is_jp and not is_tw and not is_cn:
        await bot.kkr_send(ev, '\n请问您要查询哪个服务器的rank表？\n*日rank表\n*台rank表\n*B服rank表\n', at_sender=True)
        return
    msg = [
        '\n※表格仅供参考，升r有风险，强化需谨慎\n※一切以会长要求为准——',
    ]
    if is_jp:
        msg.append('※不定期搬运自图中Q群\n※广告为原作者推广，与本bot无关\nrank表：')
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
        pos = match.group(3)
        if not pos or '前' in pos:
            await bot.kkr_send(ev, jp_1)
        if not pos or '中' in pos:
            await bot.kkr_send(ev, jp_2)
        if not pos or '后' in pos:
            await bot.kkr_send(ev, jp_3)
        
    elif is_tw:
        msg.append(f'※不定期搬运自漪夢奈特\n※油管频道有介绍视频及原文档\nrank表：\n')
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
        await bot.kkr_send(ev, tw_1)
        await bot.kkr_send(ev, tw_2)
    elif is_cn:
        await bot.kkr_send(ev, '\n'.join(msg), at_sender=True)
        await bot.kkr_send(ev, cn_1)
        await bot.kkr_send(ev, cn_2)
        await bot.kkr_send(ev, cn_3)

@sv.on_fullmatch(('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'jjc数据库'))
async def say_arina_database(bot, ev):
    await bot.kkr_send(ev, '公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


OTHER_KEYWORDS = '【日rank】【台rank】【b服rank】【jjc作业网】【黄骑充电表】【一个顶俩】'
PCR_SITES = f'''
【繁中wiki/兰德索尔图书馆】pcredivewiki.tw
【日文wiki/GameWith】gamewith.jp/pricone-re
【日文wiki/AppMedia】appmedia.jp/priconne-redive
【竞技场作业库(中文)】pcrdfans.com/battle
【竞技场作业库(日文)】nomae.net/arenadb
【论坛/NGA社区】bbs.nga.cn/thread.php?fid=-10308342
【iOS实用工具/初音笔记】bbs.nga.cn/read.php?tid=14878762
【安卓实用工具/静流笔记】bbs.nga.cn/read.php?tid=20499613
【台服卡池千里眼】bbs.nga.cn/read.php?tid=16986067
【日官网】priconne-redive.jp
【台官网】www.princessconnect.so-net.tw

===其他查询关键词===
{OTHER_KEYWORDS}
※B服速查请输入【bcr速查】'''

BCR_SITES = f'''
【妈宝骑士攻略(懒人攻略合集)】bbs.nga.cn/read.php?tid=20980776
【机制详解】bbs.nga.cn/read.php?tid=19104807
【初始推荐】bbs.nga.cn/read.php?tid=20789582
【术语黑话】bbs.nga.cn/read.php?tid=18422680
【角色点评】bbs.nga.cn/read.php?tid=20804052
【秘石规划】bbs.nga.cn/read.php?tid=20101864
【卡池亿里眼】bbs.nga.cn/read.php?tid=20816796
【为何卡R卡星】bbs.nga.cn/read.php?tid=20732035
【推图阵容推荐】bbs.nga.cn/read.php?tid=21010038

===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''

@sv.on_fullmatch(('pcr速查', 'pcr图书馆', '图书馆', 'pcr-sites'))
async def pcr_sites(bot, ev: EventInterface):
    await bot.kkr_send(ev, PCR_SITES, at_sender=True)
@sv.on_fullmatch(('bcr速查', 'bcr攻略', 'bcr-sites'))
async def bcr_sites(bot, ev: EventInterface):
    await bot.kkr_send(ev, BCR_SITES, at_sender=True)


YUKARI_SHEET_ALIAS = util.join_iterable(('黄骑', '酒鬼', '黃騎'), ('充电', '充电表', '充能', '充能表')) + ('yukari-sheet',)
YUKARI_SHEET = f'''
※大圈是1动充电对象 PvP测试
※黄骑四号位例外较多
※对面羊驼或中后卫坦 有可能歪
※我方羊驼算一号位
※图片搬运自漪夢奈特'''
@sv.on_fullmatch(YUKARI_SHEET_ALIAS)
async def yukari_sheet(bot, ev):
    await bot.kkr_send(ev, R.img('priconne/quick/黄骑充电.jpg'))
    await bot.kkr_send(ev, YUKARI_SHEET, at_sender=True)

NORMAL_MAP_PREFIX='刷图'
@sv.on_prefix(('刷图','刷图指南', '刷装备', '装备掉落', '刷图攻略'))
async def normal_map(bot, ev: EventInterface):
    try:
        number = int(ev.get_param().remain)
    except Exception as e:
        await bot.kkr_send(ev, '参数必须为数字。示例：`刷图 10`')
        return

    img = f'{NORMAL_MAP_PREFIX}-{number}.jpg'
    img = R.img(f'priconne/quick/{img}')
    if not img.exist:
        await bot.kkr_send(ev, f'{number} 图刷图攻略未找到呜呜呜 ┭┮﹏┭┮')
    else:
        await bot.kkr_send(ev, f'{number} 图刷图攻略：')
        await bot.kkr_send(ev, img)
