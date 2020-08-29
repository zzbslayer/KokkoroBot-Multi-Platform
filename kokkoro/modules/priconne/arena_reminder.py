from kokkoro.service import Service

svjp = Service('pcr-arena-reminder-utc9', enable_on_default=False, help_='背刺时间提醒(UTC+9)')
svtw = Service('pcr-arena-reminder-utc8', enable_on_default=False, help_='背刺时间提醒(UTC+8)')

msg = '主さま、准备好背刺了吗？'

@svtw.scheduled_job('cron', hour='14', minute='45')
async def pcr_reminder_utc8():
    await svtw.broadcast(msg, 'pcr-reminder-utc8', 0.2)

@svjp.scheduled_job('cron', hour='13', minute='45')
async def pcr_reminder_utc9():
    await svjp.broadcast(msg, 'pcr-reminder-utc9', 0.2)
