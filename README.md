# KokkoroBot
KokkoroBot is a forked version of **HoshinoBot** and migrates from QQ to discrod and telegram. 

本项目是 HoshinoBot 的分支版本，充斥着大量个人魔改产物。若希望体验原汁原味的 HoshinoBot 请自行魔改回去。

## 1. Motivation
HoshinoBot 无论是基础设施还是应用层，大量使用了来自 Nonebot 中的概念如 `CQEvent`, `MessageSegment`，这直接导致上层服务与 Nonebot 以及 Nonebot 底层的 CQHttp 极大程度上耦合在一起，难以将 HoshinoBot 移植到其他平台或框架，比如从 QQ 迁移至 Discord。

因此 KokkoroBot 针对这一问题对底层代码进行重构，期望应用服务与 IM 平台解耦合，能够较迅速的迁移至其他平台。~~其实是因为酷Q凉了，mirai随时可能会挂~~

## 2. 使用方法
### 2.1 配置文件
首先将 `kokkoro` 文件夹下的 `config_example` 在当前文件夹复制一份并重命名为 `config`。然后修改其中的各个配置文件

```sh
cd kokkoro
cp -r config_example config
```

#### 2.1.1 通用配置
配置文件为 `kokkoro/config/__bot__.py`
- `BOT_TYPE`
    - 将 `BOT_TYPE` 修改为你需要使用的 IM 平台，可填写的值有以下三种
    - `discord`
    - `telegram`
    - `wechat_enterprise` (企业微信)
- `BOT_ID`, `SUPER_USER`, `ENABLED_GROUP`
    - 这三个参数都是平台相关的。需要在对应平台的配置文件中进行修改
    - `BOT_ID`：bot 自己的 ID
        - 部分平台 bot 会收到自己的消息，因此使用该参数过滤 bot 自己的消息
    - `SUPER_USER`：在 bot 中拥有最高权限的用户，通常将自己的 ID 填在这里
    - `ENABLED_GROUP`：bot 仅会对 `ENABLED_GROUP` 中的群组作出回应
- `LOG_LEVE`
    - 开发人员 DEBUG 用，一般用户设置为 "INFO" 即可
- `ENABLE_IMAGE`
    - 是否允许 bot 发送图片
    - 第一次部署建议先设置为 `False`，成功后再改为 `True`
- `NICK_NAME`
    - bot 别称，通过在消息最前面加别称达到与 @bot 相同的效果
- `RES_PROTOCOL`
    - 加载内置资源文件的方式，可填写的值有以下两种：
    - `file` （通过文件访问）
    - `http` （通过 http 协议访问，需另外部署静态资源服务器）
- `RES_DIR`
    - 资源文件的根目录路径
    - 示例：`~/.kokkoro/res/`
- `RES_URL`
    - 资源文件的根 URL
    - 示例：`http://123.123.123.123/`
- `MODULES_ON`
    - 开启的模块
    - 将 `kokkoro/modules/` 目录下想要开启的模块名称填写在这个列表中

#### 2.1.2 Discord 配置
配置文件为 `kokkoro/config/bot/discord.py`。

Discord 需要将客户端设置为开发者模式才能查看群组、用户 ID。开发者模式的开启请参考该链接 https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-

> 在修改配置文件之前，先在 discord 网站上申请好 bot
> 
> https://discord.com/developers/docs/intro

- `DISCORD_TOKEN`
    - 填写之前申请得到的 TOKEN
- `ENABLED_GROUP`
    - 允许使用 BOT 的 discord 群组 ID
- `SUPER_USER`
    - 填写自己的 ID
- `BOT_ID`
    - 填写 BOT 的 ID

#### 2.1.3 Telegram 配置
配置文件为 `kokkoro/config/bot/telegram.py`

Telegram 获取用户与群组 ID 很麻烦，需要从 API 中自己获取，请参考该链接 https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id

> 在修改配置文件之前，先在在 Telegram 客户端中找 BotFather 申请好 BOT，并使用 `/setprivacy` 命令将 bot 设置为允许接受来自群组的消息
>
> https://core.telegram.org/bots

- `TELEGRAM_TOKEN`
    - 填写从 BotFather 得到的 TOKEN
- `ENABLED_GROUP`
    - 允许使用 BOT 的 telegram 群组 ID
- `SUPER_USER`
    - 填写自己的 ID
- `BOT_ID`
    - 填写 BOT 的 ID
    - 目前 telegram 暂时没有一个比较好的手段获得 `BOT_ID`，不过 telegram bot 也不会收到自己发的消息，因此设置为 `None` 即可

#### 2.1.4 企业微信
TODO

### 2.2 部署流程
#### 2.2.1 Linux (推荐)
使用 Linux 部署可以通过 docker 省去自行搭建环境的麻烦与各种平台问题。
- 安装 docker 环境
    - https://docs.docker.com/engine/install/centos/
- 安装 docker-compose
    - https://docs.docker.com/compose/install/
- 建立 Docker 镜像
    - 在 KokkoroBot 根目录下，运行如下命令，生成的镜像中将会包含 KokkoroBot 中需要的所有依赖
```sh 
docker build . -t kokkoro-env
```
- 使用 docker-compose 部署
    - 进行 debug 时请删除 -d 参数
```sh
docker-compose up -d # 生产环境
```
- 在群里发一句 `help`，bot 如果反馈帮助信息则说明初步搭建完成！

#### 2.2.2 Windows
TODO

### 2.3 资源文件
目前 KokkoroBot 中的图片等资源文件来自于 HoshinoBot 群内提供的资源包，可以直接去 HoshinoBot 群内下载。未来可能会使用到部分额外资源，因此在 KokkoroBot 中单独提供一份 KokkoroBot 专用资源包。

HoshinoBot 群：367501912。KokkoroBot 群：887897168。

下载好的资源文件放在服务器的 `~/.kokkoro` 目录下，保证目录看上去是如下结构 `~/.kokkoro/res/img`。

### 2.4 第三方应用的 API Key
TODO

## 3. 二次开发与新平台适配
### 3.1 接口设计
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

### 3.2 新 IM 平台适配
以 telegram 为例，从零对 telegram 平台进行开发主要包含以下几步。
- `kokkoro.config.__bot__` 中配置 `BOT_TYPE = 'telegram'`
- `kokkoro.config.bot` 中添加 `telegram.py` 配置文件
- 在 `kokkoro.telegram` 中实现相关适配
- 在 `kokkoro.__init__` 中添加 telegram bot

# TODO
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
    - [x] Wechat Enterprise
        - [ ] Audio
        - [ ] Image
        - [x] Text
        - [ ] Permission control with admin