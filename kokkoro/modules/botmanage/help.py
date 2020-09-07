import itertools

from kokkoro import priv
from kokkoro.service import Service
from kokkoro.common_interface import EventInterface
from kokkoro.util import join_iterable

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

HELP_HEADER='''
=====================
- KokkoroBot使用说明 -
=====================
发送方括号[]内的关键词即可触发
※功能采取模块化管理，管理员可控制开关
※部分未实装功能以符号 ※ 开头
'''.strip()

HELP_BOTTOM='''
※※KokkoroBot是基于HoshinoBot开发的跨平台bot
※※可以从github下载源码自行搭建部署，欢迎star&pr
※※https://github.com/zzbslayer/KokkoroBot-Multi-Platform
'''.strip()

PRC_HELP = '''
==================
- 公主连结Re:Dive -
==================
-      娱乐      -
==================
[@bot 签到] 给主さま盖章章
[@bot 单抽] 单抽转蛋模拟
[@bot 来发十连] 十连转蛋模拟
[@bot 来一井] 4w5钻！买定离手！
[查看卡池] 模拟卡池&出率
[切换卡池] 更换模拟卡池
[赛马]兰德索尔赛🐎大赛
[猜头像] 猜猜库唔似撒
[ag 可可萝] 猜头像回答
[头像提示] 猜头像提示信息
[头像答案] 公布猜头像答案
[猜角色] 猜猜库唔似撒
[dg 可可萝] 猜角色回答
[角色提示] 猜描述提示信息
[角色答案] 公布猜角色答案
[切噜一下] 后以空格隔开接想要转换为切噜语的话
[切噜～♪切啰巴切拉切蹦切蹦] 切噜语翻译
[@bot 官漫132] 官方四格阅览
[@bot 看微博 公主连结] 官方微博阅览（仅限最近5条）
==================
-      查询      -
==================
[怎么拆 妹弓] 后以空格隔开接角色名，查询竞技场解法
[pcr速查] 常用网址/速查表
[bcr速查] B服萌新攻略
[rank表] 查看rank推荐表
[黄骑充电表] 查询黄骑1动充电规律
[挖矿 15001] 查询矿场中还剩多少钻
[角色计算 2 100] 查询角色升级所需的经验药水与mana
[国/日服日程表] 查看活动日程表
[国/台服新闻] 查看新闻
==================
-      推送      -
==================
[启用/禁用 pcr-comic] 官方漫画推送（日文）
[启用/禁用 pcr-arena-reminder-utc9] 背刺时间提醒(日服)
[启用/禁用 pcr-arena-reminder-utc8] 背刺时间提醒(国服台服)
[启用/禁用 pcr-portion-reminder-utc9] 提醒买药小助手(日服)
[启用/禁用 pcr-portion-reminder-utc8] 提醒买药小助手(国服台服)
[启用/禁用 weibo-pcr] 国服官微推送
==================
-      会战      -
==================
[！帮助] 查看会战管理功能的说明
'''.strip()

ARKNIGHTS_HELP='''
=====================
- 明日方舟 Arknights -
=====================
[公开招募 位移 近战位] 公开招募模拟器
[公招TAG] 公开招募TAG一览
[启用/禁用 weibo-ark] 国服官微推送
'''.strip()

PUSH_HELP='''
===========
- 推送服务 -
===========
[微博配置] 查看微博推送服务的配置
[@bot 看微博 公主连结 3] 根据别名阅览指定账户最近的微博（仅限最近5条）
[pcr-comic get-bc-tag] 获取推送服务的频道标签
[weibo-pcr set-bc-tag 国服推送] 设置推送服务的频道标签（管理员限定）
'''.strip()

NORMAL_HELP='''
===========
- 通用功能 -
===========
[启用/禁用 antiqks] 识破骑空士的阴谋
※[启用/禁用 bangumi] 开启番剧更新推送
※[@bot 来点新番] 查看最近的更新(↑需开启番剧更新推送↑)
※[倒放<gif图片>] 倒放gif(需开启gif-reverter)
※[搜无损 关键词] 搜索无损acg音乐
[.r] 掷骰子
[.r 3d12] 掷3次12面骰子
[生成表情 <表情名> <文字>] 表情包生成器
[表情列表] 列出可生成的表情名称
※[@bot 精致睡眠] 8小时精致睡眠(bot需具有群管理权限)
※[给我来一份精致昏睡下午茶套餐] 叫一杯先辈特调红茶(bot需具有群管理权限)
'''.strip()

SHORT_HELP=f'''
{HELP_HEADER}
====================
[公主连结帮助]查看公主连结相关功能
[！帮助] 查看公主连结会战管理功能的说明
[明日方舟帮助]查看明日方舟相关功能
[通用功能]查看通用功能
[推送帮助]查看推送服务
=====管理限定功能=====
[lssv] 查看功能模块的开关状态
[lsbcsv] 查看推送服务的开关状态与标签
[enable <服务名>] 开启指定服务
[disable <服务名>] 关闭指定服务
====================
{HELP_BOTTOM}
'''.strip()

_pcr=['公主连结', '公主链接', '公主连接', 'pcr', 'bcr']
_help=['帮助', 'help']
@sv.on_fullmatch(join_iterable(_pcr, _help) + ('pcr-help', ))
async def pcr_help(bot, ev: EventInterface):
    await bot.kkr_send(ev, PRC_HELP)

_ark=['明日方舟', '舟游', 'arknights']
@sv.on_fullmatch(tuple([''.join(l) for l in itertools.product(_ark, _help)]))
async def ark_help(bot, ev: EventInterface):
    await bot.kkr_send(ev, ARKNIGHTS_HELP)

_push=['推送', 'push']
@sv.on_fullmatch(tuple([''.join(l) for l in itertools.product(_push, _help)]))
async def push_help(bot, ev: EventInterface):
    await bot.kkr_send(ev, PUSH_HELP)

@sv.on_fullmatch(('通用功能', '通用帮助', 'general-help'))
async def normal_help(bot, ev: EventInterface):
    await bot.kkr_send(ev, NORMAL_HELP)

@sv.on_fullmatch(('帮助', '幫助', 'help'))
async def send_help(bot, ev: EventInterface):
    await bot.kkr_send(ev, SHORT_HELP)
