from kokkoro.service import Service, BroadcastTag

svjp = Service('pcr-arena-reminder-utc9', enable_on_default=False, help_='背刺时间提醒(UTC+9)')
svtw = Service('pcr-arena-reminder-utc8', enable_on_default=False, help_='背刺时间提醒(UTC+8)')

msg = '主人様、准备好背刺了吗？'

@svtw.scheduled_job('cron', hour='14', minute='45')
async def pcr_reminder_utc8():
    await svtw.broadcast(msg, tag=[BroadcastTag.cn_broadcast, BroadcastTag.tw_broadcast])

@svjp.scheduled_job('cron', hour='13', minute='45')
async def pcr_reminder_utc9():
    await svjp.broadcast(msg, tag=BroadcastTag.jp_broadcast)