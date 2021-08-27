from dotenv import dotenv_values
from quart import Quart, request, websocket

from exceptions import SmscApiError
from sms_service import send_sms

app = Quart(__name__)
app.static_folder = 'templates'
app.config.update(dotenv_values())


@app.route('/')
async def index():
    return await app.send_static_file('index.html')


@app.route('/send/', methods=['POST'])
async def send():
    form = await request.form
    message = form['message']
    try:
        result = await send_sms(
            app.config['SMSC_LOGIN'],
            app.config['SMSC_PASSWORD'],
            message,
            app.config['SMSC_OWN_NUMBER'],
        )
        return result
    except SmscApiError:
        return {}


@app.websocket('/ws')
async def ws():
    while True:
        data = await websocket.receive()
        await websocket.send(f'echo {data}')


if __name__ == '__main__':
    app.run(port=5000)
