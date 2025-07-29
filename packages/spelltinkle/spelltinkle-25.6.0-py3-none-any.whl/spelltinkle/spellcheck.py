import argparse
import re
import sys
from pathlib import Path
from typing import Generator

import enchant  # type: ignore

from spelltinkle.document import Document
from spelltinkle.i18n import guess_language


def check(word: str, dictionary) -> Generator[str, None, None] | None:
    if dictionary.check(word):
        return None
    return dictionary.suggest(word)


def find_words(text, kind: str) -> Generator[tuple[int, int, str], None, None]:
    """Find words in tetx."""
    parts = []
    if kind == 'py':
        # Python code
        for m in re.finditer(r'  # ', text):
            i = m.end()
            parts.append((i, text[i:].split('\n', 1)[0]))
        for m in re.finditer(r'""".*?"""', text, re.DOTALL):
            i, j = m.span()
            parts.append((i + 3, text[i + 3:j - 3]))
    else:
        parts.append((0, text))

    words = []
    for i, part in parts:
        for m in re.finditer(r'\w+', part):
            words.append((i + m.start(), m[0]))
    words.sort()
    w = 0
    i1 = 0
    for y, line in enumerate(text.splitlines()):
        i2 = i1 + len(line) + 1
        while w < len(words):
            i, word = words[w]
            if i1 <= i < i2:
                yield y, i - i1, word
                w += 1
            else:
                break
        i1 = i2


class SpellcheckDocument(Document):
    def __init__(self,
                 r1: int,
                 c1: int,
                 lines: list[str],
                 kind: str):
        Document.__init__(self)
        self.name = '[spell]'
        errors = []
        words = list(find_words('\n'.join(lines), kind))
        lang = guess_language(' '.join(word for y, x, word in words))
        d = enchant.Dict(lang)
        for y, x, word in words:
            suggestions = check(word, d)
            if suggestions is not None:
                if y == 0:
                    y += c1
                x += r1
                errors.append(f'{y + 1}:{x + 1} '
                              f'{word} -> {",".join(suggestions)}')
        self.change(0, 0, 0, 0, errors)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', default='-')
    args = parser.parse_args()
    if args.filename == '-':
        text = sys.stdin.read()
        kind = 'txt'
    else:
        text = Path(args.filename).read_text()
        kind = args.filename.rsplit('.')[-1]

    words = list(find_words(text, kind))
    lang = guess_language(' '.join(word for y, x, word in words))
    d = enchant.Dict(lang)
    for y, x, word in words:
        suggestions = check(word, d)
        if suggestions is not None:
            print(y + 1, x + 1, word, ','.join(suggestions))


if __name__ == '__main__':
    main()
