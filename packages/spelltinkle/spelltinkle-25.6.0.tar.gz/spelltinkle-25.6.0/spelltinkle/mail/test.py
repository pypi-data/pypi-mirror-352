from typing import Tuple, List, Union

emails = {
    1: (b'Date: Wed, 21 Aug 2019 06:20:24 +0000\r\n'
        b'From: Sloof Lirpa <sloof@lirpa.dk>\r\n'
        b'To: jj@smoerhul.dk\r\n'
        b'Subject: Hello\r\n\r\n'),
    2: (b'Date: Wed, 21 Aug 2019 06:20:24 +0000\r\n'
        b'From: Sloof Lirpa <sloof@lirpa.dk>\r\n'
        b'To: jj@smoerhul.dk\r\n'
        b'Subject: Hello\r\n\r\n')}


bodystructure = (
    'OK',
    [b"""
     1
     (UID 42106 BODYSTRUCTURE
      (
       ("text" "plain" ("charset" "UTF-8") NIL NIL "quoted-printable"
        1013 27 NIL NIL NIL NIL)
       ("text" "html" ("charset" "UTF-8") NIL NIL "quoted-printable"
        1140 15 NIL NIL NIL NIL)
       "alternative" ("boundary" "00000000000011a1ee05bde8c670") NIL NIL NIL
      )
     )"""])

body1 = (
    'OK',
    [(b'1 (UID 42106 BODY[1] {1013}',
      b' Hej Martin, Johannes og Jens J=C3=B8rgen\r\nMvh\r\nTue\r\n'),
     b')'])
body2 = (
    'OK',
    [(b'1 (UID 42106 BODY[2] {1140}',
      b'<div dir=3D"ltr">=C2=A0Hej Jens J=C3=B8rgen<br></div>\r\n'),
     b')'])


class TestIMAP4:
    def login(self, user: str, pw: str):
        pass

    def select(self, name, readonly):
        pass

    def list(self, name, what):
        return ('OK',
                [b'(\\HasChildren) "." "INBOX"',
                 b'(\\HasNoChildren \\UnMarked) "." "INBOX.subfolder"'])

    def fetch(self, arg, what):
        assert arg == '1:*' and what == '(UID, FLAGS)'
        return ('OK', [b'? (UID %d FLAGS (\\Seen))' % uid
                       for uid in emails])

    def uid(self,
            cmd: str,
            which: str,
            what: str) -> Tuple[str, List[Union[bytes, Tuple[bytes, bytes]]]]:
        if cmd == 'FETCH':
            uids = [int(x) for x in which.split(',')]
            data: List[Union[bytes, Tuple[bytes, bytes]]] = []
            for id, uid in enumerate(uids, 1):
                txt = emails[uid]
                data.append((f'{id} (UID {uid} {what} {{{len(txt)}}}'.encode(),
                             txt))
                data.append(b')')
            return ('OK', data)
        assert 0


if __name__ == '__main__':
    print(TestIMAP4().uid('FETCH', '1,2',
                          'BODY[HEADER.FIELDS (SUBJECT FROM TO DATE)]'))
