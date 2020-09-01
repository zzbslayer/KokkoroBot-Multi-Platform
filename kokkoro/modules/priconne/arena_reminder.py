from kokkoro.service import BroadcastTag, BroadcastService

sv9 = BroadcastService('pcr-arena-reminder-utc9', 
    broadcast_tag=[BroadcastTag.cn_broadcast, BroadcastTag.tw_broadcast], enable_on_default=False, help_='背刺时间提醒(UTC+9)')

sv8 = BroadcastService('pcr-arena-reminder-utc8', 
    broadcast_tag=BroadcastTag.jp_broadcast, 
    enable_on_default=False, help_='背刺时间提醒(UTC+8)')

msg = '主人様、准备好背刺了吗？'

@sv8.scheduled_job('cron', hour='14', minute='45', misfire_grace_time=60*10)
async def pcr_reminder_utc8():
    await sv8.broadcast(msg)

@sv9.scheduled_job('cron', hour='13', minute='45', misfire_grace_time=60*10)
async def pcr_reminder_utc9():
    await sv9.broadcast(msg)