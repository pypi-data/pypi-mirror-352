from __future__ import annotations
from typing import Tuple, Set, TYPE_CHECKING

from spelltinkle.color import highlight_codes, ERROR
if TYPE_CHECKING:
    from spelltinkle.document import Document

NHC = len(highlight_codes)

P = {'(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{'}


def adjust_mark(m, m1, m2, m3):
    """Adjust mark after changes.

    >>> adjust_mark((10, 0), (1, 0), (5, 0), (2, 0))
    (7, 0)
    >>> adjust_mark((5, 30), (3, 10), (3, 20), (3, 15))
    (5, 30)
    >>> adjust_mark((3, 30), (3, 10), (3, 20), (3, 15))
    (3, 25)
    """
    if m is None:
        return m
    if m >= m1:
        if m < m2:
            return None
        r, c = m
        r2, c2 = m2
        r3, c3 = m3
        if r == r2:
            return (r3, c3 + c - c2)
        return (r3 + r - r2, c)
    return m


class View:
    def __init__(self, doc: Document, show_line_numbers=True):
        self.doc = doc
        self.show_line_numbers = show_line_numbers

        self.y1 = 0
        self.x = 0
        self.y = 0
        self.c = 0
        self.r = 0
        self.c0: int | None = None

        self.ys1 = 0
        self.ys2 = 0

        self.mark: tuple[int, int] | None = None
        self.bookmark: int | None = None

        self.message: str | None = None

        self.moved: tuple[int, int] | None = None
        self.scrolled = True

        self.lines: list[tuple[int, int, int]] = []
        self.wn = 0
        self.cursors: Set[Tuple[int, int]] = set()

    def updated(self, m1, m2, m3):
        if self.bookmark is not None:
            self.bookmark = adjust_mark((self.bookmark, 0), m1, m2, m3)[0]
        self.mark = adjust_mark(self.mark, m1, m2, m3)

    def set_screen(self, scr):
        self.tabs = scr.subwin(1, scr.w, 0, 0)
        self.text = scr.subwin(scr.h - 2, scr.w, 1, 0)
        self.info = scr.subwin(1, scr.w, scr.h - 1, 0)

    @property
    def pos(self) -> tuple[int, int]:
        return self.r, self.c

    @pos.setter
    def pos(self, p):
        self.r, self.c = p

    def prev(self):
        if self.c == 0:
            if self.r > 0:
                return (self.r - 1, len(self.doc.lines[self.r - 1]))
            return (0, 0)
        return (self.r, self.c - 1)

    def next(self):
        if self.c == len(self.doc.lines[self.r]):
            if self.r == len(self.doc.lines) - 1:
                return self.pos
            return (self.r + 1, 0)
        return (self.r, self.c + 1)

    def move(self,
             r: int = -1,
             c: int = 0,
             later: bool = True) -> None | tuple[int, int]:
        if later:
            self.moved = (r, c)
            return None

        if c == -1:
            if self.c0 is None:
                self.c0 = self.c
            c = self.c0
        else:
            self.c0 = None

        if r == -1:
            r = self.r
        L = len(self.doc.lines)
        if r >= L:
            r = L - 1
            c = len(self.doc.lines[r])
        c = min(c, len(self.doc.lines[r]))

        self.c = c
        self.r = r

        w = self.text.w - self.wn - 1
        self.y = 0
        for row, c1, c2 in self.lines:
            if row == r and c1 <= c <= c2:
                self.x = c - c1
                if self.x == w:
                    self.y += 1
                    self.x = 0
                break
            self.y += 1

        h = self.text.h
        if self.y < self.y1:
            self.y1 = self.y
            self.scrolled = True
        elif self.y >= self.y1 + h:
            self.y1 = self.y + 1 - h
            self.scrolled = True

        Y = len(self.lines)
        s1 = self.y1 / Y
        s2 = min(h, Y) / Y
        self.ys1 = int(s1 * min(h, Y))
        self.ys2 = self.ys1 + max(1, int(round(s2 * min(h, Y))))

        self.moved = None

        return self.pos

    def marked_region(self):
        if self.mark is None:
            return 0, 0, -1, 0
        if self.mark < self.pos:
            return self.mark + self.pos
        else:
            return self.pos + self.mark

    def mouse(self, x, y):
        if x <= self.wn:
            r = int(len(self.lines) * y / self.text.h)
            c = 0
        else:
            r, c1, c2 = self.lines[min(self.y1 + y - 1, len(self.lines) - 1)]
            c = min(c1 + max(0, x - self.wn - 1), c2)
        self.move(r, c, later=False)
        self.moved = (r, c)
        return r, c

    def build(self):
        self.wn = self.doc.gutterwidth - 1
        w = self.text.w - self.wn - 1
        self.lines = self.doc.build(w)

    def update(self, session):
        if self.doc.changes or self.lines is None:
            self.build()
        elif not self.moved and self.message is None:
            return

        if self.moved:
            self.move(*self.moved, later=False)
            highlight = self.match_parenthesis()
        else:
            highlight = []

        highlight += list(self.cursors)

        self.update_info_line()
        self.update_tabs(session)

        ra, ca, rb, cb = self.marked_region()

        text = self.text

        y2 = self.y1 + self.text.h
        w = text.w - self.wn - 1

        a1, a2, b1, b2, bb, choises = self.doc.completion.lines(
            w, self.text.h, self.x, self.y - self.y1)

        colors: bytearray | list[int]
        i = 0
        for r, c1, c2 in self.lines[self.y1:y2]:
            text.move(i, 0)
            cn = 4 * NHC + 5
            if self.ys1 <= i < self.ys2:
                cn += 1
            if c1 == 0:
                text.write(self.doc.gutter(r), cn)
            else:
                text.write(' ' * (self.wn + 1), cn)

            line = self.doc.lines[r][c1:c2]
            try:
                colors = self.doc.color.colors[r][c1:c2]
            except IndexError:
                colors = bytearray(len(line))
            m = w - len(line)

            line += ' ' * m
            colors = colors + bytearray(m)

            if r == self.r:
                colors = [c + NHC for c in colors]
            # elif c1 <= self.c < c2:
            #     colors[self.c - c1] += NHC

            for rh, ch in highlight:
                if rh == r and c1 <= ch < c2:
                    colors[ch - c1] = colors[ch - c1] % NHC + 2 * NHC

            if ra <= r <= rb:
                if r > ra:
                    ca = c1
                if r == rb:
                    cc = cb
                else:
                    cc = c2
                for c in range(max(ca, c1), min(cc, c2)):
                    colors[c - c1] = colors[c - c1] % NHC + 3 * NHC

            if i + self.y1 == len(self.lines) - 1:
                colors[c2 - c1:] = [4 * NHC + 7] * (w - c2 + c1)

            if b1 <= i < b2:
                line = line[:a1] + choises[i - b1] + line[a2:]
                if i - b1 == bb:
                    color = 4 * NHC + 6
                else:
                    color = 4 * NHC + 5
                colors[a1:a2] = [color] * (a2 - a1)

            text.write(line, colors)
            i += 1

        while i < self.text.h:
            text.move(i, 0)
            if b1 <= i < b2:
                text.write(' ' * (self.wn + 1 + a1), 4 * NHC + 7)
                if i - b1 == bb:
                    color = 4 * NHC + 6
                else:
                    color = 4 * NHC + 5
                text.write(choises[i - b1], color)
                text.write(' ' * (w - a2), 4 * NHC + 7)
            else:
                text.write(' ' * self.text.w, 4 * NHC + 7)
            i += 1

        text.move(self.y - self.y1, self.x + self.wn + 1)
        text.refresh()
        self.scrolled = False
        self.moved = None

    def match_parenthesis(self):
        r1, c1 = self.pos
        line = self.doc.lines[r1]
        p1 = line[c1:c1 + 1]
        p2 = P.get(p1)
        if not p2:
            if c1 > 0 and line[c1 - 1] in ')]}':
                c1 -= 1
                p1 = line[c1]
                p2 = P[p1]
            else:
                return []
        n = 0
        if p1 in '([{':
            for r2, c2, line in self.doc.enumerate(r1, c1 + 1):
                for c2, p in enumerate(line, c2):
                    if p == p1:
                        n += 1
                    elif p == p2:
                        if n == 0:
                            return [(r1, c1), (r2, c2)]
                        n -= 1
        else:
            for r2, c2, line in self.doc.enumerate(r1, c1, -1):
                c2 = len(line) - 1
                for p in line[::-1]:
                    if p == p1:
                        n += 1
                    elif p == p2:
                        if n == 0:
                            return [(r2, c2), (r1, c1)]
                        n -= 1
                    c2 -= 1

        return []

    def update_info_line(self):
        line = self.message
        colors: int | list[int]
        color = 4 * NHC + 3
        if line is None:
            r, c = self.doc.view.pos
            if self.doc.color.probe(r, c) == ERROR:
                for pos, error in self.doc.color.report:
                    if pos == (r, c):
                        line = error
                        break
                else:
                    line = '???'
                colors = color + 1
            else:
                if self.doc.modified:
                    status = '[modified]'
                else:
                    status = ''
                if self.cursors:
                    status += f' *{len(self.cursors)}'
                if self.doc.tabs:
                    status += f' TAB={self.doc.tabs}'
                name = self.doc.path or '[no name]'
                line = (f'line:{r + 1:{self.wn}} col:{c + 1:2} ' +
                        f'{name} {status} [{self.doc.mode}]')
                nwarn = len(self.doc.color.report)
                if nwarn:
                    line += f' [{nwarn}]'
                colors = [color] * self.info.w
        elif not isinstance(line, str):
            line, n = line
            colors = [color] * self.info.w
            colors[n] = color + 1
        else:
            colors = color

        line += ' ' * (self.info.w - len(line))
        self.info.move(0, 0)
        self.info.write(line, colors)
        self.info.refresh()

    def update_tabs(self, session):
        line = ' ' * (self.wn + 1)
        c = NHC * 4
        colors = [c + 2] * (self.wn + 1)
        self.tabcolumns = [self.wn]
        for doc in session.docs[::-1]:
            line += ' ' + doc.name + ' '
            colors.extend([c + doc.modified] * (len(doc.name) + 2))
            c = NHC * 4 + 2
            self.tabcolumns.append(len(line))

        line += ' ' * (self.tabs.w - len(line))
        colors += [c] * (self.tabs.w - len(colors))

        self.tabs.move(0, 0)
        self.tabs.write(line, colors)
        self.tabs.refresh()
