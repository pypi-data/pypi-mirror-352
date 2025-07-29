from __future__ import annotations

import os
import os.path as op
import re
from typing import Iterable


def untabify(line: str) -> tuple[str, bool]:
    r"""Remove leading tabs.

    Returns new string and boolean indicating the presence of tabs.

    >>> untabify('abc')
    ('abc', False)
    >>> untabify('\tabc')
    ('        abc', True)
    """
    if '\t' not in line:
        return line, False
    line0 = line.lstrip('\t').replace('\t', ' ')
    # assert '\t' not in line0, line
    return ' ' * (8 * (len(line) - len(line0))) + line0, True


def tabify(line: str) -> str:
    r"""Convert leading spaces to tabs.

    >>> tabify('        abc')
    '\tabc'
    >>> tabify('            abc')
    '\t    abc'
    """
    nspaces = len(line) - len(line.lstrip(' '))
    ntabs = nspaces // 8
    return '\t' * ntabs + line[ntabs * 8:]


def isempty(line: str) -> bool:
    return line == ' ' * len(line)

# re.match('(.*\S)(?= *)|( +)', line).group()


def tolines(fd: Iterable[str]) -> tuple[list[str], bool]:
    r"""Normalize lines.

    >>> tolines(['Hello  \n'])
    (['Hello', ''], False)
    """
    lines = []
    line = '\n'
    has_tabs = False
    for n, line in enumerate(fd):
        line, tabs = untabify(line)
        has_tabs = has_tabs or tabs
        for a in line[:-1]:
            assert ord(a) > 31, (line, n)
        if not isempty(line[:-1]):
            line = line[:-1].rstrip() + line[-1]
        lines.append(line[:-1])
    if line[-1] == '\n':
        lines.append('')
    else:
        lines[-1] = line
    return lines, has_tabs


def findword(line, c):
    """Find word in line."""
    while line[c - 1].isalnum():
        c -= 1
    return c


def find_files(x):
    x = re.compile('.*'.join(re.escape(word) for word in x.split(',')))
    matches = []
    for root, dirs, names in os.walk('.'):
        for name in names:
            if name.endswith('.pyc'):
                continue
            path = op.join(root, name)
            if x.search(path):
                matches.append(path)
        if '.git' in dirs:
            dirs.remove('.git')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
    return matches


def convert_dict_syntax(line, c):
    """...

    >>> convert_dict_syntax('a.b = 7', 1)
    (0, 3, "a['b']")
    >>> convert_dict_syntax('a["b"] = 7', 1)
    (0, 6, 'a.b')
    >>> convert_dict_syntax('"b": 7', 3)
    (0, 5, 'b=')
    >>> convert_dict_syntax('b=7', 1)
    (0, 2, "'b': ")
    """
    regexes = {
        '.': (r'([_a-zA-Z][_a-zA-Z0-9]*)\.([_a-zA-Z][_a-zA-Z0-9]*)',
              '{}[{!r}]'),
        '[': (r'([_a-zA-Z][_a-zA-Z0-9]*)' +
              r"""\[['"]([_a-zA-Z][_a-zA-Z0-9]*)['"]\]""",
              '{}.{}'),
        ':': (r"""['"]([_a-zA-Z][_a-zA-Z0-9]*)['"]: """,
              '{}='),
        '=': (r'([_a-zA-Z][_a-zA-Z0-9]*)=',
              '{!r}: ')}

    if line[c] not in regexes:
        return c, c, ''

    regex, fmt = regexes[line[c]]

    for mo in re.finditer(regex, line):
        c1 = mo.start()
        c2 = mo.end()
        if c1 <= c < c2:
            break
    else:  # no break
        return c, c, ''  # no match

    if line[c] in '.[':
        return c1, c2, fmt.format(mo[1], mo[2])
    return c1, c2, fmt.format(mo[1])
