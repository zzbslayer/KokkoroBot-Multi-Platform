from kokkoro.service import Service
from kokkoro.common_interface import KokkoroBot, EventInterface
import httpx, sys, bs4, itertools, asyncio

sv = Service('ark-recruit')

url = "https://wiki.biligame.com/arknights/公开招募工具"

worker_infos = list()
all_tags = set()

def parse_data(data):
    _worker_infos = []
    _all_tags = {"资深", "高级资深"}
    bsObj = bs4.BeautifulSoup(data, "html.parser")
    details = bsObj.findAll("div",{"class": "contentDetail"})
    for detail in details:
        if u"公开招募" not in detail.attrs["data-param1"]:
            continue
        name = detail.find("a").attrs["title"].strip()
        profes = detail.attrs["data-param1"].split(",")[0].strip()
        #sex = detail.attrs["data-param1"].split(",")[1].strip()
        star = int(detail.attrs["data-param2"].strip())
        tags = set()
        if star == 5:
            tags.add("资深")
        elif star == 6:
            tags.add("高级资深")

        for tag in detail.findAll("span", {"class": "tagText"}):
            cur_tag = tag.getText().strip().split(" ")

            for i in range(len(cur_tag)):
                if cur_tag[i] == "近战":
                    cur_tag[i] = "近战位" # TODO This is a bug of biligame wiki
                
            tags.update(cur_tag)
            _all_tags.update(cur_tag)
        tags.add(profes)
        #tags.add(sex)
        _all_tags.add(profes)
        #_all_tags.add(sex)

        if name == "芙兰卡": # TODO This is a bug of biligame wiki
            continue

        stars = ""
        for i in range(star):
            stars += "★"

        info = [tags, star, f"{name} {star}★"]
        _worker_infos.append(info)
    return _worker_infos, _all_tags

def validate_tags(tags):
    for tag in tags:
        if tag not in all_tags:
            return False, tag
    return True, None


def get_combs(tags):
    combs = []
    for i in range(len(tags)):
        for iter in itertools.combinations(tags, i + 1):
            combs.append(set(iter))
    return combs

def compare_workers(w1, w2):
    return w1[1] > w2[1]

def get_workers(tags, worker_infos, over4_only=True):
    ret = []
    combs = get_combs(tags)
    for comb in combs:
        workers = []
        cur_over4_only = True
        for worker in worker_infos:
            if comb <= worker[0]:
                star = worker[1]
                if star in [4, 5]:
                    workers.append(worker)
                elif star == 6:
                    if "高级资深" in comb:
                        workers.append(worker)
                elif star == 3:
                    cur_over4_only = False
                    if over4_only == False:
                        workers.append(worker)
        # sort by star
        workers.sort(key=lambda x: x[1], reverse=True)
        if over4_only == False or cur_over4_only == True and len(workers) > 0:
            ret.append([comb, workers, cur_over4_only])
    # sort by cur_over4_only
    ret.sort(key=lambda x: x[2], reverse=True)
    return ret

def format_workers(workers):
    message = []
    for worker in workers:
        tip = "（"
        tag_list = []
        for tag in worker[0]:
            tag_list.append(tag)
        tip += f"{'，'.join(tag_list)}）"
        tip += "可以招募以下干员："
        message.append(tip)
        worker_list = []
        for info in worker[1]:
            worker_list.append(info[2])
        message.append(" ".join(worker_list))
        message.append("")
    return "\n".join(message)

async def _async_init():
    url = "https://wiki.biligame.com/arknights/公开招募工具"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=10.0)
        if res.status_code == httpx.codes.OK:
            global worker_infos
            global all_tags
            worker_infos, all_tags = parse_data(res.text)
        else:
            sv.logger.error("Fail to load recruit info of arknights")

loop = asyncio.new_event_loop()
loop.run_in_executor(_async_init())

HELP_MESSAGE = '请输入标签。默认仅显示必得4★的TAG组合\n示例：公开招募 位移 近战位\n显示所有可能干员请使用参数"-a"或"全部"\n示例：公开招募 -a 位移 近战位\n网页版：https://www.bigfun.cn/tools/aktools-old/akhr.html'
@sv.on_prefix(('ark-recruit','公开招募', "公招"))
async def public_recruit(bot: KokkoroBot, ev: EventInterface):
    over4_only = True
    args = ev.get_param().remain
    if args[:2] in ['-a', '全部']:
        over4_only = False 
        args = args[2:]

    tags = args.split()
    size = len(tags)
    if size == 0:
        await bot.kkr_send(ev, HELP_MESSAGE)
        return

    for i in range(size):
        if tags[i][-2:] == "干员":
            tags[i] = tags[i][:-2]
    valid, _tag = validate_tags(tags)
    if not valid:
        await bot.kkr_send(ev, f'无效 TAG：{_tag}')
        return

    workers = get_workers(tags, worker_infos, over4_only)
    if len(workers) == 0:
        if over4_only:
            await bot.kkr_send(ev, f'无法保证招聘四星及以上干员\n若希望显示所有可能干员请使用命令：公开招募 -a {args}')
        else:
            await bot.kkr_send(ev, '无匹配干员')
    else:
        msg = format_workers(workers)
        await bot.kkr_send(ev, msg)

@sv.on_fullmatch(('ark-tags', '公招TAG', '公招tag'))
async def tags(bot, ev):
    msg = f'公开招募TAG一览：\n{all_tags}'
    await bot.kkr_send(ev, msg)