# 开发者文档

## 开发环境

无论 Linux 还是 macOS，使用 Docker 运行开发环境都可以避免 Python 版本冲突、依赖管理等很多琐碎问题。

- 安装 Docker 环境。

  https://docs.docker.com/engine/install/centos/

- 安装 Docker Compose。

  https://docs.docker.com/compose/install/

- 构建 Docker 镜像。

  ```sh
  # 确保处于项目根目录
  docker-compose build
  ```

- 使用 Docker Compose 运行所有服务。

  ```sh
  # 确保处于项目根目录
  docker-compose up
  ```

  也可以只运行 Bot，不运行 Web 界面。

  ```sh
  # 确保处于项目根目录
  docker-compose up bot
  ```

- 在群里发一句 `help`，Bot 如果反馈帮助信息则说明初步搭建完成！

- 修改代码后无需重新构建 Docker 镜像，只需要再次执行 `docker-compose up` 即可生效。

## 项目架构

项目架构文档分为两部分：基于 `kokkoro.service` 与 `kokkoro.common_interface` 接口进行上层功能开发；基于 `kokkoro.common_interface` 与 `kokkoro.platform_patch` 进行新平台适配。

### 1. 上层功能开发
接口与 HoshinoBot 几乎保持一致，如果之前有过 HoshinoBot 二次开发经验，相信你一定能快速上手 KokkoroBot 的二次开发。
功能管理如下所示，

- Module A
    - Service 1
        - Functionality a
        - Functionality b
- Module B
    - Service 2
        - Functionality c
    - Service 3
        - Functionality d
        - Functionality e

#### 1.1 Quick Example
1. 在 `kokkoro/modules` 中新建文件夹 `echo`
2. 在 `kokkoro/config/__bot__.py` 中的 `MODULES_ON` 中添加 `echo` 模块。
3. 在 `kokkoro/modules/echo` 中新建文件 `__init__.py`
4. `__init__.py` 中编写以下代码
```python
from kokkoro.service import Service
from kokkoro.common_interface import KokkoroBot, EventInterface
sv = Service('echo') # 创建 Service 对象
@sv.on_prefix(('echo'), only_to_me=False) # 以前缀 `echo` 匹配消息
async def help(bot: KokkoroBot, ev: EventInterface):
    # 将 echo 前缀之后的所有内容发给用户
    await bot.send(ev, ev.get_param().remain)
```
5. 启动 bot
6. 在群聊中发送消息 `echo 优质复读机` 后，会收到 bot 的回复消息 `优质复读机`

#### 1.2 模块管理 (Modules)
KokkoroBot 延用了 HoshinoBot 中的模块管理机制。KokkoroBot 仅仅会加载 `MODULES_ON` 中开启的模块。
1. 在 `kokkoro/modules` 中新建文件夹 `new_module`
2. 在 `kokkoro/config/__bot__.py` 中的 `MODULES_ON` 中添加 `new_module` 模块。
3. 在 `kokkoro/modules/new_module` 中编写业务逻辑
执行完以上三步就完成了新模块的创建与启用。

#### 1.3 服务层 (Services)
一个模块中可以有一个或多个服务。每个服务中可以有一个或多个功能函数。可以通过在群聊中发送特殊命令，来管理当前群内的服务。
- `lssv` 列出群内服务
- `enable <service_name>` 开启群内服务
- `disable <service_name>` 关闭群内服务。

```python
#Example
from kokkoro.service import Service
sv = Service('echo')  # <------------------------------ 这里是服务
@sv.on_prefix(('echo'), only_to_me=False)
async def help(bot: KokkoroBot, ev: EventInterface):
    await bot.send(ev, ev.get_param().remain)
```

##### 1.3.1 构造函数
Service 构造函数
- `name: str` - 服务名
- `use_priv: int` - 使用所需要的权限
    - 默认为 `kokkoro.priv.NORMAL`，即普通群员
- `manage_priv: int` - 管理所需要的权限
    - 默认为 `kokkoro.priv.ADMIN`，即管理员
- `enable_on_default: bool` - 是否默认开启
    - 默认为 `True`
- `visible: bool` - 是否对 `lssv` 命令可见
    - 使用 `lssv -a` 命令可以查看不可见服务
    - 默认为 `True`

```python
class Service:
    def __init__(self, name, use_priv=None, manage_priv=None, enable_on_default=None, visible=None):
```

##### 1.3.2 broadcast
向开启该服务的群组广播消息
- `msgs: Union[SupportedMessageType, List[SupportedMessageType]]` - 消息或消息列表
- `TAG: str` - 广播标签，仅用于日志打印
    - 默认为空字符串

