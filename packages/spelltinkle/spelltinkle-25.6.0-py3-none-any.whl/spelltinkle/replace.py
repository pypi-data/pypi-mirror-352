import re
import threading

from .input import Input
from .search import TRANSLATION, NHC
from .document import Document


class Replace(Input):
    def __init__(self,
                 doc: Document,
                 find: str,
                 replace: str,
                 use_regex=False):
        self.doc = doc
        self.view = doc.view
        self.replace = replace
        self.use_regex = use_regex

        Input.__init__(self)
        self.paint_thread = None
        if not use_regex:
            find = re.escape(find)
        self.match: re.Match | None = None
        self.find = re.compile(find)
        threading.Thread(target=self.paint).start()
        self.next()
        self.update()

    def update(self, string=None):
        Input.update(self, string)
        text = 'Replace?  yes, no or all!'
        self.view.message = text
        self.view.update_info_line()

    def insert_character(self, chr):
        r, c = self.view.pos

        assert self.match is not None
        n = self.match.end() - self.match.start()

        if chr == 'n':
            self.view.move(r, c + n)
            self.next()
        elif chr == 'y':
            replace = self.replace
            if self.use_regex:
                replace = self.match.expand(replace)
            self.doc.change(r, c, r, c + n, [replace])
            self.next()
        elif chr == '!':
            while True:
                replace = self.replace
                if self.use_regex:
                    replace = self.match.expand(replace)
                self.doc.change(r, c, r, c + n, [replace])
                if not self.next():
                    break
                assert self.view.moved is not None
                r, c = self.view.moved
                n = self.match.end() - self.match.start()

    def next(self):
        if self.view.moved:
            r, c = self.view.moved
        else:
            r, c = self.view.pos
        for r, c, line in self.doc.enumerate(r, c):
            self.match = self.find.search(line)
            if self.match:
                c += self.match.start()
                self.view.move(r, c)
                return True

        self.esc()
        self.clean()
        return False

    def esc(self):
        self.view.message = None
        self.doc.handler = None

    def paint(self):
        self.clean()
        for r, line in enumerate(self.doc.lines):
            for match in self.find.finditer(line):
                for c in range(match.start(), match.end()):
                    self.doc.color.colors[r][c] += NHC
        # self.session.queue.put('draw colors')

    def clean(self):
        for line in self.doc.color.colors:
            line[:] = line.translate(TRANSLATION)
