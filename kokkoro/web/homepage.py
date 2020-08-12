import kokkoro
app = kokkoro.get_app()

@app.route('/')
async def hello():
    return "Hello!"

