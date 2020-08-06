# KokkoroBot
KokkoroBot is a forked version of **HoshinoBot** and migrates from QQ to discrod and telegram. 

本项目是 HoshinoBot 的分支版本，充斥着大量个人魔改产物。若希望体验原汁原味的 HoshinoBot 请自行魔改回去。

## Motivation
HoshinoBot 无论是基础设施还是应用层，大量使用了来自 Nonebot 中的概念如 `CQEvent`, `MessageSegment`，这直接导致上层服务与 Nonebot 以及 Nonebot 底层的 CQHttp 极大程度上耦合在一起，难以将 HoshinoBot 移植到其他平台或框架，比如从 QQ 迁移至 Discord。

因此 KokkoroBot 针对这一问题对底层代码进行重构，期望应用服务与 IM 平台解耦合，能够较迅速的迁移至其他平台。~~其实是因为酷Q凉了，mirai随时可能会挂~~

## 各平台使用方法
### 目前支持的平台：
- [x] Discord
- [x] Telegram
- [x] 企业微信
### Discord
- `kokkoro.config.__bot__.py` 中设置 `BOT_TYPE` 为 `discord`
- `kokkoro.config.bot.discord.py` 中设置相关参数
> FAQ:
>
> Q1: 如何查看 Discord 群组 ID 与用户 ID ?
>
> A1: https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-

### Telegram
- `kokkoro.config.__bot__.py` 中设置 `BOT_TYPE` 为 `telegram`
- `kokkoro.config.bot.telegram.py` 中设置相关参数
> FAQ:
>
> Q1: 如何查看群组 ID ?
>
> A1: https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id
>
> Q2: 如何查看我的用户 ID ?
>
> A2: https://bigone.zendesk.com/hc/en-us/articles/360008014894-How-to-get-the-Telegram-user-ID-
>
> Q3: 如何查看其他用户 ID 或者 BOT ID ?
>
> A3: 真不知道。虽然可以通过在 bot 中打印 types.Message 相关参数得到用户 ID。但暂时并不知道什么方法能够快速进行查询。

### 企业微信
TODO

## 开发者碎碎念
### 接口设计
KokkoroBot 在基础设施与应用层中加一层统一接口 `common_interface` 以达到解耦合的目的。

任何平台的机器人都需要实现 `kokkoro.common_interface.KokkoroBot` 接口。

任何平台的事件(`Event`)都需要转化为 `kokkoro.common_interface.EventInterface` 供上层服务使用。同理，任何平台的用户(`User`)都需要转化为 `kokkoro.common_interface.UserInterface`。

发送图片时不再依赖任何平台相关逻辑，直接将 `common_interface.SupportedMessageType` 格式的消息传给 `kokkoro.common_interface.KokkoroBot.kkr_send` 函数，在具体实现类中实现具体平台相关的处理逻辑。

上层服务与平台彻底解耦合。平台依赖于 `kokkoro.common_interface`，上层服务依赖于 `kokkoro.commmon_interface`。因此能够兼容多种平台。

- 在这样的设计下，将 KokkoroBot 移植到其他平台便不再困难。只需要以下三步：
    - 完成平台相关的机器人
        - 机器人需要实现 `kokkoro.common_interface.KokkoroBot` 接口
        - 需要支持 `common_interface.SupportedMessageType` 中所有消息类型的发送
        - 示例: `kokkoro.discord.KokkroDiscordBot`
    - 实现 `Event` 的适配
        - 将平台相关 `Event` 适配为 `common_interface.EventInterface`
            - 比如 `CQEvent`, `discord.Message`
        - 示例：`kokkoro.discord.discord_adaptor.DiscordEvent`
    - 实现 `User` 的适配
        - 将平台相关 `User` 适配为 `common_interface.UserInterface`
            - 比如 `CQEvent` 中的 at 信息，`discord.User`
        - 示例：`kokkoro.discord.discord_adaptor.DiscordUser`

### 新 IM 平台适配
以 telegram 为例，从零对 telegram 平台进行开发主要包含以下几步。
- `kokkoro.config.__bot__` 中配置 `BOT_TYPE = 'telegram'`
- `kokkoro.config.bot` 中添加 `telegram.py` 配置文件
- 在 `kokkoro.telegram` 中实现相关适配
- 在 `kokkoro.__init__` 中添加 telegram bot

### TODO
- [x] Isolate platform specific logic from application services
- [ ] Scheduler
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
        - [x] Horse 
        - [ ] News
        - [x] Query
        - [ ] Reminder
    - [ ] Setu
    - [ ] Weibo Spider
- [x] Multi-platform
    - [x] Discord
        - [ ] Audio
        - [x] Image
        - [x] Text
        - [ ] Permission control with admin
    - [x] Telegram
        - [ ] Audio
        - [ ] Image
        - [x] Text
        - [ ] Permission control with admin