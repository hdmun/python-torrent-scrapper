import json
import os
from collections import namedtuple

import ftpclient
import scrapper


def json_obj_to_namedtuple(d):
    return namedtuple('X', d.keys())(*d.values())


def json_to_namedtuple(filename: str):
    with open(filename, 'rb') as f:
        return json.load(f, encoding='utf-8', object_hook=json_obj_to_namedtuple)


def main():
    settings = json_to_namedtuple('.settings.json')

    download_dir = settings.download_path
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    with ftpclient.openftp(settings.ftp_server) as ftp:
        for keyword in settings.search_keywords:
            torrentwal = scrapper.Torrentwal(ftp, settings.telegram, download_dir)
            torrentwal.search(keyword)


if __name__ == "__main__":
    main()
