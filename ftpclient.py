import ftplib


class openftp(object):
    def __init__(self, ftpserver):
        self._addr = ftpserver.address
        self._port = ftpserver.port
        self._id = ftpserver.id
        self._pw = ftpserver.pw
        self._upload = ftpserver.upload
        self._ftp = ftplib.FTP()

    def upload(self, path: str, filename: str):
        fullpath = '\\'.join([path, filename])
        with open(fullpath, 'rb') as f:
            self._ftp.storbinary('STOR ' + filename, f)

    def __enter__(self):
        self._ftp.connect(self._addr, self._port)
        self._ftp.encoding = 'utf-8'
        self._ftp.login(self._id, self._pw)
        self._ftp.cwd(self._upload)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._ftp:
            self._ftp.close()
