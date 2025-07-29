import os
import os.path as op
from pathlib import Path
from typing import Union, List

from .document import Document
from .text import TextDocument


class FileInputDocument(Document):
    def __init__(self, fpath: Union[str, Path], action: str = 'open'):
        fpath = str(fpath)
        Document.__init__(self)
        self.action = action
        self.name = f'[{action}]'
        self.c = -1
        self.dir = '_not_initialized_'
        self.filename: str
        self.allfiles: List[str]
        self.fpath: str
        self.update(fpath)

    def insert_character(self, chr: str) -> None:
        c = self.c
        p = self.fpath[:c] + chr + self.fpath[c:]
        self.c += 1
        self.update(p)

    def enter(self) -> Union[TextDocument, None]:
        self.session.docs.pop()
        if self.action == 'open':
            doc = TextDocument(self.session)
            doc.read(self.fpath)
            return doc
        else:
            self.session.docs[-1].path = Path(self.fpath)
            self.session.docs[-1].write()
            return None

    def insert(self) -> None:
        if self.action == 'open':
            current = self.session.docs[-1]
            if isinstance(current, TextDocument):
                self.session.docs.pop()
                doc = TextDocument(self.session)
                doc.read(self.fpath)
                self.session.memory = doc.lines
                current.paste()

    paste = insert

    def esc(self) -> None:
        self.session.docs.pop()

    def bs(self) -> None:
        c = self.c
        if c:
            p = self.fpath[:c - 1] + self.fpath[c:]
            self.c -= 1
            self.update(p)

    def delete(self) -> None:
        c = self.c
        p = self.fpath[:c] + self.fpath[c + 1:]
        self.update(p)

    def tab(self) -> None:
        names = self.lines[:-1]
        if not names:
            return

        i0 = i = len(self.filename)
        while True:
            name0 = names[0][:i + 1]
            if len(name0) == i:
                break
            for f in names[1:]:
                if not f.startswith(name0):
                    break
            else:
                i += 1
                continue
            break

        self.c += i - i0
        self.filename = name0[:i]
        self.fpath += name0[i0:i]
        self.view.message = self.fpath + ' '  # , self.c
        self.update(self.fpath)

    def update(self, fpath: str) -> None:
        self.fpath = fpath

        if self.c == -1:
            self.c = len(fpath)

        self.view.message = fpath + ' '  # , self.c

        if fpath == '..':
            dir = '..'
            self.filename = ''
        else:
            dir, self.filename = op.split(fpath)

        if dir != self.dir:
            self.allfiles = [name for name in
                             os.listdir(op.expanduser(dir) or '.')[:1000]
                             if not name.endswith('__pycache__') and
                             not name.endswith('.pyc')]
            self.dir = dir

        names = []
        for f in self.allfiles:
            if f.startswith(self.filename):
                if op.isdir(op.join(dir, f)):
                    f += '/'
                names.append(f)

        self.change(0, 0, len(self.lines) - 1, 0, names + [''])
        self.view.move(0, 0)
