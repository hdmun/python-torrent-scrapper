import copy
import os

import bs4
import requests

_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',}


def download_torrent_magnet2torrent(magnet):
    data = {'magnet': magnet}
    return requests.post('http://magnet2torrent.com/upload/', data=data, headers=_headers)


def download_torrent_itorrents(magent_name):
    url = f'https://itorrents.org/torrent/{magent_name}.torrent'
    return requests.get(url, headers=_headers)


def download_torrent_filedue(download_page_url):
    _session = requests.Session()
    response = _session.get(download_page_url, headers=_headers)
    if response.status_code != 200:
        print('faield download_torrent_filedue')
        return response

    print(response.request.headers)

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    down_key = soup.select_one('#downloadForm > input[type=hidden]:nth-child(1)')
    remote_addr = soup.select_one('#downloadForm > input[type=hidden]:nth-child(2)')
    params = {
        'downKey': down_key.get('value'),
        'remoteAddr': remote_addr.get('value')
    }
    print(download_page_url, params)

    __headers = copy.deepcopy(_headers)
    __headers['referer'] = download_page_url
    __headers['sec-fetch-site'] = 'same-origin'
    __headers['sec-fetch-user'] = '?1'
    return _session.get(download_page_url, params=params, headers=__headers)


def file_exist(target_dir, filename):
    return os.path.isfile('\\'.join([target_dir, filename]))


from .torrentwal_com import Torrentwal
from .torrentwork_com import TorrentWork

classes = [
    Torrentwal,
    TorrentWork
]