import random
from quart import Quart

quart_app = Quart(__name__)

# generate random secret_key
if(quart_app.secret_key is None):
    quart_app.secret_key = bytes(
        (random.randint(0, 255) for _ in range(16)))

def get_app():
    return quart_app

from .route_elucidator import *