```python
async def broadcast(self, msgs: Union[SupportedMessageType, List[SupportedMessageType]], TAG=''):
```

##### 1.3.3 装饰器
使用服务层提供的装饰器(decorator)装饰功能函数，装饰器会自动将功能函数注册到 KokkoroBot 中，一旦群内消息触发了装饰器的匹配条件，将会自动触发对应功能函数。

```python
#Example
from kokkoro.service import Service
sv = Service('echo')
@sv.on_prefix(('echo'), only_to_me=False)  # <---------- 这里是装饰器
async def help(bot: KokkoroBot, ev: EventInterface):
    await bot.send(ev, ev.get_param().remain)
```

###### 1.3.3.1 on_prefix
前缀匹配。
- `prefix: Union[str, Tuple[str]]` - 前缀
- `only_to_me: bool` - 是否需要 at bot
```python
def on_prefix(self, prefix, only_to_me=False) -> Callable:
```

匹配完成后，功能函数可通过 `EvnetInterface.get_param()` 获取到前缀匹配相关的结果，类型为`PrefixHandlerParameter`。
- `PrefixHandlerParameter`
    - `prefix: str` - 匹配的前缀
    - `remain: str` - 从原消息中删除前缀后的剩余部分
    - `args: str` - 将剩余部分(remain)转化为 ArgParser 的参数
```python
class PrefixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, prefix, remain):
        super().__init__(msg)
        self.prefix=prefix
        self.remain=remain.strip()

    @property
    def args(self):
        return self.remain.split(' ')
```

###### 1.3.3.2 on_suffix
后缀匹配。
- `suffix: Union[str, Tuple[str]]` - 后缀
- `only_to_me: bool` - 是否需要 at bot
```python
def on_suffix(self, suffix, only_to_me=False) -> Callable:
```

匹配完成后，功能函数可通过 `EvnetInterface.get_param()` 获取到后缀匹配相关的结果。类型为 `SuffixHandlerParameter`。
- `SuffixHandlerParameter`
    - `suffix: str` - 匹配的后缀
    - `remain: str` - 从原消息中删除后缀后的剩余部分
```python
class SuffixHandlerParameter(BaseParameter):
    def __init__(self, msg:str, suffix, remain):
        super().__init__(msg)
        self.suffix=suffix
        self.remain=remain.strip()
```

###### 1.3.3.3 on_fullmatch
完全匹配。
- `word: Union[str, Tuple[str]]` - 完全匹配
- `only_to_me: bool` - 是否需要 at bot
```python
def on_fullmatch(self, word, only_to_me=False) -> Callable:
```

###### 1.3.3.4 on_keyword
关键词匹配。
- `keywords: Union[str, Tuple[str]]` - 关键词
- `only_to_me: bool` - 是否需要 at bot
```python
def on_keyword(self, keywords, only_to_me=False) -> Callable:
```


###### 1.3.3.5 on_rex
正则匹配。
- `rex: Union[str, re.Pattern]` - 正则表达式
- `only_to_me: bool` - 是否需要 at bot
```python
def on_rex(self, rex: Union[str, re.Pattern], only_to_me=False) -> Callable:
```

匹配完成后，功能函数可通过 `EvnetInterface.get_param()` 获取到正则匹配相关的结果。类型为 `RegexHandlerParameter`。
- `RegexHandlerParameter`
    - `match: re.Match` - re.search 的匹配结果
```python
class RegexHandlerParameter(BaseParameter):
    def __init__(self, msg:str, match):
        super().__init__(msg)
        self.match=match
```

