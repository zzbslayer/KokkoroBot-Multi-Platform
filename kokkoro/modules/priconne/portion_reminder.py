from kokkoro.service import Service, BroadcastTag
from kokkoro import R

sv9 = Service('pcr-portion-reminder-utc9', enable_on_default=False, help_='药水购买小助手(UTC+9)')
sv8 = Service('pcr-portion-reminder-utc8', enable_on_default=False, help_='药水购买小助手(UTC+8)')
#msg = "主人様、记得买经验药水~"
img = R.img('提醒药水小助手.jpg')

@sv8.scheduled_job('cron', hour='0,6,12,18')
async def pcr_portion_reminder_utc8():
    await sv8.broadcast(img, [BroadcastTag.cn_broadcast, BroadcastTag.tw_broadcast])

@sv9.scheduled_job('cron', hour='23,5,11,17')
async def pcr_portion_reminder_utc9():
    await sv9.broadcast(img, BroadcastTag.jp_broadcast)