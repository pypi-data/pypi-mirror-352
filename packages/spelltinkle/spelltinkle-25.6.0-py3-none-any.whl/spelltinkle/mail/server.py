import imaplib
import sqlite3
import stat
from typing import List, Tuple
import functools
import re

from spelltinkle.mail.email import EMail
from spelltinkle.mail.test import TestIMAP4


@functools.lru_cache(maxsize=5)
def create_mail_server(name, config):
    return MailServer(name, config)


class MailServer:
    def __init__(self, name: str, conf):
        self.config = conf.mail[name]
        self.dir = conf.home / 'mail' / name
        self._server: TestIMAP4 | imaplib.IMAP4_SSL | None = None
        self._db: sqlite3.Connection | None = None

    @property
    def db(self):
        if self._db:
            return self._db
        dbfile = self.dir / 'db.sqlite3'
        exists = dbfile.is_file()
        self._db = sqlite3.connect(
            # f'file:{dbfile}?nolock=1',
            str(dbfile),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        if not exists:
            with self._db as db:
                db.execute(
                    'CREATE TABLE mails ('
                    'uid INTEGER PRIMARY KEY,'
                    'folder TEXT,'
                    'time timestamp,'
                    'subject TEXT,'
                    'sender TEXT,'
                    'receivers TEXT,'
                    'parts TEXT);')
            with self._db as db:
                db.execute('CREATE INDEX mails_index ON mails(folder);')
            with self._db as db:
                db.execute(
                    'CREATE TABLE folders ('
                    'name TEXT PRIMARY KEY,'
                    'folder TEXT);')
        return self._db

    def read_password(self):
        pw = self.dir / 'pw'
        assert pw.stat().st_mode & (stat.S_IRGRP | stat.S_IROTH) == 0
        return pw.read_text().strip()

    @property
    def server(self):
        if self._server is None:
            host = self.config['host']
            server: TestIMAP4 | imaplib.IMAP4_SSL
            if host == 'test':
                # self._server.enable('UTF8=ACCEPT')
                server = TestIMAP4()
            else:
                server = imaplib.IMAP4_SSL(host)
            server.login(self.config['user'], self.read_password())
            self._server = server
        return self._server

    def folder(self, name):
        with self.db as db:
            uids = [row[0] for row in
                    db.execute('SELECT uid FROM mails WHERE folder=?',
                               [name])]
            folders = [fname for fname in
                       db.execute('SELECT name FROM folders WHERE folder=?',
                                  [name])]
        return uids, folders

    def mails(self, uids):
        with self.db as db:
            mails = [next(db.execute('SELECT * FROM mails WHERE uid=?',
                                     [uid]))
                     for uid in uids]
        return {uid: EMail(uid,
                           date,
                           subject,
                           fro,
                           to.split(','),
                           parts.split(','))
                for uid, name, date, subject, fro, to, parts
                in mails}

    def refresh(self, old_uids, name):
        from email.parser import BytesHeaderParser
        from email.utils import parsedate_to_datetime
        import imapclient.imap_utf7 as imap_utf7  # type: ignore

        self.server.select(name, True)

        _, rply = self.server.fetch('1:*', '(UID, FLAGS)')

        unknown_uids = []
        new_uids = []
        for x in rply:
            print(x)
            _, _, _uid, _, _flags = x.split(b' ', 4)
            print(_uid, _flags)
            uid = int(_uid)
            flags = _flags[1:-2].split()
            if b'\\Deleted' not in flags:
                new_uids.append(uid)
                if uid not in old_uids:
                    unknown_uids.append(uid)

        mails = {}
        rows = []
        if unknown_uids:
            _, rply = self.server.uid(
                'FETCH',
                ','.join(str(uid) for uid in unknown_uids),
                '(BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)] BODYSTRUCTURE)')

            parser = BytesHeaderParser()
            for (_, stuff), bs, uid in zip(rply[::2],
                                           rply[1::2],
                                           unknown_uids):
                msg = parser.parsebytes(stuff)
                # print(msg)
                # print(bs)
                # print(dir(msg))
                # for part in msg.walk():
                #     print(part.get_content_type(), part)
                # asdfg
                subject = decode(msg.get('Subject', ''))
                date = parsedate_to_datetime(msg['Date'])
                date = date.astimezone().replace(tzinfo=None)  # type: ignore
                fro = decode(msg['From'])
                to = '' if msg['To'] is None else decode(msg['To'])
                parts = [':'.join(part) for part in parse_body_structure(bs)]
                rows.append((uid, name, date, subject, fro, to,
                             ','.join(parts)))
                mails[uid] = EMail(uid,
                                   date,
                                   subject,
                                   fro,
                                   to.split(','),
                                   parts)

            with self.db as db:
                db.executemany(
                    'INSERT INTO mails VALUES (?, ?, ?, ?, ?, ?, ?);',
                    rows)

        _, fldrs = self.server.list('""', '*')
        folders = []
        for f in fldrs:
            folders.append(imap_utf7.decode(f.split(b' "." ')[1]))

        return new_uids, mails, folders

    def text(self, name, uid, part_number):
        self.server.select(name)
        path = self.dir / 'text/{uid}.txt'
        if path.is_file():
            return path.read_text()

        ok, ((_, part), _) = self.server.uid('FETCH',
                                             str(uid),
                                             f'(BODY[{part_number + 1}])')
        print(part)


def decode(s):
    from email.header import decode_header
    return ''.join((b if isinstance(b, str) else b.decode())
                   if encoding is None else b.decode(encoding)
                   for b, encoding in decode_header(s))


def from2senders(frm: str) -> List[Tuple[str, str]]:
    return [parse_address(a.strip()) for a in frm.split(',')]


def parse_address(addr: str) -> Tuple[str, str]:
    name, email = addr.split('<')
    return name, email[:-1]


def parse_body_structure(bs: bytes) -> List[Tuple[str, str]]:
    """Parse BODYSTRUCTURE.

    >>> parse_body_structure(b'(("text" "plain" ...) ("text" "html" ...))')
    [('text', 'plain'), ('text', 'html')]
    """
    parts = []
    for match in re.finditer(r'\("(.*?)" "(.*?)" .*?\)', bs.decode()):
        parts.append((match[1], match[2]))
    return parts


"""
BODYSTRUCTURE = (
(
 ("text" "plain" ("charset" "UTF-8")
  NIL NIL "quoted-printable" 52 1 NIL NIL NIL NIL)
 ("text" "html" ("charset" "UTF-8")
  NIL NIL "quoted-printable" 76 1 NIL NIL NIL NIL)
 "alternative"
 ("boundary" "0000000000007a784e05c15df0da")
 NIL NIL NIL)
("image" "jpeg" ("name" "IMG_20210501_190047.jpg")
 "<1792e925ff99b9a1ffe1>" NIL "base64" 6763896 NIL
 ("attachment" ("filename" "IMG_20210501_190047.jpg")) NIL NIL)

("image" "jpeg" ("name" "IMG_20210501_151414.jpg")
 "<1792e9288a780b9ad7d2>" NIL "base64" 5316126 NIL
 ("attachment" ("filename" "IMG_20210501_151414.jpg")) NIL NIL)
("image" "jpeg" ("name" "IMG_20210501_151357.jpg")
 "<1792e92a1a352d11b3b3>" NIL "base64" 6272476 NIL
 ("attachment" ("filename" "IMG_20210501_151357.jpg")) NIL NIL)
("image" "jpeg" ("name" "IMG_20210501_134918.jpg")
 "<1792e92cc30988bdc614>" NIL "base64" 5543874 NIL
 ("attachment" ("filename" "IMG_20210501_134918.jpg")) NIL NIL)
("image" "jpeg" ("name" "IMG_20210501_134933.jpg")
 "<1792e92e8909baf181a5>" NIL "base64" 6462212 NIL
 ("attachment" ("filename" "IMG_20210501_134933.jpg")) NIL NIL)
"mixed" ("boundary" "0000000000007a785105c15df0dc") NIL NIL NIL
)
)
"""
