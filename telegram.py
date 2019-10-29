import requests


def send_message(token: str, chat_id: int, msg: str):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': chat_id,
        'text': msg
    }
    requests.get(url, params=params)
    print(msg)
