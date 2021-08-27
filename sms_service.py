import functools
from unittest.mock import AsyncMock

import asks
from asks.errors import BadStatus

from exceptions import SmscApiError


def get_api_response(method):
    if method == 'status':
        return {
            'status': 1,
            'last_timestamp': 1629921425,
            'send_timestamp': 1629921421,
            'cost': '3.52',
            'sender_id': 'SMSC.UA',
            'status_name': 'Доставлено',
            'message': 'Сегодня будет гроза!',
            'type': 0,
            'sms_cnt': 1,
        }
    elif method == 'send':
        return {'id': 1}


def mock_conditionally(mock=True):
    def wrapper(func):
        @functools.wraps(func)
        def inner(method, *args, **kwargs):
            api_response = get_api_response(method)
            async_mock = AsyncMock(return_value=api_response)
            return async_mock()
        return inner if mock else func
    return wrapper


@mock_conditionally(mock=True)
async def request_smsc(method, login, password, payload):
    if method not in {'send', 'status'}:
        raise SmscApiError(f'Unknown method: {method}')
    url = f'https://smsc.ua/sys/{method}.php'
    params = {
        'login': login, 'psw': password,
        'charset': 'utf-8', 'fmt': 3,
        **payload,
    }
    try:
        response = await asks.post(url, data=params)
        response.raise_for_status()
        decoded_response = response.json()
        if 'error' in decoded_response:
            raise SmscApiError(decoded_response['error'])
    except BadStatus:
        raise SmscApiError('Something gone wrong.')
    return decoded_response


async def send_sms(login, password, message, phones):
    payload = {
        'phones': phones,
        'mes': message,
    }
    response = await request_smsc('send', login, password, payload)
    return response


async def check_status(login, password, phone):
    payload = {
        'phone': phone,
        'id': 1,
    }
    response = await request_smsc('status', login, password, payload)
    return response
