import json
import os
import traceback
from collections import namedtuple

import ftpclient
import scrapper
import telegram


def json_obj_to_namedtuple(d):
    return namedtuple('X', d.keys())(*d.values())


def json_to_namedtuple(filename: str):
    with open(filename, 'rb') as f:
        return json.load(f, encoding='utf-8', object_hook=json_obj_to_namedtuple)


def main(settings):
    download_dir = settings.download_path
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    with ftpclient.openftp(settings.ftp_server) as ftp:
        for keyword in settings.search_keywords:
            for class_ in scrapper.classes:
                site_scrapper = class_(ftp, settings.telegram, download_dir)
                try:
                    site_scrapper.search(keyword)
                except Exception as ex:
                    token: str = settings.telegram.token
                    chat_id: str = settings.telegram.chat_id
                    telegram.send_message(token, chat_id, f'exception={traceback.format_exc()}')


if __name__ == "__main__":
    try:
        settings = json_to_namedtuple('.settings.json')

        main(settings)
    except Exception as ex:
        token: str = settings.telegram.token
        chat_id: str = settings.telegram.chat_id
        telegram.send_message(token, chat_id, f'exception={traceback.format_exc()}')
