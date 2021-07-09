# -*- coding: utf-8 -*-
import os
from quart import Quart, request, abort
from wechatpy.work.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException
from wechatpy.work.exceptions import InvalidCorpIdException
from wechatpy.work import parse_message, create_reply
from wechatpy.messages import BaseMessage

import kokkoro
from kokkoro.typing import overrides
from kokkoro.common_interface import KokkoroBot, EventInterface, SupportedMessageType
from kokkoro.bot.wechat_enterprise.wechat_enterprise_adaptor import WechatEpEvent

def wechat_handler(bot):
    async def wrapper():
        signature = request.args.get("msg_signature", "")
        timestamp = request.args.get("timestamp", "")
        nonce = request.args.get("nonce", "")

        crypto = WeChatCrypto(
                bot.config.bot.wechat_enterprise.WECHAT_TOKEN, 
                bot.config.bot.wechat_enterprise.ENCODING_AES_KEY, 
                bot.config.bot.wechat_enterprise.CORP_ID)

        if request.method == "GET":
            kokkoro.logger.debug("Wechat check triggered")
 
            echo_str = request.args.get("echostr", "")
            try:
                echo_str = crypto.check_signature(signature, timestamp, nonce, echo_str)
            except InvalidSignatureException:
                abort(403)
            return echo_str
        else:
            kokkoro.logger.debug("Wechat messages handler triggered")
            try:
                msg = crypto.decrypt_message(await request.data, signature, timestamp, nonce)
                kokkoro.logger.debug(f"Descypted message: \n{msg}")
            except (InvalidSignatureException, InvalidCorpIdException):
                abort(403)
            msg = parse_message(msg)

            await bot.kkr_on_message(msg)
            reply = create_reply(bot.ret_val, msg).render()
            bot.ret_val = None
            res = crypto.encrypt_message(reply, nonce, timestamp)
            return res
    return wrapper

class KokkoroWechatEpBot(KokkoroBot):
    def __init__(self, config):
        self.config = config
        super().kkr_load_modules(self.config)
        self.app = Quart(__name__)
        self.app.route("/wechat", methods=["GET", "POST"])(wechat_handler(self))
        self.ret_val = None

    @overrides(KokkoroBot)
    def kkr_event_adaptor(self, raw_event: BaseMessage) -> EventInterface:
        return WechatEpEvent(raw_event)
    
    @overrides(KokkoroBot)
    async def kkr_send(self, ev: EventInterface, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        if isinstance(msg, str):
            kokkoro.logger.debug(f"Send result: {msg}")
            self.ret_val = msg
        else:
            raise NotImplementedError

    @overrides(KokkoroBot)
    def kkr_run(self):
        self.app.run("0.0.0.0", 5001, debug=True)