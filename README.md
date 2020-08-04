# KokkoroBot
KokkoroBot is a forked version of **HoshinoBot** and migrates from QQ to discrod. 

## Motivation
HoshinoBot 无论是基础设施还是应用层，大量使用了来自 Nonebot 中的概念如 `CQEvent`, `MessageSegment`，这直接导致上层服务与 Nonebot 以及 Nonebot 底层的 CQHttp 极大程度上耦合在一起，难以将 HoshinoBot 移植到其他平台或框架，比如从 QQ 迁移至 Discord。

因此 KokkoroBot 针对这一问题对底层代码进行重构，期望应用服务与 IM 平台解耦合，能够较迅速的迁移至其他平台。~~其实是因为酷Q凉了，mirai随时可能会挂~~

## Migration
KokkoroBot 在基础设施与应用层中加一层统一接口以达到解耦合的目的。

定义机器人收到来自平台的事件为 `Event`。在 Nonebot 中即 `CQEvent`；在 discord 中即 `discord.Message`。定义统一接口 `EventInterface`。在 KokkoroBot-discord 中定义 `DiscordEvent`， 这个类实现了 `EventInterface` 接口，接收到的所有 `discord.Message` 类都需要转化为 `DiscordEvent`， 上层服务使用 `EventInterface` 接口来使用 `DiscordEvent` 对象。

也就是说无论使用何种平台搭建 KokkoroBot，都需要将平台事件适配为 `EventInterface` 的实现类。因此上层应用与平台无关的基础设施，两者都依赖于 `EventInterface` 这个统一接口，从而与底层平台解耦合。

发送图片时同理，本机图片使用 `ResImg` 表示；远程图片使用 `RemoteResImg` 表示；处理过的图片使用`PIL.Image.Image`表示，将这三个类的对象直接作为参数传递给 `KokkoroBot.send` 方法，在 bot 的 `send` 方法内部执行平台相关逻辑。

```python
class KokkoroBot(discord.Client):
    def send(self, ev: EventInterface, msg:UnionUnion[ResImg, RemoteResImg, Image.Image, str], filename="image.png"):
        pass
```

- 在这样的设计下，将 KokkoroBot 移植到其他平台便不再困难。只需要完成以下三步：
    - 完成平台相关的机器人初始化逻辑
        - `kokkoro/__init__.py` 中的 `KokkoroBot.__init__` 与 `KokkoroBot.run` 
    - 完成机器人发送消息的接口
        - `kokkoro/__init__.py` 中的 `KokkoroBot.send`
        - 使机器人能够发送文字、本地图片、远程图片、 PIL 图片等等。
    - 完成机器人处理消息时 `Event` 的适配
        - `kokkoro/msg_handler.py` 中的  `event_adaptor`
        - 使平台相关的 `Event` 转化为统一接口 `EventInterface`
- 甚至对代码进一步设计可以作为一个同时兼容多平台的 bot 项目。
- 目前使用 `EventInterface.get_mentions` 接口仍会导致与下层平台耦合，可能需要进一步设计。
## TODO
- [x] Isolate platform specific logic from application services
- [x] Image
- [ ] Audio
- [ ] Scheduler
- [ ] Permission control with admin
- [ ] Modules migration
    - [ ] Arknights
    - [ ] Pcr Clanbattle
    - [ ] Dice
    - [ ] Flac
    - [ ] Group Master
    - [ ] Priconne
        - [x] Arena
        - [x] Calender
        - [ ] Comic Spider
        - [ ] Horse
        - [ ] News
        - [x] Query
        - [ ] Reminder
    - [ ] Setu
    - [ ] Weibo Spider
- [ ] Decouple `EventInterface.get_mentions` from platform
- [ ] Multi-platform
    - [x] Discord
    - [ ] Other