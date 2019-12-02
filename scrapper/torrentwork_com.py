import time

import bs4
import requests

import scrapper
import telegram


class TorrentWork(object):
    def __init__(self, ftp, telegram: dict, download_path: str):
        self._session = requests.Session()
        self._base_url = 'https://torrentwork.com'
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
        search_url = self._base_url + '/bbs/search.php'
        params = {'stx': keyword.replace(' ', '+')}
        res = self._session.get(search_url, params=params, headers=scrapper._headers)
        if res.status_code != 200:
            if res.status_code != 403:
                self._send_telegram(f'request error search page|status_code={res.status_code}|search_url={search_url}')
            return

        html_text = res.text
        soup = bs4.BeautifulSoup(html_text, 'html.parser')

        # selector = '#bg-content > div > div.col-md-9.col-md-pull-0.m-col-mb-9 > div.search-media > div > div > div.media-body > div.media-heading > a'
        # subject_list = soup.select(selector)
        subject_list = soup.find_all('div', attrs={'class': 'media-heading'})
        for div_ in subject_list:
            subject = div_.find_all('a')[0]
            subject_link = subject.get('href')
            sub_title = subject.text.replace('\r', '').replace('\n', '').replace('\t', '')
            sub_title = sub_title.replace('.mp4', '')
            sub_title = sub_title.strip()

            if '720p-NEXT' not in sub_title:
                continue

            if self._is_downloaded(sub_title):
                print('downloaded', sub_title)
                return

            self._parse_subject_page(subject_link, sub_title)

        time.sleep(5)

    def _parse_subject_page(self, subject_link: str, sub_title: str):
        _SLEEP_TIME_SEC = 10

        response = self._session.get(subject_link, headers=scrapper._headers)
        if response.status_code != 200:
            self._send_telegram(f'request error subject page|status_code={response.status_code}|url={subject_link}')
            return

        html_text = response.text
        soup = bs4.BeautifulSoup(html_text, 'html.parser')
        download_btns = soup.find_all('a', attrs={'class': 'btn btn-color btn-xs view_file_download'})
        for btn in download_btns:
            if self._is_downloaded(sub_title):
                print('downloaded', sub_title)
                return

            href = btn.get('href')
            print('href', href, self._base_url)
            if 'magnet:?xt=urn:btih:' in href:
                response = scrapper.download_torrent_magnet2torrent(href)
                if response.status_code != 200:
                    print('status_code', response.status_code, href)
                    time.sleep(_SLEEP_TIME_SEC)
                    continue
            else:
                response = scrapper.download_torrent_filedue(href)

            filename = f'{sub_title}.torrent'
            with open(f'{self._download_path}\\{filename}', 'wb') as f:
                f.write(response.content)

            time.sleep(_SLEEP_TIME_SEC)
            self._ftp.upload(self._download_path, filename)
            self._send_telegram(f'donwload torrent file|filename={filename}|url={self._base_url}')
