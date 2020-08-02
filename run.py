import kokkoro
from kokkoro import config, service, trigger

from kokkoro import service
async def hello(bot, message, param):
    await message.channel.send('hello')

async def hey(bot, message, param):
    await message.channel.send('hey')

sv = service.Service("_test")
sf1 = service.ServiceFunc(sv, hello, False)
sf2 = service.ServiceFunc(sv, hey, True)

trigger.prefix.add('hello', sf1)
trigger.prefix.add('hey', sf2)

kokkoro.kkr_bot.run(config.DISCORD_TOKEN)
