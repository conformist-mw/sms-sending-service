import asyncio
import aiofiles
from quart_trio import QuartTrio
from quart import Quart, render_template, websocket, Response
from functools import partial, wraps


app = QuartTrio(__name__)
app.static_folder = 'templates'


@app.route('/')
async def index():
    return await app.send_static_file("index.html")
    # return 'pidor'

@app.websocket('/ws')
async def ws():
    while True:
        data = await websocket.receive()
        await websocket.send(f"echo {data}")


if __name__ == '__main__':
    app.run(port=5000)
