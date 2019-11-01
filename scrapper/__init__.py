import os

import requests

_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',}


def download_torrent_magnet2torrent(magnet):
    data = {'magnet': magnet}
    return requests.post('http://magnet2torrent.com/upload/', data=data, headers=_headers)


def download_torrent_itorrents(magent_name):
    url = f'https://itorrents.org/torrent/{magent_name}.torrent'
    return requests.get(url, headers=_headers)


def file_exist(target_dir, filename):
    return os.path.isfile('\\'.join([target_dir, filename]))


from .torrentwal_com import Torrentwal
from .torrentwork_com import TorrentWork

classes = [
    Torrentwal,
    TorrentWork
]