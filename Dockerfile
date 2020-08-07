FROM python:3.8-slim-buster

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
RUN pip install https://github.com/jxtech/wechatpy/archive/master.zip
# RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# font for matplotlib
# COPY ["fonts/Microsoft YaHei.ttf", "/usr/share/fonts/Microsoft YaHei.ttf"]