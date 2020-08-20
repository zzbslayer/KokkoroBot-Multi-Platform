from aiogram import Bot, Dispatcher, executor, types

import kokkoro
from kokkoro.common_interface import KokkoroBot, SupportedMessageType, EventInterface
from kokkoro.telegram.telegram_adaptor import TelegramEvent
from kokkoro.typing import overrides

class KokkoroTelegramBot(KokkoroBot):
    def __init__(self, config):
        self.config = config
        super().kkr_load_modules(self.config) # KokkoroBot init
        self.bot = Bot(config.bot.telegram.TELEGRAM_TOKEN)
        self.dp = Dispatcher(self.bot)

        async def tg_msg_handler(raw_event: types.Message):
            await self.kkr_on_message(raw_event)

        self.dp.register_message_handler(tg_msg_handler)

    @overrides(KokkoroBot)
    def kkr_event_adaptor(self, raw_event:types.Message) -> EventInterface:
        return TelegramEvent(raw_event)
        

    @overrides(KokkoroBot)
    async def kkr_send(self, ev: TelegramEvent, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        if isinstance(msg, str):
            await ev.get_raw_event().answer(msg)
        else:
            raise NotImplementedError

    @overrides(KokkoroBot)
    def kkr_run(self):
        executor.start_polling(self.dp, skip_updates=True)
    