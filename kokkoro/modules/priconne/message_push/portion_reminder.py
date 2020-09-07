from kokkoro.service import BroadcastTag, BroadcastService
from kokkoro import R

sv9 = BroadcastService('pcr-portion-reminder-utc9', 
    broadcast_tag=BroadcastTag.jp_broadcast, 
    enable_on_default=False, help_='药水购买小助手(UTC+9)')

sv8 = BroadcastService('pcr-portion-reminder-utc8', 
    broadcast_tag=[BroadcastTag.cn_broadcast, BroadcastTag.tw_broadcast],
    enable_on_default=False, help_='药水购买小助手(UTC+8)')

img = R.img('提醒药水小助手.jpg')

@sv8.scheduled_job('cron', hour='0,6,12,18', misfire_grace_time=60*10)
async def pcr_portion_reminder_utc8():
    await sv8.broadcast(img)

@sv9.scheduled_job('cron', hour='23,5,11,17', misfire_grace_time=60*10)
async def pcr_portion_reminder_utc9():
    await sv9.broadcast(img)