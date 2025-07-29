from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .document import Document  # noqa


def str2keys(keys):
    while keys:
        if keys[:2] == '^^':
            yield '^'
            keys = keys[2:]
        if keys[0] == '^':
            yield keys[:2]
            keys = keys[2:]
        elif keys[:2] == '<<':
            yield '<'
            keys = keys[2:]
        elif keys[0] == '<':
            key, keys = keys[1:].split('>', 1)
            yield key.replace('-', '_')
        elif keys[0] == '\n':
            keys = keys[1:]
        else:
            yield keys[0]
            keys = keys[1:]


class InputHandler:
    def insert_character(self, char: str) -> Optional['Document']:
        raise NotImplementedError

    def unknown(self, key: str) -> Optional['Document']:
        pass

    def find_chr(self, s: str, direction: int = 1) -> None:
        pass


class Input(InputHandler):
    def __init__(self, string=''):
        self.c = len(string)
        self.update(string)

    def update(self, string=None):
        if string is not None:
            self.string = string

    def insert_character(self, chr):
        s = self.string[:self.c] + chr + self.string[self.c:]
        self.c += 1
        self.update(s)

    def bs(self):
        if self.c > 0:
            s = self.string[:self.c - 1] + self.string[self.c:]
            self.c -= 1
            self.update(s)

    def delete(self):
        s = self.string[:self.c] + self.string[self.c + 1:]
        self.update(s)

    def left(self):
        self.c = max(0, self.c - 1)
        self.update()

    def right(self):
        self.c = min(len(self.string), self.c + 1)
        self.update()

    def home(self):
        self.c = 0
        self.update()

    def end(self):
        self.c = len(self.string)
        self.update()