###### 1.3.3.6 scheduled_job
使用 apscheduler 实现定时任务，接口可参考[文档](https://apscheduler.readthedocs.io/en/stable/modules/schedulers/base.html#apscheduler.schedulers.base.BaseScheduler.scheduled_job)，支持 cron。或参考 `kokkoro.modules.arena_reminder` 中的使用。
```python
def scheduled_job(self, *args, **kwargs) -> Callable:

#example 背刺提醒
@svjp.scheduled_job('cron', hour='13', minute='45')
async def pcr_reminder_utc9():
    await svjp.broadcast(msg, 'pcr-reminder-utc9')
```

#### 1.4 功能函数

功能函数仅仅接受两个参数 `kokkoro.common_interface.KokkoroBot` bot 对象与 `kokkoro.common_interface.EventInterface` 事件对象。
```python
# Example
@sv.on_prefix(('帮助', 'help'), only_to_me=False)
async def help(bot: KokkoroBot, ev: EventInterface): # <---- 这里是功能函数
    await bot.send(ev, '这也是帮助信息')
```

`EventInterface` 对象包含当前会话信息，包括发送者、消息内容等等；`KokkoroBot` 对象包含了对于 bot 的基本操作，包括发送信息等等

#### 1.5 Kokkoro 标准接口 (kokkoro.common_interface)
仅介绍与功能开发相关的**部分接口**。

##### 1.5.1 SupportedMessageType
KokkoroBot 支持发送的消息类型。
- `str`: 字符串类型消息
- `kokkoro.R.ResImg`: 图片资源文件
    - KokkoroBot 会自动根据配置文件中的 RES_PROTOCOL 去发送 ResImg 对应的本地或远程图片资源
- `kokkoro.R.RemoteResImg`: 远程图片资源文件
    - KokkoroBot 会发送 RemoteResImg 的 url 所指向的远程图片资源
- `PIL.Image.Image`: 内存中的 PIL 图片
- `matplotlib.figure.Figure`: matplotlib 图表

```python
SupportedMessageType = Union[ResImg, RemoteResImg, Image.Image, Figure, str]
```
##### 1.5.2 KokkoroBot
```python
class KokkoroBot:
    def kkr_send(self, ev: EventInterface, msg: SupportedMessageType, at_sender=False, filename="image.png"):
        pass

    def at(self, uid):
        raise NotImplementedError
```
###### 1.5.2.1 kkr_send
发送消息。可发送的消息类型为 `SupportedMessageType`，主要包含字符串、若干种图片类型、语音（暂未实现）。
- `ev: EventInterface` - 当前事件对象
- `msg: SupportedMessageType` - 发送的消息
- `at_sender: bool` - 是否 at 发送者
    - 默认为 `False`
- `filename: str` - discord 等平台在发送图片、文件时可以指定文件名进行发送。发送其他类型消息时，该参数无作用。
    - 默认为 `image.png`

###### 1.5.2.2 at
根据用户 id at 指定用户。不同平台的 at 不同，比如 QQ 为 `@12345` 而 discord 为 `<@!12345>`。因此通过 `bot.at(uid)` 生成 at 信息。

##### 1.5.3 UserInterface
```python
class UserInterface:
    # 获取用户 id
    def get_id(self):
        raise NotImplementedError
    # 获取用户名
    def get_name(self):
        raise NotImplementedError
    # 获取原始用户对象，如 discord.User
    # 上层功能开发时不推荐使用该接口，一旦使用则该功能将与平台耦合。
    # 使用前请加入形如 if config.BOT_TYPE == 'discord' 的判定。
    def get_raw_user(self):
        raise NotImplementedError
    # 获取用户群名片
    def get_nick_name(self):
        raise NotImplementedError
    # 是否是管理员
    def is_admin(self):
        raise NotImplementedError
    # 获取用户权限 返回值为 kokkoro.priv.BLACK ~ kokkoro.priv.SUPERUSER
    def get_priv(self):
        raise NotImplementedError
```

##### 1.5.4 EventInterface
```python
class EventInterface:
    # 获取事件（消息） id
    def get_id(self):
        raise NotImplementedError
    # 获取事件发送者id
    def get_author_id(self):
        raise NotImplementedError
    # 获取事件发送者名称
    def get_author_name(self):
        raise NotImplementedError
    # 获取事件发送者 UserInterface
    def get_author(self) -> UserInterface:
        raise NotImplementedError
    # 获取当前群组中的成员 List[UserInterface]
    def get_members_in_group(self) -> List[UserInterface]:
        raise NotImplementedError
    # 成员是否在当前群组中
    def whether_user_in_group(self, uid) -> bool:
        for member in self.get_members_in_group():
            if member.get_id() == uid:
                return True
        return False
    # 获取当前群组id
    def get_group_id(self):
        raise NotImplementedError
    # 获取消息内容
    def get_content(self) -> str:
        raise NotImplementedError
    # 获取该事件所有 at 的用户列表 List[UserInterface]
    def get_mentions(self) -> List[UserInterface]:
        raise NotImplementedError
    # 获取匹配结果
    def get_param(self) -> BaseParameter:
        return self.param
    # 获取原始事件对象，如 discord.Message
    # 上层功能开发时不推荐使用该接口，一旦使用则该功能将与平台耦合。
    # 使用前请加入形如 if config.BOT_TYPE == 'discord' 的判定。
    def get_raw_event(self):
        # coupleness
        raise NotImplementedError
```

### 2. 新平台适配
目前新平台适配主要涉及两个模块 `kokkoro.common_interface` 与 `kokkoro.platform_patch`。

#### 2.1 kokkoro.common_interface
TODO
#### 2.2 kokkoro.platform_patch
TODO
