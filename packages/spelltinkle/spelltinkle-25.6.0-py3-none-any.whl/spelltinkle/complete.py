import re
from threading import Thread
from typing import List, Optional, Tuple


def complete(word: str, words: List[str]) -> str:
    """Complete as much as possible from list of words.

    >>> complete('abc', ['abcd', 'abcdef'])
    'abcd'
    """
    if not words:
        return word
    if len(words) == 1:
        return words[0]
    n = len(word)
    if len(words[0]) == n:
        return word
    x = words[0][n]
    for w in words[1:]:
        if len(w) == n or w[n] != x:
            return word
    return complete(word + x, words)


def complete_word(doc):
    # Find the word we are looking for:
    r, c = doc.view.pos
    line = doc.lines[r]
    match = re.search(r'[a-zA-Z]\w*$', line[:c])
    if not match:
        return
    word = line[match.start():match.end()]

    # Look for possible completions in document:
    n = len(word)
    regex = re.compile(r'\b' + word + r'\w*')
    words = set()
    for R, line in enumerate(doc.lines):
        for match in regex.finditer(line):
            assert match is not None  # bug in typeshed?
            c1, c2 = match.span()
            if R != r or c1 != c - n:
                words.add(line[c1:c2])
    newword = complete(word, list(words))
    if newword != word:
        doc.change(r, c, r, c, [newword[n:]])


class Completion:
    def __init__(self):
        self.thread: Thread | None = None
        self._stop = True
        self.completions = []
        self.text_lines: List[str] = []
        self.active = False
        self.restart: Optional[Tuple[int, int]] = None
        self.line_number = 0

    def run(self, doc, r: int, c: int, loop) -> None:
        if doc.path is None or not doc.path.name.endswith('.py'):
            return

        self._stop = False
        if self.thread and self.thread.is_alive():
            self.restart = (r, c)
        else:
            self.thread = Thread(target=self.jedi, args=[doc, r, c, loop])
            self.thread.start()

    def stop(self) -> None:
        self.completions = []
        self._stop = True

    def jedi(self, doc, r, c, loop):
        from jedi import settings, Script  # type: ignore

        if settings.case_insensitive_completion:
            settings.case_insensitive_completion = False
            settings.add_bracket_after_function = True

        while True:
            try:
                s = Script('\n'.join(doc.lines))
                self.completions = s.complete(r + 1, c + 1)
            except Exception:
                return
            if self._stop:
                return
            if self.restart:
                (r, c), self.restart = self.restart, None
            else:
                break

        if self.completions:
            names = []
            types = []
            for comp in self.completions:
                try:
                    names.append(comp.name_with_symbols)
                    types.append(comp.type)
                except Exception:
                    self.text_lines = []
                    return
            self.offset = len(comp.name_with_symbols) - len(comp.complete)
            L1 = max(len(name) for name in names)
            L2 = max(len(type) for type in types)
            self.text_lines = [f'{name:{L1}} {type:>{L2}}'
                               for name, type in zip(names, types)]
            self.active = True
            self.line_number = 0
            loop.call_soon_threadsafe(doc.session.draw_colors)

    def down(self):
        if self.line_number < len(self.text_lines) - 1:
            self.line_number += 1

    def lines(self, w, h, x, y):
        if not self.active or not self.text_lines:
            return 0, 0, 0, 0, 0, []

        a = len(self.text_lines[0])
        b = len(self.text_lines)
        if b > h - y - 1:
            # above
            y1 = max(0, y - b)
            y2 = y
        else:
            y1 = y + 1
            y2 = min(h - 1, y1 + b)
        x1 = x - self.offset
        x2 = x1 + a
        if x2 > w:
            x1 -= x2 - w
            x2 = w
        return (x1, x2, y1, y2,
                self.line_number, self.text_lines[:y2 - y1])

    def word(self):
        return self.text_lines[self.line_number].split()[0][self.offset:]
