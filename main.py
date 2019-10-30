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
            torrentwal = scrapper.Torrentwal(ftp, settings.telegram, download_dir)
            torrentwal.search(keyword)


def _get_traceback_str():
    '''
    from http://egloos.zum.com/mcchae/v/11018564
    '''

    lines = traceback.format_exc().strip().split('\n')
    rl = [lines[-1]]
    lines = lines[1:-1]
    lines.reverse()
    nstr = ''
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('File "'):
            eles = lines[i].strip().split('"')
            basename = os.path.basename(eles[1])
            lastdir = os.path.basename(os.path.dirname(eles[1]))
            eles[1] = '%s/%s' % (lastdir,basename)
            rl.append('^\t%s %s' % (nstr,'"'.join(eles)))
            nstr = ''
        else:
            nstr += line
    return '\n'.join(rl)


if __name__ == "__main__":
    try:
        settings = json_to_namedtuple('.settings.json')

        main(settings)
    except Exception as ex:
        token: str = settings.telegram.token
        chat_id: str = settings.telegram.chat_id
        telegram.send_message(token, chat_id, f'exception={ex}|callstack={_get_traceback_str()}')
