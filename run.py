import kokkoro
from kokkoro import service, trigger

async def hello(bot, message, param):
    await message.channel.send('hello')

async def hey(bot, message, param):
    await message.channel.send('hey')

sv = service.Service("_test")
sf1 = service.ServiceFunc(sv, hello, False)
sf2 = service.ServiceFunc(sv, hey, True)

trigger.prefix.add('hello', sf1)
trigger.prefix.add('hey', sf2)

kkr_bot = kokkoro.get_bot()
kkr_bot.run()
