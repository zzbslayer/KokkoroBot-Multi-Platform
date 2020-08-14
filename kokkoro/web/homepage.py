from . import get_app

app = get_app()

@app.route('/')
async def hello():
    return "Hello!"

