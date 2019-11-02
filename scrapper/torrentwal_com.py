import time

import bs4
import requests

import scrapper
import telegram


_SLEEP_TIME_SEC = 10


class Torrentwal(object):
    def __init__(self, ftp, telegram: dict, download_path: str):
        self._session = requests.Session()
        self._base_url = 'https://torrentwal.com/'
        self._ftp = ftp
        self._token: str = telegram.token
        self._chat_id: int = telegram.chat_id
        self._download_path = download_path

    def _send_telegram(self, msg: str):
        if self._token and self._chat_id:
            telegram.send_message(self._token, self._chat_id, msg)

    def _is_downloaded(self, sub_title):
        return scrapper.file_exist(self._download_path, f'{sub_title}.torrent')

    def search(self, keyword: str):
        search_url = self._base_url + 'bbs/s.php'
        params = {'k': keyword.replace(' ', '+')}
        res = self._session.get(search_url, params=params, headers=scrapper._headers)
        if res.status_code != 200:
            self._send_telegram(f'request error search page|status_code={res.status_code}')
            return

        self._parse_search_page(res.text)
        time.sleep(1)

    def _parse_search_page(self, html_text):
        soup = bs4.BeautifulSoup(html_text, 'html.parser')
        sub_list = soup.find_all('a', attrs={'target': 's'})
        for i, subject in enumerate(sub_list, 0):
            time.sleep(_SLEEP_TIME_SEC)

            sub_title = subject.text.replace('\r', '').replace('\n', '').replace('\t', '')
            sub_title = sub_title.replace('.mp4', '')
            sub_title = sub_title.strip()

            if '720p-NEXT' not in sub_title:
                continue

            if self._is_downloaded(sub_title):
                print('downloaded', sub_title)
                return

            sub_link = subject.get('href').replace('../', self._base_url)
            self._parse_subject_page(sub_title, sub_link)

    def _parse_subject_page(self, sub_title: str, sub_link: str):
        res = self._session.get(sub_link, headers=scrapper._headers)
        if res.status_code != 200:
            self._send_telegram(f'request error subject page|status_code={res.status_code}')
            return

        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        for search_magnetlink in soup.find_all('a'):
            if self._is_downloaded(sub_title):
                print('downloaded', sub_title)
                return

            href = search_magnetlink.get('href')
            if not href:
                continue

            if 'magnet:?' in href:
                magnet_link = href.split(':')[-1]
                res = scrapper.download_torrent_itorrents(magnet_link)

                if res.headers['content-type'] != 'application/x-bittorrent':
                    print(res.headers['content-type'])
                    continue

            elif 'javascript:_filetender' in href:
                download_page = self._base_url + href.replace("javascript:_filetender('", '').replace("')", '')
                res = scrapper.download_torrent_filetender(self._session, download_page, sub_link)
            else:
                continue

            if res.status_code != 200:
                self._send_telegram(f'download error torrent itorrents|status_code={res.status_code}|url={magnet_link}')
                time.sleep(_SLEEP_TIME_SEC)
                continue

            print(sub_title, href)

            filename = f'{sub_title}.torrent'
            with open(f'{self._download_path}\\{filename}', 'wb') as f:
                f.write(res.content)

            time.sleep(_SLEEP_TIME_SEC)
            self._ftp.upload(self._download_path, filename)
            self._send_telegram(f'donwload torrent file|filename={filename}|url={self._base_url}')
