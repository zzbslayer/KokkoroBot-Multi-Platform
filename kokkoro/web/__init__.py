from quart import Quart

quart_app = Quart(__name__)

def get_app():
    return quart_app

from .homepage import *
