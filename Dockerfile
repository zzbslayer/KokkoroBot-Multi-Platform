FROM python:3.8-slim-buster AS develop

RUN mkdir -p /bot
WORKDIR /bot

# aliyun source
# RUN sed -i 's#http://deb.debian.org#https://mirrors.aliyun.com#g' /etc/apt/sources.list

# time zone
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' >/etc/timezone

# python dependencies
WORKDIR /bot
COPY requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt
# RUN pip install https://github.com/jxtech/wechatpy/archive/master.zip
# RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

FROM develop AS release

COPY kokkoro /bot/kokkoro
COPY run.py /bot
COPY run_web.py /bot
