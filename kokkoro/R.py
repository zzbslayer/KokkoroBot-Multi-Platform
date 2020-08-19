import os
from urllib.parse import urljoin
from urllib.request import pathname2url

from PIL import Image

import kokkoro
from kokkoro import logger, util

class ResObj:
    def __init__(self, res_path):
        res_dir = os.path.expanduser(kokkoro.config.RES_DIR)
        fullpath = os.path.abspath(os.path.join(res_dir, res_path))
        if not fullpath.startswith(os.path.abspath(res_dir)):
            raise ValueError('Cannot access outside RESOUCE_DIR')
        self.__path = os.path.normpath(res_path)

    @property
    def url(self):
        """资源文件的url，供酷Q（或其他远程服务）使用"""
        return urljoin(kokkoro.config.RES_URL, pathname2url(self.__path))

    @property
    def path(self):
        """资源文件的路径，供bot内部使用"""
        return os.path.abspath(os.path.expanduser(os.path.join(kokkoro.config.RES_DIR, self.__path)))

    @property
    def exist(self):
        return os.path.exists(self.path)

class ResImg(ResObj):
    def open(self) -> Image:
        try:
            return Image.open(self.path)
        except FileNotFoundError:
            kokkoro.logger.error(f'缺少图片资源：{self.path}')
            raise

class RemoteResObj:
    def __init__(self, url):
        self.__path = url
    
    @property
    def url(self):
        return self.__path

class RemoteResImg(RemoteResObj):
    async def open(self) -> Image:
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url)
            return Image.open(BytesIO(r.content))


def get(path, *paths):
    return ResObj(os.path.join(path, *paths))

def img(path, *paths) -> ResImg:
    return ResImg(os.path.join('img', path, *paths))

def remote_img(url) -> ResImg:
    return RemoteResImg(url)